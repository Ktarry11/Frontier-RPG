#!/usr/bin/env python3
"""Silverpine Stage 5 quests (2026-10-23): Widow's Lair, Ambermill Tower, Shadowfang Keep, Fenris Isle and Shadowpine Altar.  Idempotent.

    python3 tools/build_silverpine_dungeon_quests.py && python3 tools/retier_quest_rewards.py
    (then `git checkout` every OTHER quest file and restore the intended ones from /tmp copies)

Writes data/quests/silverpine_dungeons.json (Widow's Lair 7, Ambermill Tower 10, Shadowfang Keep 12) and data/quests/fenris_isle.json
(Fenris Isle + the Altar, 30).  Removes the 8 one-line fenris_* quests from forsaken_lands.json.  Kill / fetch / boss / explore / deliver
ONLY - no escorts.  Dungeon quests are handed out by the NPCs outside the door (Corvane, Pell, Orsolo, Haskell, Marl, Rynn).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import kill, fetch                                   # noqa: E402
from tools import build_silverpine_quests as BQ                                      # noqa: E402
from tools import tirisfal_gear                                                      # noqa: E402
from tools.build_silverpine_quests import Q, explore, boss, deliver, carry           # noqa: E402

BQ.XP.update({21: 1400, 22: 1480, 23: 1560, 24: 1640, 25: 1720})
BQ.GOLD.update({21: 6000, 22: 6300, 23: 6600, 24: 6900, 25: 7200})

OUT_D = ROOT / "data/quests/silverpine_dungeons.json"
OUT_F = ROOT / "data/quests/fenris_isle.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
SPN, SPS, FEN = "silverpine_north", "silverpine_south", "fenris_isle"
WL, AT, SK, SA = "widows_lair", "ambermill_tower", "shadowfang_keep", "shadowpine_altar"

tirisfal_gear.THEMES.update({
    "spn_hive": (["Hive-Cut", "Broodmother's", "Silk-Spun", "Larder-Cured", "Comb-Hardened", "Velaxis'"],
                 ["Spun by something with a great many opinions.", "Cut from a husk and sewn with its own silk.", "Sticky at the seams."]),
    "sps_tower": (["Ambermill", "Waygate-Scribed", "Hawren's", "Archivist's", "Orrery-Lit", "Atiesh's"],
                  ["Footnoted in three languages.", "Violet at the seam, ink at the cuff.", "Dalaran-stitched and slightly haunted."]),
    "sps_keep": (["Shadowfang", "Keep-Hall", "Silverlaine's", "Kennel-Warden's", "Moon-Marked", "Arugal's"],
                 ["Worn in the keep, and not removed since.", "Torn at the sleeve by something large.", "Smells of wet fur and old candles."]),
    "fen_shore": (["Cursed-Shore", "Strand-Worn", "Tidewrack", "Isle-Hardened", "Gravemoss'", "Salt-Cursed"],
                  ["Salt in every seam.", "The tide left it, and the curse kept it.", "Dried on a driftwood fire."]),
    "fen_docks": (["Drowned-Docks", "Harpooner's", "Brine-Stiff", "Captain's", "Lakewater", "Corwell's"],
                  ["Stiff with lake salt.", "Hauled out of a wreck and dried by hand.", "Smells like a drowned ship."]),
    "fen_grave": (["Cur's-Grave", "Packmaster's", "Bone-Strewn", "Selke's", "Kennel-Cured", "Alpha's"],
                  ["Chewed at the hem.", "Patchwork of ten different pelts.", "Hide-tough and bone-stitched."]),
    "fen_manor": (["Ashbury's", "Fenris Proper", "Gate-Watch", "Moth-Eaten", "Manor-Born", "Merrin's"],
                  ["Moth-eaten but dignified.", "Cut for a house that no longer stands.", "Stitched in better days."]),
    "fen_altar": (["Shadowpine", "Ritual-Scribed", "Moon-Bound", "Orlan's", "Bone-Circle", "Fenris'"],
                  ["Cut under a borrowed moon.", "Marked with something that looks back.", "Warm, faintly, where it touches skin."]),
})


def dungeons():
    Z = []
    A = Z.append
    # ============================================================================================ WIDOW'S LAIR (Corvane, Pell)
    COR, PELL = "sp_sd_webhunter", "sp_rg_apothecary"
    A(Q("spn_wl_brood", "Cleaning the Comb", COR, SPN, 17, 17, "spn_hive",
        "Corvane has seen the inside of the Widow's Lair's mouth and counted what lives there: hatchlings in the thousands and silk-bound "
        "weavers tending them. He wants the first rooms thinned before anyone tries the deeper ones.",
        [kill("Lair Hatchling", 6, zone=WL), kill("Silkbound Weaver", 4, zone=WL)],
        "Inside the Lair, around the Web Heart. Hatchlings first. The weavers sit above them and spit.",
        "Fewer legs. That's the best thing I can say about the Lair right now. Take this.", "spn_wl_silka",
        requires_quests=["spn_sd_lair"]))
    A(Q("spn_wl_silka", "The Broodmother", COR, SPN, 17, 17, "spn_hive",
        "The hive buds off a single queen: Broodmother Silka, in the west lair of the Web Heart. Everything Longleg ever was came from her "
        "eggs. Corvane wants that line ended.",
        [boss("Broodmother Silka", WL)],
        "West of the Web Heart. Follow the egg sacs. She is what they're all running from.",
        "No more eggs. For the first time since the plague, the woods will have fewer legs than last year. Thank you.", None,
        requires_quests=["spn_wl_brood"]))
    A(Q("spn_wl_skitter", "The Weaver in the East", COR, SPN, 18, 18, "spn_hive",
        "A second queen-brood sits in the east lair under a weaver named Skitter, who hangs her victims from the ceiling for later. "
        "Corvane has watched it from the mouth and wants to stop watching.",
        [boss("Weaver Skitter", WL)],
        "East of the Web Heart. Look up before you step in.",
        "Hung up like laundry. The whole east lair. Well. Not any more.", None,
        requires_quests=["spn_wl_brood"]))
    A(Q("spn_wl_venom", "Venom for Pell", PELL, SPN, 18, 18, "spn_hive",
        "Apothecary Pell's venom theory has a new requirement: stalker venom, which is stronger than Silverpine Spider glands by a "
        "good half. Bring five sacs from the Lair's Venom Stalkers, and please don't open them to look.",
        [fetch("sp_wl_venomsac", 5)],
        "Venom Stalkers inside the Lair. Cut the sac at the base. Seal it. Run.",
        "Oh, that is beautiful. Thick as syrup, green as a corpse. The Dark Lady's Apothecaries will want to hear about this.", None,
        requires_quests=["spn_wl_brood"]))
    A(Q("spn_wl_larder", "Count the Larder", COR, SPN, 18, 18, "spn_hive",
        "Corvane wants to know how many people the hive has eaten. The answer is in two places, deep in the Lair: the Larder, where "
        "they hang the fresh ones, and the Husk Pit, where they drop what's left.",
        [explore(WL, 19, 47, 5), explore(WL, 111, 47, 5)],
        "Far west and far east of the Web Heart. Stand in each long enough to count.",
        "Forty-one, and I stopped counting. Thank you. I'll send a letter to a few families who'll hate me for it.", None,
        requires_quests=["spn_wl_brood"]))
    A(Q("spn_wl_journal", "A Hunter's Last Page", "item:sp_wl_journal", SPN, 17, 19, "spn_hive",
        "A silk-wrapped journal page, pulled from a Brood Warden's carapace. It's a hunter's hand: the last entry begins 'I have counted the "
        "exits, and there are only two.' Apothecary Pell was keeping a list of the missing.",
        [deliver("sp_wl_journal", "Bring the journal page to Apothecary Pell at the Rear Guard")],
        "Pell, at the Rear Guard, with the cauldron. He keeps the list.",
        "Marek Dunn. I had him as 'lost to wolves'. A spider is worse, and better. I'll correct the list.", None,
        turn_in_npc_id=PELL))
    A(Q("spn_wl_velaxis", "The Matriarch of the Spire", COR, SPN, 19, 19, "spn_hive",
        "Above the Web Heart is the Matriarch's Spire, where Velaxis nests: older than Silka, larger than Skitter, and not fond of company. "
        "Corvane wants the hive's head cut off, and will not pretend it's anything but a death sentence for whoever tries.",
        [boss("Matriarch Velaxis", WL)],
        "Up the north neck from the Web Heart. The Spire is lit by her eyes.",
        "Eight eyes, all closed. I'll rest easy tonight, and so will the woods. You've earned every copper.", None,
        mult=1.5, requires_quests=["spn_wl_silka", "spn_wl_skitter"]))

    # ============================================================================================ AMBERMILL TOWER (Orsolo, Haskell)
    ORS, HSK = "sp_amber_magister", "sp_amber_millwright"
    A(Q("sps_at_vestibule", "Through the Waygate", ORS, SPS, 21, 21, "sps_tower",
        "With Quillfire silent, Orsolo dares to wonder what the waygate was keeping. The tower's lowest rooms are a vestibule and a reading "
        "hall. He wants someone to stand in both and say whether the lamps are still lit.",
        [explore(AT, 75, 127, 4), explore(AT, 75, 109, 5)],
        "Step into the waygate. The vestibule is first. The reading hall is up the stair.",
        "Still lit. Violet. So it's listening. Thank you, truly.", None,
        requires_quests=["sps_quillfire"]))
    A(Q("sps_at_mages", "Lectern Guard", ORS, SPS, 21, 22, "sps_tower",
        "The reading hall is staffed by the dead: Kirin Tor and Forsaken mages who kept studying after they stopped breathing, and imps "
        "bound to the lecterns. Orsolo wants the hall cleared so a scribe can walk it.",
        [kill("Kirin Tor Mage", 5, zone=AT), kill("Forsaken Mage", 5, zone=AT), kill("Arcane-Bound Imp", 3, zone=AT)],
        "The Reading Hall and the galleries above. Mages cast first. Imps hold the doors.",
        "A scribe can walk it now. Perhaps even a very brave librarian.", None,
        requires_quests=["sps_at_vestibule"]))
    A(Q("sps_at_tomes", "Pages from the Reading Hall", ORS, SPS, 22, 22, "sps_tower",
        "Tome Wraiths are the pages of a book that learned to hover. Orsolo has a theory about who wrote the book. He needs six torn pages "
        "to prove it.",
        [fetch("sps_tome_page", 6)],
        "Tome Wraiths haunt the galleries. Take the pages off them. Do not read aloud.",
        "I know this hand. I know this hand. Hawren. It was Hawren all along. Hawren, who taught me to read.", None,
        requires_quests=["sps_at_mages"]))
    A(Q("sps_at_hawren", "Magister Hawren", ORS, SPS, 22, 22, "sps_tower",
        "Magister Hawren was Orsolo's teacher, and keeps the Archivist's Gallery. He no longer remembers a pupil's name. Orsolo cannot do "
        "it himself.",
        [boss("Magister Hawren", AT)],
        "The Archivist's Gallery, west of the reading hall. He is surrounded by his own pages.",
        "He'd want to be remembered for something better. I'll try to oblige.", None,
        requires_quests=["sps_at_tomes"]))
    A(Q("sps_at_spellblades", "Saws That Cut Back", HSK, SPS, 22, 22, "sps_tower",
        "The mill's saws were enchanted to run themselves. The tower's enchanted blades are the same kind of fool: bright, quick and "
        "indifferent to who they cut. Haskell has lost two apprentices to the lesser ones.",
        [kill("Animated Spellblade", 5, zone=AT)],
        "All through the tower. They're the ones that glint. They don't tire.",
        "Quieter. I've got my last two apprentices counting sawblades and sorting nails. That's all I'll ask of them for a month.", None,
        requires_quests=["sps_at_vestibule"]))
    A(Q("sps_at_reagents", "Lab Reagents", HSK, SPS, 22, 22, "sps_tower",
        "The Alchemy Lab was Dalaran's best-stocked apothecary outside the Violet Citadel, and its alchemists never stopped brewing. "
        "Haskell wants five sealed reagent vials, before the lab's slow poison gets out of hand.",
        [fetch("sps_reagent_vial", 5)],
        "The Alchemy Lab, north-east of the lower hall. Forsaken Alchemists carry them on their belts.",
        "Sealed, thank the Light, and not yet leaking. I'll have them neutralised by dawn.", None,
        requires_quests=["sps_at_vestibule"]))
    A(Q("sps_at_ledger", "A Ledger Gone Green", "item:sps_helbrim_ledger", SPS, 22, 23, "sps_tower",
        "A flask-stained ledger pulled from an alchemist's coat. Page after page of orders for 'reagents of discretion', all initialled H.",
        [deliver("sps_helbrim_ledger", "Bring the ledger to Millwright Haskell at Ambermill")],
        "Haskell, at the mill. He'll recognise the initials.",
        "H. Helbrim. He sold the mill its lamp-oil, and I'd have said he was a decent man. Not any more.", None,
        turn_in_npc_id=HSK))
    A(Q("sps_at_helbrim", "Apothecary Helbrim", HSK, SPS, 23, 23, "sps_tower",
        "Apothecary Helbrim runs the lab, if running is the word for a man who has been brewing the same batch for decades. He calls it "
        "research. Haskell calls it murder.",
        [boss("Apothecary Helbrim", AT)],
        "The Alchemy Lab. Follow the smell. Wear something you'd be happy to burn.",
        "It's over, then. Not a clean ending, but a final one. Thank you.", None,
        requires_quests=["sps_at_reagents"]))
    A(Q("sps_at_atiesh", "The Archmage at the Top", ORS, SPS, 23, 23, "sps_tower",
        "The tower's last occupant is Archmage Atiesh, who keeps the Observatory where the waygate was aimed. Orsolo wants to know what he "
        "was aiming at, and hopes the answer dies with him.",
        [boss("Archmage Atiesh", AT)],
        "The very top, in the Observatory. The stair is long. Don't stop on the landings.",
        "He aimed it at the stars. Just the stars. And then the stars aimed back. Thank you.", None,
        mult=1.5, requires_quests=["sps_at_hawren", "sps_at_helbrim"]))
    A(Q("sps_at_orrery", "The Last Lamp in the Orrery", ORS, SPS, 23, 23, "sps_tower",
        "The Orrery is the Observatory's twin: a round room full of little worlds, all still turning. Orsolo wants someone to stand in both "
        "and put out the lamps by being there.",
        [explore(AT, 75, 16, 5), explore(AT, 126, 15, 5)],
        "Observatory first, then the Orrery to the east. Stand a minute each.",
        "Dark. Both of them. The waygate sleeps. I'll lock it and keep the key somewhere stupid.", None,
        turn_in_npc_id=ORS, requires_quests=["sps_at_atiesh"]))

    # ============================================================================================ SHADOWFANG KEEP (Marl, Rynn)
    MAR, RYN = "sp_sfk_gatekeeper", "sp_peril_packbreaker"
    A(Q("sps_sfk_bailey", "Inside the Portcullis", MAR, SPS, 19, 20, "sps_keep",
        "Nobody comes out of Shadowfang Keep and talks about the forecourt. Marl wants someone to walk past the gatehouse, into the Outer "
        "Bailey, and say what's inside.",
        [explore(SK, 100, 170, 4), explore(SK, 100, 142, 5)],
        "Through the portcullis, the gatehouse passage, and out into the bailey. Stand by the fountain. It's dry.",
        "A dry fountain and a lot of bones. I'd imagined worse. You've got the nerve to go further.", None,
        requires_quests=["sps_sfk_forecourt"]))
    A(Q("sps_sfk_hounds", "Keep Hounds", RYN, SPS, 20, 21, "sps_keep",
        "Packbreaker Rynn knows the worgen on the hills. The ones in the keep are worse: Arugal's own hounds, kennelled and fed on things "
        "that were once people. She wants the kennels thinned before she calls them a pack.",
        [kill("Keep Worg", 6, zone=SK), kill("Slavering Worg", 5, zone=SK)],
        "The Kennels, west of the bailey. They bark at nothing. It isn't nothing.",
        "A thinner pack. Now it's a fight I can pick.", None,
        requires_quests=["sps_sfk_bailey"]))
    A(Q("sps_sfk_rethilgore", "The Kennel-Master", RYN, SPS, 21, 21, "sps_keep",
        "Rethilgore keeps the keep's hounds, and keeps them hungry. He was a decent man in Pyrewood. Rynn would like him buried "
        "before the keep makes him decent again.",
        [boss("Rethilgore", SK)],
        "The Kennels, the big pen in the west wing. He'll have a chain.",
        "He fed them first, even then. I can respect that, I suppose.", None,
        requires_quests=["sps_sfk_hounds"]))
    A(Q("sps_sfk_razorclaw", "The Butcher of the Yard", MAR, SPS, 22, 22, "sps_keep",
        "The Butcher's Yard is east of the bailey, and Razorclaw keeps it: a worgen with a cleaver where a hand ought to be. Marl has "
        "heard the chopping from the gate for years.",
        [boss("Razorclaw the Butcher", SK)],
        "East of the bailey. Follow the sound.",
        "The chopping's stopped. Thank the Light. I'll sleep, for the first time in a long while.", None,
        requires_quests=["sps_sfk_bailey"]))
    A(Q("sps_sfk_guards", "The Unrelieved", MAR, SPS, 22, 22, "sps_keep",
        "The keep's old guard never left their posts. Guardsmen wail where they stood; officers keep giving orders to no one. Marl "
        "wants them relieved, one way or another.",
        [kill("Wailing Guardsman", 6, zone=SK), kill("Tormented Officer", 4, zone=SK)],
        "The Great Hall and the passages around it. Officers first, then the men.",
        "Relieved. All of them. It's a kindness, and I'm glad it wasn't me who had to.", None,
        requires_quests=["sps_sfk_bailey"]))
    A(Q("sps_sfk_keys", "Servants' Keys", MAR, SPS, 22, 22, "sps_keep",
        "The Haunted Servitors still carry the keep's keys on their belts. Marl wants four, so the doors to the cloisters and the "
        "armoury stop being a gamble.",
        [fetch("sps_servitor_key", 4)],
        "The Great Hall and the cloisters. Servitors carry a ring each. Take the ring.",
        "The right doors, and none of them haunted. Almost enough to make a man hopeful.", None,
        requires_quests=["sps_sfk_guards"]))
    A(Q("sps_sfk_silverlaine", "Baron Silverlaine", MAR, SPS, 23, 23, "sps_keep",
        "Baron Silverlaine owned Pyrewood and Shadowfang and half the pines between. He sits on his dais in the Great Hall and receives "
        "no one. Marl would prefer the hall empty.",
        [boss("Baron Silverlaine", SK)],
        "The Great Hall, at the far end. He doesn't stand. He doesn't need to.",
        "A fitting end, I suppose. He'd have called it a very modest funeral.", None,
        requires_quests=["sps_sfk_keys"]))
    A(Q("sps_sfk_moonwalkers", "Moon-Touched", RYN, SPS, 22, 23, "sps_keep",
        "Arugal's cult is half sorcerers and half worgen who haven't yet decided. Rynn calls them moonwalkers and darksouls, and says "
        "the keep teems with them. She wants twelve of them down.",
        [kill("Shadowfang Moonwalker", 5, zone=SK), kill("Shadowfang Darksoul", 5, zone=SK)],
        "All through the keep, wherever you hear chanting. Casters first.",
        "Fewer chants. Perhaps the moon will go unremarked tonight.", None,
        requires_quests=["sps_sfk_bailey"]))
    A(Q("sps_sfk_cloister", "The Haunted Cloister", MAR, SPS, 23, 23, "sps_keep",
        "West of the Great Hall a stone cloister runs to Fenrus' crypt, and nobody has walked it in years. Marl wants it walked, "
        "start to end, by someone who'll tell him whether the crypt door is open.",
        [explore(SK, 42, 92, 4), explore(SK, 33, 53, 5)],
        "Out of the west door of the Great Hall, down the cloister, into the crypt.",
        "Open. I'd hoped. I'd feared. Both, honestly.", None,
        requires_quests=["sps_sfk_silverlaine"]))
    A(Q("sps_sfk_fenrus", "Fenrus the Devourer", MAR, SPS, 24, 24, "sps_keep",
        "Fenrus was Arugal's first experiment and his least successful. He devours things in the crypt, and nothing that goes in comes "
        "out. Marl would like to be the exception.",
        [boss("Fenrus the Devourer", SK)],
        "In the crypt, at the end of the cloister. Mind the sarcophagi. They breathe.",
        "He ate his handler, and then his handler's replacement. Thank you for being the exception.", None,
        requires_quests=["sps_sfk_cloister"]))
    A(Q("sps_sfk_sons", "Arugal's Get", RYN, SPS, 24, 24, "sps_keep",
        "The inner keep is stocked with Arugal's best: Sons of Arugal in half-turned shapes, Lupine Horrors that don't fit through "
        "doors, and Deathsworn Captains who command them. Rynn will not call them a pack.",
        [kill("Son of Arugal", 5, zone=SK), kill("Lupine Horror", 2, zone=SK), kill("Deathsworn Captain", 3, zone=SK)],
        "The crypt, the armoury and the upper landing. Don't fight them in a corridor.",
        "Not a pack. A cult, with fangs. Fewer of those is a victory.", None,
        requires_quests=["sps_sfk_silverlaine"]))
    A(Q("sps_sfk_arugal", "The Archmage's Folly", MAR, SPS, 25, 25, "sps_keep",
        "Archmage Arugal opened the door that let the worgen into Lordaeron, and now sits at the top of the keep with his tower of "
        "shadow. Marl has stood at his gate for years and would like to see the other side of it.",
        [boss("Archmage Arugal", SK)],
        "The upper landing, and then the Sanctum. Don't stop. Don't answer when he speaks.",
        "Arugal, dead. I'll lock the gate and sit for a while. Thank you. You'll never need to buy a drink at my post.", None,
        mult=1.6, requires_quests=["sps_sfk_silverlaine"]))
    return Z


def fenris():
    Z = []
    A = Z.append
    PIER, ELD, COR = "fenris_pier_warden", "bloodmoon_elder", "fenris_village_elder"
    SCOUT, ALT, HUNT = "fenris_keep_scout", "fenris_altar_warden", "fenris_grave_hunter"
    # ============================================================================================ THE PIER + THE CURSED SHORE
    A(Q("fen_walk_spine", "Walk the Spine Road", PIER, FEN, 17, 18, "fen_shore",
        "The only road on Fenris Isle runs from the pier to the manor. Pier-Warden Hask has not walked it since the crossing. He wants "
        "someone to walk it to the manor gate and tell him what's changed.",
        [explore(FEN, 80, 92, 5), explore(FEN, 80, 64, 5), explore(FEN, 80, 46, 4)],
        "Village, crossroads, manor gate. Stay on the road. The isle doesn't like strays.",
        "The road holds. I thought it wouldn't. Thank you. Take this.", None))
    A(Q("fen_shore_crawlers", "Crawlers on the Strand", PIER, FEN, 17, 18, "fen_shore",
        "The shore around the pier is crowded with tidewrack crawlers, picking at what the lake delivers, and rabid wolves that "
        "follow them. Hask wants a path he can walk without a knife.",
        [kill("Tidewrack Crawler", 6, zone=FEN), kill("Rabid Wolf", 5, zone=FEN)],
        "Anywhere along the shore. Crawlers dig. Wolves snap.",
        "A shore a man can stand on. I'll hang a lantern and see who comes.", None))
    A(Q("fen_cursed_shore", "The Cursed Shore", ELD, FEN, 17, 18, "fen_shore",
        "Elder Gravemoss guards what's left of Bloodmoon Village. The worgen stalkers have been creeping closer every night, and the "
        "cursed villagers have started to look in the windows.",
        [kill("Feral Worgen Stalker", 6, zone=FEN), kill("Cursed Villager", 5, zone=FEN)],
        "Out in the open ground around the village. Stalkers hunt in threes. Villagers hunt in silence.",
        "I can sleep, now, for a night or two. Thank you. It matters more than you'll know.", None))
    A(Q("fen_isle_banshees", "Banshees of the Strand", ELD, FEN, 18, 19, "fen_shore",
        "The drowned still sing along the strand, and the banshees singing back are the worst of it. Gravemoss wants them quiet.",
        [kill("Isle Banshee", 6, zone=FEN)],
        "The Cursed Shore, along the beaches. They sing at dusk.",
        "Quiet. I'd forgotten the quiet. It's almost worse.", "fen_banshee_locks",
        requires_quests=["fen_cursed_shore"]))
    A(Q("fen_banshee_locks", "A Lock of Hair", ELD, FEN, 19, 19, "fen_shore",
        "Every banshee leaves a lock of hair behind when she fades. Gravemoss has a theory the locks are anchors, and wants five to "
        "bury under the village stones.",
        [fetch("fen_banshee_lock", 5)],
        "From the banshees, after they fade. Gently. They remember being people.",
        "They go in the ground by the well. It's the best I can do for them.", None,
        requires_quests=["fen_isle_banshees"]))
    A(Q("fen_ancient_curse_beast", "The Ancient Curse-Beast", ELD, FEN, 21, 21, "fen_shore",
        "Something older than the curse walks the Cursed Shore: a bear the size of a barn, wrapped in its own rot. The villagers call "
        "it the Ancient Curse-Beast, and nobody who hunts it has gone twice.",
        [boss("Ancient Curse-Beast", FEN), kill("Rabid Wolf", 3, zone=FEN)],
        "It wanders the Shore. Follow the destroyed trees. The wolves won't go near it.",
        "It was already old when the curse came. I'd like to think it's resting.", None,
        requires_quests=["fen_cursed_shore"]))
    # ============================================================================================ THE DROWNED DOCKS (Corwell)
    A(Q("fen_drowned_docks", "The Drowned Docks", COR, FEN, 18, 18, "fen_docks",
        "The south-west docks are where the drowned come ashore, and the bilge rats come with them. Huntsman Corwell lost a boat there, "
        "and a nephew, and wants the docks clear.",
        [kill("Drowned Sailor", 6, zone=FEN), kill("Bilge Rat Swarm", 5, zone=FEN)],
        "The Drowned Docks, south-west of the village. Sailors on the beach, rats under the boards.",
        "A cleaner dock. I won't pretend my nephew's coming back. But the boat's safe to look at.", None))
    A(Q("fen_harpoons", "Heads of Harpoons", COR, FEN, 19, 20, "fen_docks",
        "The Drowned Harpooners carry iron heads Corwell's family forged, and every one is bent the same way. He wants five for the "
        "smithy, to be melted and made right.",
        [fetch("fen_harpoon_head", 5)],
        "From the Drowned Harpooners at the docks. Take the heads, not the poles.",
        "Bent by cold lake. I'll bring them back to something honest.", None,
        requires_quests=["fen_drowned_docks"]))
    A(Q("fen_wretches", "What the Lake Gave Back", COR, FEN, 19, 20, "fen_docks",
        "Waterlogged Wretches drag themselves up the beach at night. They were fishermen, once. Corwell would like to see them off.",
        [kill("Waterlogged Wretch", 6, zone=FEN)],
        "The beach at the Drowned Docks, and the shingle west of the jetty.",
        "I knew four of them. I'm sorry for all of them. Thank you.", None,
        requires_quests=["fen_drowned_docks"]))
    A(Q("fen_logbook_page", "A Water-Stained Page", "item:fen_logbook_page", FEN, 18, 20, "fen_docks",
        "A page from a ship's log, pulled from a Drowned Sailor's pocket. The last line reads: 'The Captain locked the hatch from "
        "the outside.' Corwell kept the drowned ship's roster.",
        [deliver("fen_logbook_page", "Bring the page to Huntsman Corwell in Bloodmoon Village")],
        "Corwell, in the village. He kept the roster.",
        "So that's what happened to the Captain's crew. I'd wondered. Thank you.", None,
        turn_in_npc_id=COR))
    A(Q("fen_captains_ghost", "The Captain's Ghost", COR, FEN, 22, 22, "fen_docks",
        "The ship's Captain still walks the docks, wrapped in water and rage, hunting the men he locked below. Corwell has the roster "
        "and the shame of it.",
        [boss("Captain's Ghost", FEN)],
        "On the jetty at the Drowned Docks, at night. He looks for his crew.",
        "He'll trouble no more crews. I hope the lake gives him back his rest.", None,
        requires_quests=["fen_harpoons"]))
    # ============================================================================================ CUR'S GRAVE (Selke)
    A(Q("fen_curs_grave", "Cur's Grave", HUNT, FEN, 18, 19, "fen_grave",
        "The east of the isle is a boneyard for hounds: worgs and curs, bred for the Baron's hunt, buried with their masters. Gravehunter "
        "Selke says they've started to dig themselves out.",
        [kill("Grave Worg", 6, zone=FEN), kill("Bone-Strewn Cur", 5, zone=FEN)],
        "The east lobe, past the crossroads. They dig around the old stones.",
        "Fewer dogs underfoot. I'll take it.", None))
    A(Q("fen_collars", "Packmasters' Collars", HUNT, FEN, 19, 20, "fen_grave",
        "The Feral Packmasters wear the Baron's old collars: iron, studded, stamped with the Ashbury crest. Selke wants five, to be sure "
        "nobody wears them again.",
        [fetch("fen_cur_collar", 5)],
        "The Packmasters in Cur's Grave. Cut the strap. Don't touch the studs.",
        "A crest, five times over. The Baron owned everything on this isle, even the dogs.", None,
        requires_quests=["fen_curs_grave"]))
    A(Q("fen_cur_wardens", "The Keepers of the Kennel", HUNT, FEN, 20, 21, "fen_grave",
        "The Cur-Wardens keep the graves and the dogs in them, and they speak in a language nobody has heard since the curse. Selke wants "
        "six of them quiet.",
        [kill("Cur-Warden", 5, zone=FEN)],
        "Cur's Grave, among the stones. They chant at dusk.",
        "Quiet, at last. I don't need to understand what they said.", None,
        requires_quests=["fen_curs_grave"]))
    A(Q("fen_alpha_cur", "The Alpha Cur", HUNT, FEN, 22, 22, "fen_grave",
        "The hounds of Cur's Grave follow one: a scarred, grey, impossibly large cur. The Baron's last hunt-leader. Selke wants it off "
        "the boneyard.",
        [boss("The Alpha Cur", FEN)],
        "The middle of the boneyard, among the stones. You'll hear it first.",
        "He led them well. I'll bury him with the rest. It's the least I can do.", None,
        requires_quests=["fen_collars"]))
    # ============================================================================================ FENRIS PROPER (Merrin)
    A(Q("fen_manor_approach", "Eyes on the Gate", SCOUT, FEN, 19, 20, "fen_manor",
        "Scout Merrin has been watching Baron Ashbury's manor for three nights and hasn't seen a living thing. She wants someone to walk "
        "to the gate and into the forecourt.",
        [explore(FEN, 80, 52, 4), explore(FEN, 80, 44, 3), explore(FEN, 80, 36, 4)],
        "The spine road north. Past the ridge walls, through the cracked gate, up to the fountain.",
        "Nothing stopped you. That's what worries me.", None))
    A(Q("fen_manor_guards", "The Unrelieved Guard", SCOUT, FEN, 20, 21, "fen_manor",
        "Ashbury's guard never left their posts. Footmen walk the forecourt; guardians hold the gate. Merrin wants them relieved.",
        [kill("Fenris Guardian", 5, zone=FEN), kill("Ashbury's Footman", 5, zone=FEN)],
        "The manor forecourt and the walls either side of the gate.",
        "Relieved. The Baron will be lonely.", None,
        requires_quests=["fen_manor_approach"]))
    A(Q("fen_manor_hounds", "Hounds of the Manor", SCOUT, FEN, 20, 21, "fen_manor",
        "The Baron's hounds roam the manor grounds, and the worgen keepers who feed them. Merrin has seen the keepers eat what they "
        "were meant to feed.",
        [kill("Manor Hound", 5, zone=FEN), kill("Worgen Keeper", 4, zone=FEN)],
        "The grounds around the manor, east and west of the forecourt.",
        "The grounds are quiet. The manor is not.", None,
        requires_quests=["fen_manor_approach"]))
    A(Q("fen_noble_signets", "Signets of the Cursed", SCOUT, FEN, 21, 21, "fen_manor",
        "The Cursed Nobles of Fenris Proper still wear their house signets. Merrin wants four, to prove to the Rear Guard who sat at "
        "Ashbury's table.",
        [fetch("fen_noble_signet", 4)],
        "The Cursed Nobles in the forecourt and the manor grounds. Take the rings.",
        "Four houses, four names. The Rear Guard will want these.", None,
        requires_quests=["fen_manor_guards"]))
    A(Q("fen_baron_ashbury", "Baron Ashbury", SCOUT, FEN, 22, 22, "fen_manor",
        "Baron Ashbury ruled Fenris Isle alive, and rules it worse dead. He sits in the manor hall and waits for the next guest to "
        "disappoint him. Merrin would like to see him disappointed.",
        [boss("Baron Ashbury", FEN)],
        "In the manor, past the forecourt. Dress for a funeral.",
        "The manor's quiet. The Baron is down. It's an odd thing to say, after all this.", None,
        mult=1.5, requires_quests=["fen_manor_guards", "fen_noble_signets"]))
    # ============================================================================================ SHADOWPINE ALTAR (Orlan)
    A(Q("fen_altar_arch", "The Arch in the Ridge", ALT, FEN, 20, 20, "fen_altar",
        "The curse was cast under the west ridge, in the Shadowpine Altar, and Warden Orlan has watched its arch for ten years. He wants "
        "someone to stand at the foot of the stair and tell him the air is still wrong.",
        [explore(SA, 75, 111, 5)],
        "The arch in the western ridge. The stair is below it.",
        "Still wrong. Of course. Thank you for confirming.", None))
    A(Q("fen_altar_cultists", "The Shadowpine Circle", ALT, FEN, 20, 21, "fen_altar",
        "The Shadowpine Circle never left: cultists and risen bone-warders keep the altar's rites going, long after the cause was lost. "
        "Orlan wants them thinned.",
        [kill("Shadowpine Cultist", 6, zone=SA), kill("Altar Bonewalker", 5, zone=SA)],
        "The Altar's passages and circles. Cultists cast. Bonewalkers shield.",
        "The rites will go on, I suppose. But slower.", None,
        requires_quests=["fen_altar_arch"]))
    A(Q("fen_altar_aldric", "Bonewarden Aldric", ALT, FEN, 21, 21, "fen_altar",
        "Bonewarden Aldric keeps the Bone Circle, west of the stair, and has for centuries. He's made of the things he keeps. Orlan "
        "wants him unmade.",
        [boss("Bonewarden Aldric", SA)],
        "The Bone Circle, the western cavern. Walk the stair and turn left.",
        "He was a good warden, once. He guarded the wrong thing.", None,
        requires_quests=["fen_altar_cultists"]))
    A(Q("fen_altar_tael", "Curse Keeper Tael", ALT, FEN, 22, 22, "fen_altar",
        "Curse Keeper Tael tends the Moon Circle in the east, feeding the moonstone with whatever the cult throws at it. He doesn't "
        "need to be there. He's been there for centuries.",
        [boss("Curse Keeper Tael", SA)],
        "The Moon Circle, east across the long road. Don't watch the moonstone.",
        "He won't tend it any more. The stone will dim, or it won't. Either way, thank you.", None,
        requires_quests=["fen_altar_cultists"]))
    A(Q("fen_altar_moonhowl", "Moonhowl", ALT, FEN, 22, 23, "fen_altar",
        "The Altar's worgen howl at a moon the cavern can't see. Orlan wants eight of them down, five of the wraiths that walk with "
        "them, and five moon-fangs for the cairn.",
        [kill("Moonhowl Worgen", 6, zone=SA), kill("Altar Wraith", 4, zone=SA), fetch("fen_moon_fang", 5)],
        "The Altar's circles and the long roads between. Fangs from the worgen.",
        "A cairn of fangs. The curse should keep its distance for a season.", None,
        requires_quests=["fen_altar_cultists"]))
    A(Q("fen_altar_fenris", "Alpha Fenris", ALT, FEN, 24, 24, "fen_altar",
        "At the top of the Altar Ring, the curse has a shape: Alpha Fenris, the first worgen, the one the isle is named for. Orlan "
        "has waited ten years to see him dead.",
        [boss("Alpha Fenris", SA)],
        "The Altar Ring, at the top of the long climb. Take whichever road you prefer. They all end at his door.",
        "Fenris is dead. After ten years, I'll sit, and stop watching the arch.", None,
        mult=1.6, requires_quests=["fen_altar_aldric", "fen_altar_tael"]))
    # ============================================================================================ FINALE
    A(Q("fen_isle_reckoning", "The Isle's Reckoning", ELD, FEN, 21, 22, "fen_shore",
        "Four reports have reached Gravemoss: the Curse-Beast, the Captain, the Alpha Cur and the Baron are all down. He'd like the "
        "person who carried those four threads back to stand at the well, where he can thank them properly.",
        [explore(FEN, 80, 104, 4)],
        "Back to the village square. Stand by the well.",
        "Four bosses, four reports, one hero. Bloodmoon Village has no gold to give you, so it gives you what it has.", None,
        mult=1.5, turn_in_npc_id=ELD,
        requires_quests=["fen_ancient_curse_beast", "fen_captains_ghost", "fen_alpha_cur", "fen_baron_ashbury"]))
    return Z


FETCH = {
    "sp_wl_venomsac": ("Stalker Venom Sac", "A swollen venom sac, thick as syrup.", [("Venom Stalker", 0.42)]),
    "sps_tome_page": ("Torn Archive Page", "A hovering page, ink still wet.", [("Tome Wraith", 0.42)]),
    "sps_reagent_vial": ("Sealed Reagent Vial", "A wax-sealed vial. It's warm to the touch.", [("Forsaken Alchemist", 0.42)]),
    "sps_servitor_key": ("Servant's Key Ring", "A heavy iron ring of keep keys, still faintly warm.", [("Haunted Servitor", 0.42)]),
    "fen_banshee_lock": ("Banshee's Lock of Hair", "A pale lock, cold as lake water.", [("Isle Banshee", 0.42)]),
    "fen_harpoon_head": ("Bent Harpoon Head", "An iron head, bent the same way every time.", [("Drowned Harpooner", 0.42)]),
    "fen_cur_collar": ("Ashbury Hound Collar", "A studded collar stamped with the Ashbury crest.", [("Feral Packmaster", 0.42)]),
    "fen_noble_signet": ("Noble House Signet", "A cracked signet ring, still bearing a house's crest.", [("Cursed Noble", 0.42)]),
    "fen_moon_fang": ("Moonhowl Fang", "A curved fang, tinted pale as moonlight.", [("Moonhowl Worgen", 0.42)]),
}
STARTERS = {           # item_id: (name, desc, quest_id, [(creature, chance)])
    "sp_wl_journal": ("Silk-Wrapped Journal Page", "A hunter's last page, wrapped in sticky silk.", "spn_wl_journal", [("Brood Warden", 0.14)]),
    "sps_helbrim_ledger": ("Flask-Stained Ledger", "A ledger gone green at the edges.", "sps_at_ledger", [("Forsaken Alchemist", 0.14)]),
    "fen_logbook_page": ("Water-Stained Log Page", "A page from a ship's log, hard to read.", "fen_logbook_page", [("Drowned Sailor", 0.14)]),
}


def main():
    zones = {"d": dungeons(), "f": fenris()}
    ids = set()
    outs = {}
    for k, Z in zones.items():
        out, i = BQ._finish(Z)
        outs[k] = out
        ids |= i
    # requires_quests may point at the other Silverpine files; BQ._finish already allows the sp_/ets_/etc_ prefix, so re-check here
    existing = set()
    for f in (ROOT / "data/quests").glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for q in (d["quests"] if isinstance(d, dict) else d):
            existing.add(q["quest_id"])
    for out in outs.values():
        for q in out:
            for r in q.get("requires_quests", []):
                assert r in ids or r in existing, (q["quest_id"], r)
    OUT_D.write_text(json.dumps({"quests": outs["d"]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_F.write_text(json.dumps({"quests": outs["f"]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fp = ROOT / "data/quests/forsaken_lands.json"
    fd = json.loads(fp.read_text(encoding="utf-8"))
    fd["quests"] = [q for q in fd["quests"] if not q["quest_id"].startswith("fenris_")]
    fp.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for item_id, (name, desc, srcs) in FETCH.items():
        for creature, chance in srcs:
            lst = drops.setdefault(creature, [])
            lst[:] = [d for d in lst if d["item_id"] != item_id]
            lst.append(dict(item_id=item_id, name=name, category="quest", description=desc, chance=chance))
    for item_id, (name, desc, qid, srcs) in STARTERS.items():
        assert qid in ids, qid
        for creature, chance in srcs:
            lst = drops.setdefault(creature, [])
            lst[:] = [d for d in lst if d["item_id"] != item_id]
            lst.append(dict(item_id=item_id, name=name, category="quest", description=desc, chance=chance, starts_quest=qid))
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"dungeon quests {len(outs['d'])}, fenris quests {len(outs['f'])}")


if __name__ == "__main__":
    main()
