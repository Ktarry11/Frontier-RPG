"""
Northern Barrens local quest hub (2026-10-21).  Idempotent: rewrites data/quests/northern_barrens_hub.json.

    python3 tools/build_northern_barrens_quests.py

(The 20 Taurajo / Ratchet / Orgrimmar-given quests in northern_barrens.json are untouched.)
DESIGN RULE (Kyle): NO ESCORT QUESTS - kill / fetch / boss / explore objectives only.

MAP (280x260; full notes in tools/handbuilt_northern_barrens.py)
  Road-Warden Hargak (148,206)  Gold Road waystation          Beachmaster Kizzle (222,236)  Merchant Coast beach
  Scout Mahri (194,182)         Stagnant Oasis shore          Outrider Kelsara (258,130)    Far Watch Post headland
  Fenwarden Dugmok (139,147)    Slug Fens causeway mouth      Salvager Nix (222,76)         Sludge Fen oil rig
  Claim-Surveyor Gruda (249,51) below the Boulder Lode adit   Warsong Outrider Dask (145,65) Mor'shan Base Camp
  Captain Korvash (157,31)      Mor'shan Rampart gate         Huntress Zan'Ula (26,68)      Dry Hills trailhead
  Earthcaller Rohna (66,155)    Serena's Hollow approach
Every giver has ONE chain; rares are paired with trash so the ~6 % roll never stalls a quest.
Cave-scoped objectives use zone="boulder_lode_mine" / "serenas_hollow" (they only count inside the cave).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import kill, fetch                      # noqa: E402
from tools.build_southern_barrens_quests import R, boss                 # noqa: E402

OUT = ROOT / "data/quests/northern_barrens_hub.json"
Z = "northern_barrens"
MINE = "boulder_lode_mine"
HOLLOW = "serenas_hollow"


def explore(x, y, radius=8):
    return dict(type="explore", target=Z, target_x=x, target_y=y, radius=radius)


def Q(qid, title, giver, lvl, desc, objs, accept, turnin, rewards, nxt=None, xp=None, gold=None, span=2):
    return dict(
        quest_id=qid, title=title, giver_npc_id=giver, zone=Z, level_min=lvl, level_max=lvl + span,
        description=desc, objectives=objs,
        reward_exp=xp or int(lvl * 58 + 40), reward_gold=gold or int(lvl * 240),
        accept_text=accept, turn_in_text=turnin, rewards=rewards, next_quest_id=nxt)


def quests():
    A = []
    a = A.append

    # ============================== ROAD-WARDEN HARGAK (Gold Road waystation) ==============================
    G = "nb_road_warden"
    a(Q("nb_toll_collectors", "Toll Collectors", G, 14,
        ("The Gold Road is the only honest thing in the Northern Barrens, and someone has started charging for "
         "it. Road Bandits wait at the bends, polite for exactly one sentence, and every wagon that can't pay "
         "gets lighter. Hargak runs the waystation and has run out of patience."),
        [kill("Road Bandit", 6)],
        ("They wear their coats the wrong way round so you can't tell who they are. I can tell. Thin them out "
         "along the bends and bring me what you find."),
        ("Fewer coats, more wagons. That's the arithmetic I like. Here, the waystation's thanks."),
        [R(14, "Waystation Drover's Coat", "chest", "of the Bear", "Heavy canvas, waxed against the rain. It has outlasted three previous owners.", "leather"),
         R(14, "Wagon-Guard Cudgel", "main_hand", "of the Soldier", "A short iron-banded club. Excellent at ending arguments over fares.", "mace_1h"),
         R(14, "Teamster's Road-Boots", "feet", "of the Monkey", "Broken in on ten thousand miles of rut. Your feet will never feel the difference.", "leather")],
        nxt="nb_the_highwaymans_ledger"))
    a(Q("nb_the_highwaymans_ledger", "The Highwayman's Ledger", G, 15,
        ("Bandits keep books. Hargak finds this both funny and useful. Every Road Bandit carries a stained page "
         "of who paid, who didn't, and which wagons are worth the trouble. Collect enough pages and you can read "
         "the route they plan next."),
        [fetch("highwayman_ledger", 5)],
        ("Five pages should do. Look in their coat linings. They think nobody checks there."),
        ("Mm. They're going to hit the coast road next. I'd better tell someone with a spear. Take this."),
        [R(15, "Ledger-Keeper's Spectacles", "head", "of the Eagle", "Thick lenses in a bent wire frame. Numbers stand still when you look at them.", "cloth"),
         R(15, "Bandit-Taker's Wristguards", "wrist", "of the Tiger", "Bracers stripped from a bandit chief's arms. They still smell of cheap rum.", "leather"),
         R(15, "Pageturner's Quiet Dagger", "main_hand", "of the Assassin", "Thin, light, perfect for opening letters and, occasionally, people.", "dagger")],
        nxt="nb_cutthroats_on_the_road"))
    a(Q("nb_cutthroats_on_the_road", "Cutthroats on the Road", G, 16,
        ("The pages named a crew: cutthroats on foot, outriders on beasts, working the stretch of road between "
         "the oasis fork and the coast. They are not toll collectors. They do not ask first."),
        [kill("Bandit Cutthroat", 5), kill("Bandit Outrider", 4)],
        ("Cutthroats move in pairs and outriders cover them from a distance. Take the outriders' bows first if "
         "you can. They hurt more than they look."),
        ("The road's quiet. That's the first time in a season. You've earned more than I can pay, but this is what I have."),
        [R(16, "Roadwarden's Mail Hauberk", "chest", "of the Soldier", "Riveted mail, patched with road-iron. It has stopped a few too many knives.", "mail"),
         R(16, "Outrider's Short-Bow", "ranged", "of the Marksman", "Light and quick. Built for shooting from a moving mount.", "bow"),
         R(16, "Gold Road Signet", "ring", "of the Falcon", "A ring cast from a mile-marker. It makes the road feel a little shorter.")],
        xp=1020, gold=3860))

    # ============================== BEACHMASTER KIZZLE (Merchant Coast) ==============================
    G = "nb_coast_sergeant"
    a(Q("nb_wreckers_beach", "Wreckers' Beach", G, 14,
        ("The Merchant Coast is the Barrens' loading dock, which is why every crab in the bay has decided it "
         "owns the pier. Tide-Wreckers pry the planks off cargo crates, drag them out to sea and nobody sees "
         "either again. Kizzle has asked nicely. She's now asking differently."),
        [kill("Tide-Wrecker Crab", 6)],
        ("Big, red, sulky. They hide in the surf. Crack a few and the rest will remember they have other places to be."),
        ("Listen to that, bro. Nothing! Not one claw! Take this, with the beachmaster's gratitude."),
        [R(14, "Crabshell Beach-Plate", "chest", "of the Bastion", "Shell plates sewn onto a leather vest. Don't wear it in the surf. It floats.", "mail"),
         R(14, "Beachmaster's Claw-Cutter", "main_hand", "of the Duelist", "A short curved blade for cutting claws, fish and, sometimes, trouble.", "sword_1h"),
         R(14, "Barnacle-Crusted Sash", "waist", "of the Whale", "Stiff with salt. It keeps its shape even when you don't.", "cloth")],
        nxt="nb_salvage_rights"))
    a(Q("nb_salvage_rights", "Salvage Rights", G, 14,
        ("Southsea Brigands have been dragging cargo crates up the beach and prying them open. Anything they "
         "haven't opened yet is, strictly speaking, still the Merchants'. Kizzle's definition of 'strictly "
         "speaking' is flexible."),
        [fetch("salvaged_cargo_crate", 5)],
        ("Five crates. Don't open them. I know what's in them. Don't ask how."),
        ("These are mine! Er, the Merchants'. Same thing, really. Take this for your trouble."),
        [R(14, "Salvager's Oilskin Cloak", "back", "of the Eagle", "Slick and tarry. Rain and spilled rum slide right off.", "cloth"),
         R(14, "Brigand-Taker's Cutlass", "main_hand", "of the Soldier", "A pirate's blade with a repaired hilt. Still sharp, still opinionated.", "sword_1h"),
         R(14, "Crate-Lifter's Gloves", "hands", "of the Bear", "Thick palms and reinforced thumbs. They stop splinters and some bad decisions.", "leather")],
        nxt="nb_silence_the_cannons"))
    a(Q("nb_silence_the_cannons", "Silence the Cannons", G, 15,
        ("The Southsea crews have mounted three cannons on the cliffs and are using them for target practice on "
         "anything that floats. Kizzle has a Ratchet-built guarantee that her pier is 'definitely not in range'. "
         "It definitely is."),
        [kill("Southsea Cannoneer", 5), kill("Southsea Brigand", 5)],
        ("Cannoneers stand behind the brigands. Cut through the brigands. Don't stand in a line."),
        ("Quiet again! Well, 'quiet' for a harbour. Here, take this. It's cleaner than it looks."),
        [R(15, "Cannoneer's Powder-Burnt Gloves", "hands", "of the Marksman", "Black with soot at the fingertips. They never quite wash out.", "leather"),
         R(15, "Fuse-Cutter's Dirk", "main_hand", "of the Assassin", "A short dagger with a notch in the blade. For fuses. Mostly.", "dagger"),
         R(15, "Harbour Guard's Brass Pauldrons", "shoulder", "of the Soldier", "Polished brass, bent in places by something heavy. Looks good on a pier.", "mail")],
        nxt="nb_captain_saltspray"))
    a(Q("nb_captain_saltspray", "Captain Saltspray", G, 16,
        ("Captain Saltspray runs the Southsea crew. He's not very good at it, but he is very loud, and the loud "
         "ones make the cannoneers brave. Take him down and the harbour might finally get some peace."),
        [boss("Captain Saltspray"), kill("Southsea Brigand", 5)],
        ("He shows himself when his crew is winning. Make them stop winning. Then make him regret showing himself."),
        ("The captain's down, and the beach is ours again. Come back in a week; there'll be a drink with your name on it."),
        [R(16, "Saltspray's Tricorn", "head", "of the Duelist", "A battered pirate hat, still damp. It's taller than it looks.", "leather"),
         R(16, "Beachmaster's Grudge-Blade", "main_hand", "of the Champion", "A heavy cutlass. It's a pirate's. It doesn't care whose pocket it's in.", "sword_1h"),
         R(16, "Harbour-Keeper's Seal", "neck", "of the Whale", "A brass pendant with a cannon stamped on it. Cold to the touch, warm to the conscience."),
         R(16, "Southsea Buccaneer's Pistol", "ranged", "of the Bandit", "A flintlock with a stolen engraving. It has fewer opinions than its former owner.", "gun")],
        xp=1080, gold=4200, span=3))

    # ============================== SCOUT MAHRI (Stagnant Oasis) ==============================
    G = "nb_oasis_scout"
    a(Q("nb_hounds_of_the_oasis", "Hounds of the Oasis", G, 17,
        ("The Stagnant Oasis hasn't been fit to drink from in years, but it still draws every wanderer in the "
         "plains. Lately it also draws dervish hounds, lean, mange-ridden things that Kolkar dervishes breed "
         "and set loose. Mahri wants them gone before they learn what a campfire is for."),
        [kill("Dervish Hound", 6)],
        ("They circle first and bite after. Keep your back to something solid. A cliff, a tent, anything."),
        ("They've stopped howling. I never realised how much of the night they filled. Take this."),
        [R(17, "Oasis Scout's Leather Cap", "head", "of the Wolf", "Sun-bleached leather with a flap for the neck. It smells strongly of dog.", "leather"),
         R(17, "Hound-Tamer's Chain-Whip", "main_hand", "of the Beast", "A light chain on a leather grip. Excellent for persuading things that bite.", "mace_1h"),
         R(17, "Watcher's Dust-Wrap", "wrist", "of the Eagle", "Cloth wrapping against grit. You'll never lose track of your own hands again.", "cloth")],
        nxt="nb_curved_blades"))
    a(Q("nb_curved_blades", "Curved Blades", G, 17,
        ("Kolkar dervishes fight with curved blades they sharpen on the same stones they pray at. Mahri's "
         "scouts want half a dozen, not to use, but to read. The edges carry marks that say who trained whom."),
        [fetch("dervish_curved_blade", 6)],
        ("Cut them off the bodies. Bring me six and I'll show you what the marks mean."),
        ("These are from the same forge. There's a smith feeding the whole camp. That's worth knowing. Take this."),
        [R(17, "Dervish-Hunter's Mail Coif", "head", "of the Soldier", "Heavy rings and a leather lining. It dents blades instead of being dented.", "mail"),
         R(17, "Blade-Reader's Bracers", "wrist", "of the Falcon", "Thin leather laced with copper wire. It keeps your wrists quick and your pulse steady.", "leather"),
         R(17, "Bent-Steel Scimitar", "main_hand", "of the Duelist", "A curved blade taken from a dervish. It sings when you swing it fast.", "sword_1h")],
        nxt="nb_stormcallers"))
    a(Q("nb_stormcallers", "Stormcallers", G, 18,
        ("A band of Kolkar Stormcallers has taken up at the far side of the oasis, drawing lightning out of a "
         "sky that hasn't seen rain in months. It's not working. It's still giving everyone a headache. Mahri "
         "would like to be able to think again."),
        [kill("Kolkar Stormcaller", 4)],
        ("They stay together in the middle and the dervishes ring them. Break the ring, then the casters. "
         "Don't stand in the lightning. I mean that literally."),
        ("The sky is quiet. Wonderful. I can even hear the wind. Take this, with the camp's thanks."),
        [R(18, "Stormcaller's Static-Wrap", "hands", "of the Sorcerer", "Silk gloves that crackle when you clap. Not entirely safe near copper.", "cloth"),
         R(18, "Thunder-Etched Totem", "off_hand", "of the Seer", "A small stone totem carved with lightning. It hums when thunder is near.", "totem"),
         R(18, "Oasis Dowser's Pendant", "neck", "of the Prophet", "A bent copper pendant on a thong. It dips when water is within a day's walk.")],
        nxt="nb_verog_the_dervish"))
    a(Q("nb_verog_the_dervish", "Verog the Dervish", G, 19,
        ("Verog leads the dervishes. He's fast, he's patient, and he's quick to be offended, which makes him "
         "the best bait the Kolkar could have used and the worst enemy anyone could have. The oasis will never "
         "be safe while he spins at the heart of it."),
        [boss("Verog the Dervish"), kill("Kolkar Dervish", 5)],
        ("He spins when he's angry and he's always angry. Wait for the spin to wind down, then hit him. "
         "Dervishes around him first, though. You want him alone."),
        ("Verog's dead. I never thought I'd see it. Take this, and let me be the first to buy you a drink."),
        [R(19, "Verog's Spinning-Belt", "waist", "of the Tiger", "A broad belt studded with iron spikes. It never stops swinging, even when you do.", "leather"),
         R(19, "Dervish-Slayer's Greaves", "legs", "of the Juggernaut", "Mail legguards, notched where blades struck and failed. The notches are a record.", "mail"),
         R(19, "Verog's Twin Scimitar", "main_hand", "of the Gladiator", "A pair of curved blades riveted together. It's heavier than it looks and prouder than it should be.", "sword_1h"),
         R(19, "Oasis Warden's Medallion", "neck", "of the Eagle", "A coin of old stone from the oasis shore. It gets warmer when allies are near.")],
        xp=1220, gold=4560, span=3))

    # ============================== OUTRIDER KELSARA (Far Watch Post) ==============================
    G = "farwatch_officer"
    a(Q("nb_raiders_at_the_gate", "Raiders at the Gate", G, 15,
        ("Far Watch Post holds the eastern road, and the Kolkar know it. Every dawn another band of raiders "
         "rides up the headland, circles the watchtower and tests the palisade. Kelsara has counted forty "
         "since last full moon. She's stopped counting them as people."),
        [kill("Kolkar Raider", 6)],
        ("They test the weak spots. There aren't any. Convince them of that with a spear."),
        ("Nothing at the palisade for an hour now. Almost suspicious. Take this and don't question luck."),
        [R(15, "Watch-Post Studded Vest", "chest", "of the Soldier", "Leather studded with iron nails. It stops a blade or two.", "leather"),
         R(15, "Headland Spear", "main_hand", "of the Bear", "A long ash spear with a sharp iron head. Best used before the raiders reach the wall.", "polearm"),
         R(15, "Far Watch Signet", "ring", "of the Whale", "A plain iron ring stamped with a tower. It's cold in the morning and warm after a fight.")],
        nxt="nb_war_pennants"))
    a(Q("nb_war_pennants", "War-Pennants", G, 15,
        ("Every Kolkar warband carries a pennant, a strip of dyed hide on a stick that tells the others who's "
         "in charge. Take enough of them and the bands lose their way. Kelsara is tired of reading the same "
         "colours at the same hour every morning."),
        [fetch("kolkar_warpennant", 6)],
        ("Six pennants. Don't burn them. I want to read them first."),
        ("The colours match three different bands. They've united. That's bad. Take this, and be quick going back out."),
        [R(15, "Pennant-Bearer's Cloak", "back", "of the Falcon", "A strip of dyed hide cut into a cloak. It flaps beautifully in a wind.", "cloth"),
         R(15, "Standard-Taker's Bracers", "wrist", "of the Soldier", "Mail bracers taken from a Kolkar standard-bearer. They fit better than they should.", "mail"),
         R(15, "Warband-Breaker's Axe", "main_hand", "of the Champion", "A broad axe with a notch cut in the haft for each band broken.", "axe_1h")],
        nxt="nb_scoutriders_on_the_headland"))
    a(Q("nb_scoutriders_on_the_headland", "Scoutriders on the Headland", G, 16,
        ("Kolkar Scoutriders ride the headland every night, measuring the watchtower's blind spots. Kelsara has "
         "no blind spots. She does have a lot of drudges stealing from the supply line while the scouts watch. "
         "She'd like both problems gone."),
        [kill("Kolkar Scoutrider", 5), kill("Kolkar Drudge", 5)],
        ("Scoutriders on beasts, drudges on foot. Cut the drudges down first. They're slow, and the scouts will "
         "come to rescue them."),
        ("The headland's quiet again. You earned this, and a place in my orders."),
        [R(16, "Scout-Catcher's Leggings", "legs", "of the Monkey", "Reinforced at the knees for long ambushes in short grass.", "leather"),
         R(16, "Beast-Rider's Crossbow", "ranged", "of the Hunt", "A short, light crossbow built to fire from a moving mount.", "crossbow"),
         R(16, "Watchtower Warden's Shoulders", "shoulder", "of the Bear", "Mail shoulderguards stamped with a tower. They make you feel taller than you are.", "mail")],
        nxt="nb_kragg_the_wall_breaker"))
    a(Q("nb_kragg_the_wall_breaker", "Kragg the Wall-Breaker", G, 17,
        ("Kragg is a warbrand chief who has never met a palisade he couldn't test. He rides a hide-clad "
         "warbeast and brings a ram. Far Watch's wall has stood for ten years and he's decided that's too long."),
        [boss("Kragg the Wall-Breaker"), kill("Kolkar Warbrand", 5)],
        ("He comes at dusk, usually. Warbrands first, then him. If he reaches the wall, we all know what happens."),
        ("Kragg's down. The wall holds. I'll raise a drink and a banner. Take this, the Post's thanks."),
        [R(17, "Wall-Breaker's Ram-Horn Helm", "head", "of the Juggernaut", "A ram's horns on a mail coif. It looks fierce and weighs more than it should.", "mail"),
         R(17, "Kragg's Battering Maul", "main_hand", "of the Gladiator", "A massive two-handed maul. It breaks walls. And more.", "mace_2h"),
         R(17, "Ram-Hide Waistguard", "waist", "of the Bear", "Thick hide with iron studs. It's heavy and nearly bite-proof.", "leather"),
         R(17, "Far Watch Commander's Cloak", "back", "of the Eagle", "A cloak edged in the Post's colours. It catches the wind and holds your head high.", "cloth")],
        xp=1170, gold=4350, span=3))

    # ============================== FENWARDEN DUGMOK (Slug Fens) ==============================
    G = "nb_fen_warden"
    a(Q("nb_slugs_in_the_reeds", "Slugs in the Reeds", G, 15,
        ("The Slug Fens used to be only slow, wet and quiet. Then the slugs got big. Dugmok's wardens keep "
         "the causeway open, but the slugs are creeping across it at night, and nobody wants to explain why a "
         "caravan went in and the cargo came out as soup."),
        [kill("Slug", 6)],
        ("Pale, fat, and bigger than a dog. Cut them back from the causeway. If they wriggle, hit harder."),
        ("Quiet. Thick, wet, honest quiet. Thank you. Take this, with the fen's thanks."),
        [R(15, "Fenwarden's Mudproof Coat", "chest", "of the Bear", "Waxed leather with a mud-shedding finish. It's never quite clean.", "leather"),
         R(15, "Reed-Cutter's Billhook", "main_hand", "of the Squire", "A curved blade for cutting reeds. Also slugs.", "axe_1h"),
         R(15, "Causeway Boots", "feet", "of the Whale", "High boots with sealed seams. They keep water out and tempers in.", "leather")],
        nxt="nb_venom_glands"))
    a(Q("nb_venom_glands", "Venom Glands", G, 15,
        ("Fen slugs carry venom glands in their backs, a green sac that makes a first-rate poison if you "
         "know how to cure it. Dugmok knows how. He'd rather not touch them himself."),
        [fetch("slug_venom_gland", 6)],
        ("Cut them out whole. Don't pop them. If you do, we'll be burying a tauren."),
        ("Good clean glands. I'll make something for the next caravan. Take this."),
        [R(15, "Venom-Tapper's Gloves", "hands", "of the Assassin", "Treated leather that resists most poisons. Not all. Don't test it.", "leather"),
         R(15, "Fenwarden's Poisoner's Knife", "main_hand", "of the Assassin", "A narrow blade with a groove for venom. Neat, nasty, fast.", "dagger"),
         R(15, "Glandkeeper's Pendant", "neck", "of the Beast", "A tiny glass vial on a cord. It tingles when something poisonous is near.")],
        nxt="nb_peat_hearts"))
    a(Q("nb_peat_hearts", "Peat Hearts", G, 16,
        ("Deep in the fens the peat has started to move. Peat Shamblers, mud and root and old bog-oak, "
         "shuffle along the causeway at night. At the heart of each is a warm core that Dugmok can burn "
         "through a cold winter, if he can get it out."),
        [fetch("peat_heart", 5), kill("Peat Shambler", 5)],
        ("You'll have to break them. Hit the middle. The heart's a lump the size of your fist."),
        ("Ha! Warm already. You're a wonder. Take this."),
        [R(16, "Peatwalker's Mossweave Hood", "head", "of the Whale", "A cloth hood grown over with moss. It smells like the fen, which is oddly comforting.", "cloth"),
         R(16, "Bogwarden's Studded Leggings", "legs", "of the Bear", "Leather leggings with bog-iron studs. Heavy, damp, and nearly indestructible.", "leather"),
         R(16, "Shambler-Smasher's Staff", "main_hand", "of the Seer", "A heavy staff of bog-oak. It's still faintly warm.", "staff")],
        nxt="nb_old_mire_maw"))
    a(Q("nb_old_mire_maw", "Old Mire-Maw", G, 17,
        ("Something old and very hungry lives at the bottom of the deep fen, Old Mire-Maw, a crocolisk "
         "older than the causeway and wider than a wagon. Dugmok has lost three wardens to it. He's decided "
         "that's enough."),
        [boss("Old Mire-Maw"), kill("Fenwater Crocolisk", 4)],
        ("It hides in the deep pools, at the end of the causeway. Don't stand in the water. Don't stand near "
         "the water. If you can, don't stand."),
        ("Mire-Maw's dead. I never thought I'd say it. Come back and I'll carve you something from its tooth."),
        [R(17, "Mire-Maw's Scaled Jerkin", "chest", "of the Juggernaut", "Scales from the old croc. They shed water and blows with equal contempt.", "mail"),
         R(17, "Maw-Tooth Cleaver", "main_hand", "of the Gladiator", "A great axe edged with a crocolisk's tooth. It bites twice.", "axe_2h"),
         R(17, "Fenwarden's Oath-Ring", "ring", "of the Bear", "A ring of bog-iron cast from a warden's old chain. It's heavier than it looks.")],
        xp=1020, gold=4080, span=3))

    # ============================== SALVAGER NIX (Sludge Fen) ==============================
    G = "nb_sludge_inspector"
    a(Q("nb_rig_crews", "Rig Crews", G, 17,
        ("Nix used to work for the Venture Company, before he learned what they were doing in the fen. Now he "
         "watches the rig from a rusted shack and counts the crews. They've been drilling day and night, and "
         "the ground is bleeding black. He wants the crews gone, preferably without anyone he likes in the way."),
        [kill("Venture Co. Oil Driller", 6)],
        ("The drillers are the loud ones. Stop the noise and the guards come out. They're quieter, and nastier."),
        ("Quiet! Real quiet. The fen has a pulse again. Take this, from a man who knows what it's worth."),
        [R(17, "Driller's Soot-Stained Vest", "chest", "of the Bear", "Black with oil and old grease. It stops most things, even a bad smell.", "leather"),
         R(17, "Pipe-Wrench Maul", "main_hand", "of the Soldier", "A heavy two-handed wrench. It's built for pipes. It works on skulls too.", "mace_2h"),
         R(17, "Goggles of the Pit-Crew", "head", "of the Monkey", "Thick lenses, scratched and oily. They show you the world in sepia.", "cloth")],
        nxt="nb_pressure_gauges"))
    a(Q("nb_pressure_gauges", "Pressure Gauges", G, 18,
        ("Every rig has a gauge, and every gauge tells a story: how hard they're drilling, how deep, and how "
         "close the whole fen is to blowing. Nix wants five of them from the pumpjack guards. He's lost the "
         "nerve to ask nicely."),
        [fetch("oil_pressure_gauge", 5), kill("Pumpjack Guard", 4)],
        ("Pumpjack guards keep them on a chain. Cut the chain. Don't cut the guard's friends. They fight back."),
        ("Ha. Look at that needle. They're drilling too deep. It's going to blow. Take this and keep your distance."),
        [R(18, "Pumpjack-Guard's Rubber Gloves", "hands", "of the Bear", "Thick and chemical-proof. They make you feel invincible, which is dangerous.", "leather"),
         R(18, "Gauge-Reader's Brass Dagger", "main_hand", "of the Duelist", "A small brass blade with a dial on the pommel. It points to the nearest trouble.", "dagger"),
         R(18, "Pressure-Valve Ring", "ring", "of the Soldier", "A brass ring with a tiny valve. It hisses when you're angry.")],
        nxt="nb_sludge_samples"))
    a(Q("nb_sludge_samples", "Sludge Samples", G, 18,
        ("Where the oil's pooled, the sludge has started to move. Sludge Elementals, black, sticky, and very "
         "angry. Nix wants samples to prove to the Company that its drilling is doing this. He'd also like "
         "not to be near them while they're collected."),
        [fetch("crude_sludge_sample", 6), kill("Sludge Elemental", 5)],
        ("Take the samples from the middle. They leave a slick. Careful. The goop doesn't come off."),
        ("Look at that. Pure, black, and very illegal. They won't be able to deny it. Take this."),
        [R(18, "Slickwalker's Oilcloth Cloak", "back", "of the Whale", "Treated cloth that sheds oil and the occasional curse.", "cloth"),
         R(18, "Sludge-Smeared Greaves", "legs", "of the Soldier", "Mail legguards stained black. They look awful and stop blows.", "mail"),
         R(18, "Black-Gold Pendant", "neck", "of the Prophet", "A drop of cured crude in glass. It's weirdly beautiful and heavy.")],
        nxt="nb_supervisor_lugwizzle"))
    a(Q("nb_supervisor_lugwizzle", "Supervisor Lugwizzle", G, 18,
        ("Lugwizzle runs the rig. He screams a lot, throws wrenches, and signs every order. If he stops, the "
         "rig stops. If the rig stops, the fen heals. Nix has drawn you a map to the pumphouse."),
        [boss("Supervisor Lugwizzle"), kill("Venture Co. Oil Driller", 5)],
        ("He's usually in the pumphouse, shouting. He throws oil. Don't stand in it."),
        ("Lugwizzle's down, and the rig's quiet. Take this. I owe you more than I'll ever have."),
        [R(18, "Lugwizzle's Greasy Gauntlets", "hands", "of the Juggernaut", "Heavy gloves slick with old oil. They don't slip, which is annoying.", "mail"),
         R(18, "Supervisor's Whistle", "neck", "of the Soldier", "A brass whistle on a chain. One blast and the shift ends, usually badly."),
         R(18, "Foreman-Beater's Wrench", "main_hand", "of the Champion", "A massive wrench with a dented head. It still has a little of Lugwizzle on it.", "mace_1h")],
        nxt="nb_engineer_whirleygig", xp=1100, gold=4300))
    a(Q("nb_engineer_whirleygig", "Engineer Whirleygig", G, 19,
        ("With Lugwizzle gone the engineer is panicking. Whirleygig is the one who actually made the "
         "drillers work, and he's building something large and noisy in the back of the shop. Nix says it "
         "is going to explode. Nix says a lot of things, but he's usually right about that one."),
        [boss("Engineer Whirleygig"), kill("Pumpjack Guard", 4)],
        ("He's got turrets. Kill the guards, then him. Don't be near him when he trips the switch."),
        ("The thing's dead, the engineer's dead, and the fen will heal in time. Take this. It's the last of what I own that's worth giving."),
        [R(19, "Whirleygig's Goggles", "head", "of the Archmage", "Brass goggles with seven lenses. You can see far, and also hear a faint ticking.", "cloth"),
         R(19, "Engineer's Shock-Mail", "chest", "of the Bastion", "Mail wired with copper. It crackles when you're hit.", "mail"),
         R(19, "Sprocket-Spun Boots", "feet", "of the Monkey", "Leather boots with tiny gears on the heels. They tick as you walk.", "leather"),
         R(19, "Clockwork Pistol", "ranged", "of the Marksman", "A small pistol with a spring-driven action. It jams only when you least expect it.", "gun")],
        xp=1200, gold=4560, span=3))

    # ============================== CLAIM-SURVEYOR GRUDA (Boulder Lode Mine) ==============================
    G = "nb_lode_surveyor"
    a(Q("nb_claim_jumpers", "Claim Jumpers", G, 14,
        ("The Boulder Lode was a Horde claim before the Venture Company moved in. Now Miners swing picks on "
         "its walls and Overseers shout in its tunnels, and Gruda has the paperwork to prove who owns the "
         "ore. The paperwork is not helping."),
        [kill("Venture Co. Miner", 6, zone=MINE)],
        ("Go in and clear the miners from the lower galleries. They're not soldiers. They'll still hit you "
         "with a pick."),
        ("The lower galleries are ours again. I can hear the dust settling. Take this."),
        [R(14, "Surveyor's Tool-Belt", "waist", "of the Bear", "Leather loops and pockets for every kind of tool. It jingles in a way you quickly forget.", "leather"),
         R(14, "Claim-Holder's Pickaxe", "main_hand", "of the Soldier", "A sturdy miner's pick with a polished handle. Dig or fight, it doesn't care.", "axe_1h"),
         R(14, "Miner's Hard-Hat", "head", "of the Whale", "An iron cap with a lantern bracket. You will bump your head. It won't hurt as much.", "mail")],
        nxt="nb_heart_of_the_vein"))
    a(Q("nb_heart_of_the_vein", "Heart of the Vein", G, 15,
        ("The Elementals in the mine are made of the same rock as the walls, and the walls are laced with "
         "crystal. If Gruda can read the vein, she can tell how much the Company has already taken. "
         "Sample cores from the big ones."),
        [fetch("vein_core_sample", 5, ), kill("Cavern Rock Elemental", 4, zone=MINE)],
        ("Break them open. You'll find a glowing core in each. Bring me five. I'll read the vein."),
        ("The vein's rich. Richer than they let on. And they've taken nearly half. Take this, with my thanks."),
        [R(15, "Vein-Reader's Loupe", "head", "of the Eagle", "A jeweller's loupe in a leather cap. It shows seams you didn't know were there.", "cloth"),
         R(15, "Core-Cracker's Hammer", "main_hand", "of the Squire", "A small hammer with a broad face. It breaks stone and small egos.", "mace_1h"),
         R(15, "Crystal-Core Pendant", "neck", "of the Prophet", "A tiny crystal on a cord. It pulses faintly when you walk past ore.")],
        nxt="nb_sprites_in_the_seams"))
    a(Q("nb_sprites_in_the_seams", "Sprites in the Seams", G, 15,
        ("The ore sprites are small, bright and mean. They live in the crystal seams and bite anything that "
         "gets close. Gruda wants their shards, a chip off each, for her assay table."),
        [fetch("ore_sprite_shard", 6), kill("Ore Sprite", 5, zone=MINE)],
        ("Quick and glowing. Hit them while they're pausing to sparkle. Don't breathe their dust."),
        ("Beautiful. And they test out rich, too. Take this, with the claim's thanks."),
        [R(15, "Sprite-Catcher's Gloves", "hands", "of the Sorcerer", "Fine silk lined with thread of copper. It never quite stops tingling.", "cloth"),
         R(15, "Shard-Studded Wristguards", "wrist", "of the Falcon", "Leather bracers set with sprite shards. They catch lamplight and tempers.", "leather"),
         R(15, "Assayer's Brass Wand", "ranged", "of the Archmage", "A thin brass wand with a crystal tip. It buzzes near ore.", "wand")],
        nxt="nb_prospector_delvik"))
    a(Q("nb_prospector_delvik", "Prospector Delvik", G, 16,
        ("Delvik was Gruda's partner once. He sold the claim's map to the Venture Company for a promise and "
         "a bag of silver, and now hides in a side adit with a rifle and a bad conscience. Gruda would "
         "like him to explain himself, if possible. If not, it won't be a surprise."),
        [boss("Prospector Delvik", zone=MINE), kill("Venture Co. Tinkerer", 4, zone=MINE)],
        ("He's in a side adit off the middle gallery, behind a pile of rubble. He shoots first. "
         "Tinkerers will keep him company. Clear them out and you've done most of it."),
        ("So he did get what he deserved. I'd wish it a quieter end, but I'm not sorry. Take this."),
        [R(16, "Delvik's Prospector Duster", "chest", "of the Marksman", "A long dust-coat with a hundred pockets. They're mostly empty.", "leather"),
         R(16, "Delvik's Long Rifle", "ranged", "of the Hunt", "A long-barrelled rifle, scratched and oiled. It's very accurate, if you can stand the smell.", "gun"),
         R(16, "Traitor's Silver Ring", "ring", "of the Falcon", "A heavy silver band. It was worth more once.")],
        nxt="nb_foreman_grills"))
    a(Q("nb_foreman_grills", "Foreman Grills", G, 17,
        ("At the top of the mine, round a vein of blue crystal, Foreman Grills runs the Company's crew. He "
         "wears an iron hat, shouts orders through a bullhorn and is, in his own estimation, the cleverest "
         "man ever to hold a pick. Gruda says he's only the loudest."),
        [boss("Foreman Grills", zone=MINE), kill("Venture Co. Overseer", 3, zone=MINE)],
        ("He's at the top, in the crystal chamber. Overseers guard the way up. Take them out and he's alone, "
         "if you can call a man with a bullhorn alone."),
        ("Grills is dead, the claim's ours, and the vein will outlast us all. Take this, with the claim's honour."),
        [R(17, "Foreman's Iron Hat", "head", "of the Juggernaut", "A heavy iron hat with a dented crown. It has survived worse than you.", "mail"),
         R(17, "Grills' Bullhorn-Blade", "main_hand", "of the Champion", "A heavy sword with a flared guard, shaped suspiciously like a horn.", "sword_1h"),
         R(17, "Vein-Heart Crystal", "neck", "of the Archmage", "A chunk of blue crystal from the top of the vein. It glows in the dark."),
         R(17, "Lodeguard's Mail Shoulders", "shoulder", "of the Bastion", "Mail shoulders chipped from a day's labour. They bear the Company's stamp, scratched out.", "mail")],
        xp=1030, gold=4080, span=3))

    # ============================== WARSONG OUTRIDER DASK (Mor'shan Base Camp) ==============================
    G = "morshan_outrider"
    a(Q("nb_siege_lines", "Siege Lines", G, 16,
        ("Mor'shan Base Camp sits under the Rampart like a thorn in the Kaldorei's side. Kolkar Warbrands "
         "surround it. Dask doesn't blame them: he'd attack, too. He'd like the Warbrands to stop camping "
         "on the supply road."),
        [kill("Kolkar Warbrand", 5)],
        ("Warbrands are tough, loud and always in a group of four. Break one group and the rest will think "
         "twice. Don't think twice yourself."),
        ("The supply road's clear! Well, clearer. Take this, from a grateful outrider."),
        [R(16, "Warsong Outrider's Leather Tunic", "chest", "of the Wolf", "A Warsong leather tunic, scratched and sun-faded. It's more comfortable than it looks.", "leather"),
         R(16, "Outrider's Wolfhide Cloak", "back", "of the Hunt", "A grey wolf-pelt cloak. It still has a little of the wolf's attitude.", "cloth"),
         R(16, "Camp Guard's Spear", "main_hand", "of the Soldier", "A long spear for guarding tent-lines. It reaches further than you think.", "polearm")],
        nxt="nb_break_the_scouts"))
    a(Q("nb_break_the_scouts", "Break the Scouts", G, 16,
        ("Scoutriders ride the hills above the Base Camp and report every movement to the Rampart. Dask "
         "doesn't mind being watched. He minds being shot at, which the scouts do for sport."),
        [kill("Kolkar Scoutrider", 6)],
        ("They shoot from range and run. Chase the slow ones. The fast ones will come back."),
        ("They've stopped watching. Good. I can have a quiet breakfast. Take this."),
        [R(16, "Scout-Breaker's Boots", "feet", "of the Monkey", "Light boots for chasing riders. They're very quiet.", "leather"),
         R(16, "Riders' Short-Bow", "ranged", "of the Marksman", "A short bow with a pull as stiff as a Kolkar's temper.", "bow"),
         R(16, "Outrider's Dust-Scarf", "neck", "of the Falcon", "A long cloth scarf against the sand. It's been lucky so far.")],
        nxt="nb_scout_captain_vrek"))
    a(Q("nb_scout_captain_vrek", "Scout-Captain Vrek", G, 17,
        ("Vrek commands the Rampart-watchers and is the one who tells the Kaldorei when to shoot. He rides "
         "a swift, sharp-eyed hawk and sees everything on the plain. Dask wants him blinded, preferably "
         "permanently."),
        [boss("Scout-Captain Vrek"), kill("Kolkar Raider", 5)],
        ("He hides among the scoutriders. If you can get to him, he's weak. If he gets to you, you're not."),
        ("Vrek's down. The Rampart can't see us for a day or two. That may be all we need. Take this."),
        [R(17, "Vrek's Hawk-Feather Hood", "head", "of the Falcon", "A hood trimmed with hawk feathers. The wind lifts them as if the hawk were still alive.", "leather"),
         R(17, "Scout-Captain's Spyglass-Blade", "main_hand", "of the Duelist", "A narrow blade with a small spyglass set in the pommel. Impractical, delightful.", "sword_1h"),
         R(17, "Warsong Pathfinder's Belt", "waist", "of the Eagle", "A broad leather belt marked with Warsong runes. It never quite fits, and never falls off.", "leather")],
        xp=1020, gold=4080, span=3))

    # ============================== CAPTAIN KORVASH (Mor'shan Rampart gate) ==============================
    G = "nb_rampart_captain"
    a(Q("nb_pickets_past_the_wall", "Pickets Past the Wall", G, 17,
        ("The Rampart is the Horde's wall against the Kaldorei, and it's a wall with a very thin side. "
         "Sentinel Pickets and Archers hold the strip just north of it, firing at anyone who gets near the "
         "gate. Korvash wants the strip cleared. He's tired of being polite."),
        [kill("Sentinel Picket", 5), kill("Sentinel Archer", 3)],
        ("The pickets hold the line. The archers cover them from the cliffs. Take the archers first if you "
         "can. Don't be proud."),
        ("The strip's quiet. For now. They'll send more. They always do. Take this."),
        [R(17, "Rampart Guard's Mail Hauberk", "chest", "of the Bastion", "Heavy mail edged with the Rampart's old iron. It's stopped bigger things.", "mail"),
         R(17, "Gatebreaker's Spear", "main_hand", "of the Soldier", "A long spear taken from a night elf picket. The balance is annoyingly perfect.", "polearm"),
         R(17, "Korvash's Gate-Ring", "ring", "of the Bear", "A thick iron ring. It's cold to touch and warms in a fight.")],
        nxt="nb_signal_horns"))
    a(Q("nb_signal_horns", "Signal Horns", G, 18,
        ("Every Sentinel Picket carries a signal horn: one blast and the whole forest answers. Korvash wants "
         "them silenced before the Kaldorei figure out how thin the Rampart really is."),
        [fetch("sentinel_signal_horn", 5)],
        ("Cut them off their belts. Quick, before they sound them. Bring me five."),
        ("Five horns. Five fewer calls for help. That's a good day. Take this."),
        [R(18, "Silencer's Soft-Soled Boots", "feet", "of the Assassin", "Quiet boots in dark leather. You'll startle people.", "leather"),
         R(18, "Horn-Bearer's Cloak", "back", "of the Falcon", "A grey cloak with a horn-shaped clasp. It makes a small, sad hooting in the wind.", "cloth"),
         R(18, "Korvash's Brass Knuckles", "main_hand", "of the Champion", "A pair of brass knuckles, heavy and ugly. They suit the captain.", "fist_weapon")],
        nxt="nb_moonspeakers"))
    a(Q("nb_moonspeakers", "Moonspeakers", G, 19,
        ("Behind the pickets stand Moonspeakers, night elf priestesses who call down light on anyone who "
         "falls. They're the reason the pickets keep coming back. Take them out and the line breaks."),
        [kill("Sentinel Moonspeaker", 4)],
        ("They stay in the back, glowing. Close on them quickly. They run if you wait."),
        ("The line's breaking. That's what we've been waiting for. Take this, with the Rampart's thanks."),
        [R(19, "Moonspeaker's Silver Circlet", "head", "of the Restorer", "A thin silver circlet, cold as moonlight. It makes you feel watched.", "cloth"),
         R(19, "Lunar-Etched Wristwraps", "wrist", "of the Prophet", "Cloth wraps marked with crescent moons. They soothe more than they should.", "cloth"),
         R(19, "Moonlit Dagger", "main_hand", "of the Assassin", "A narrow silver dagger that glows faintly. It's beautiful and wicked.", "dagger")],
        nxt="nb_warden_ilthae"))
    a(Q("nb_warden_ilthae", "Warden Ilthae", G, 20,
        ("The Sentinels' commander at the wall is Warden Ilthae, an old, steady, silver-haired woman who "
         "hasn't lost a skirmish in twenty years. Korvash respects her. He'd still like her dead."),
        [boss("Warden Ilthae"), kill("Sentinel Picket", 5)],
        ("She's got a glaive, a bad temper and no fear. Don't fight her in the open. Don't fight her at all, "
         "if you can avoid it. But you can't."),
        ("Ilthae's dead. The strip is ours. Take this, and may the wall hold a little longer."),
        [R(20, "Ilthae's Silverleaf Helm", "head", "of the Bastion", "A helm of silver-leafed mail. It's too light for its strength.", "mail"),
         R(20, "Warden's Moonglaive", "main_hand", "of the Gladiator", "A two-handed glaive with a curved blade. It sings in the moonlight.", "polearm"),
         R(20, "Sentinel's Cloak of Moonwool", "back", "of the Whale", "A soft grey cloak. It's warmer than it looks.", "cloth"),
         R(20, "Gatekeeper's Medal", "neck", "of the Soldier", "A medal for holding the Rampart. It's heavy.")],
        xp=1280, gold=4800, span=3))

    # ============================== HUNTRESS ZAN'ULA (Dry Hills) ==============================
    G = "nb_dryhills_huntress"
    a(Q("nb_feathers_on_the_wind", "Feathers on the Wind", G, 19,
        ("The Dry Hills belong to the Witchwings, harpies who've learned a few tricks from somewhere dark. "
         "Zan'ula tracks them for a living. She'd like fewer of them to track."),
        [kill("Witchwing Harpy", 6)],
        ("They fly low over the ridges and strike from behind. Keep your back to a hill and you'll be fine."),
        ("Good. Quiet in the hills. For a day or so. Take this."),
        [R(19, "Zan'ula's Hunter-Leathers", "chest", "of the Eagle", "Hide leathers dyed to match the hills. It's practically invisible.", "leather"),
         R(19, "Witchwing-Feather Cloak", "back", "of the Falcon", "A cloak trimmed with witchwing feathers. It makes you feel lighter.", "cloth"),
         R(19, "Hillcrest Hunting Bow", "ranged", "of the Marksman", "A bow of pale hillwood. Light, strong and quiet.", "bow")],
        nxt="nb_hexed_totems"))
    a(Q("nb_hexed_totems", "Hexed Totems", G, 20,
        ("The Witchwing Windcallers carve hex-totems and hang them in the high rocks. Zan'ula doesn't know "
         "what they do, only that she dreams badly near them. She'd like them taken down."),
        [fetch("witchwing_hex_totem", 5), kill("Witchwing Windcaller", 3)],
        ("Pull the totems from the Windcallers. Don't look at them for long."),
        ("Mm. They feel wrong, even in a bag. I'll burn them. Thank you. Take this."),
        [R(20, "Hex-Breaker's Gloves", "hands", "of the Seer", "Cloth gloves stitched with protective sigils. They itch if a hex is near.", "cloth"),
         R(20, "Totem-Smasher's Mace", "main_hand", "of the Squire", "A heavy mace with a stone head. It's good at breaking things that stare back.", "mace_1h"),
         R(20, "Stormfeather Pendant", "neck", "of the Prophet", "A harpy-feather pendant. It trembles in a rising wind.")],
        nxt="nb_hillcrest_stalkers"))
    a(Q("nb_hillcrest_stalkers", "Hillcrest Stalkers", G, 20,
        ("Hillcrest Stalkers have been hunting the trail between the hills. They're patient, grey and "
         "cunning. Zan'ula wants a dozen pelts and the hills quiet again."),
        [kill("Hillcrest Stalker", 6)],
        ("Stalkers wait on the high ledges. Look up before you walk under a ridge."),
        ("Good pelts. I'll sell the rest at the Crossroads. Take this."),
        [R(20, "Stalker-Pelt Leggings", "legs", "of the Tiger", "Grey fur leggings that muffle your steps. They're warmer than you'd like.", "leather"),
         R(20, "Hunter's Quick-Draw Crossbow", "ranged", "of the Hunt", "A light crossbow with a snap-draw lever. It's very quick.", "crossbow"),
         R(20, "Ridgewalker's Boots", "feet", "of the Monkey", "Stout boots for rough ridges. Your ankles will thank you.", "leather")],
        nxt="nb_serena_bloodfeather"))
    a(Q("nb_serena_bloodfeather", "Serena Bloodfeather", G, 20,
        ("Serena Bloodfeather leads the Witchwings. She has an old blood-feud with the Horde and a long "
         "memory. Zan'ula has tracked her for years and never gotten close. You might. You'll certainly try."),
        [boss("Serena Bloodfeather"), kill("Witchwing Slayer", 4)],
        ("She flies in at the end of a long hunt. Slayers first, always. If Serena sees you, run to the "
         "nearest ridge and fight there."),
        ("Serena's dead. The hills are quiet. I can't believe it. Take this, with a hunter's thanks."),
        [R(20, "Serena's Bloodfeather Mantle", "shoulder", "of the Eagle", "Crimson feathers stitched to leather. It's gaudy and fierce.", "leather"),
         R(20, "Bloodfeather Talon-Blade", "main_hand", "of the Assassin", "A curved talon-dagger from Serena's own hand. It's sharp as a prayer.", "dagger"),
         R(20, "Windcaller's Hex-Ring", "ring", "of the Sorcerer", "A ring of black feather and silver. It tingles when you lie."),
         R(20, "Matron's Hunt-Bow", "ranged", "of the Hunt", "A long bow strung with harpy sinew. It sings when you draw.", "bow")],
        xp=1260, gold=4800, span=3))

    # ============================== EARTHCALLER ROHNA (Serena's Hollow) ==============================
    G = "nb_hollow_shaman"
    a(Q("nb_roost_raiders", "Roost Raiders", G, 17,
        ("Serena's Hollow is a cliff-gorge that winds up to a harpy roost, and the harpies who live there "
         "don't love visitors. Rohna is an earthcaller, a spirit-speaker, and she can feel the roost "
         "crying out. It's a bad cry. She wants it quieted."),
        [kill("Roost Bonepicker", 5, zone=HOLLOW)],
        ("Go in through the cave mouth. Bonepickers hold the lower nests. They're small, mean, and love "
         "the taste of tauren."),
        ("Better. The earth is calmer. Take this, with the spirits' thanks."),
        [R(17, "Earthcaller's Woven Vest", "chest", "of the Whale", "Woven roots and hide. It smells like the first rain.", "leather"),
         R(17, "Gorge-Climber's Gloves", "hands", "of the Monkey", "Thick grippy gloves. They'll hold you on any cliff.", "leather"),
         R(17, "Hollow-Guard's Spear", "main_hand", "of the Squire", "A long spear for reaching nests. It also reaches harpies.", "polearm")],
        nxt="nb_down_from_the_roost"))
    a(Q("nb_down_from_the_roost", "Down from the Roost", G, 17,
        ("The harpies line their nests with down. Fine, white, and warm. Rohna's totem-carvers use it in "
         "their rites. She'd like six handfuls, and no more harpies in her sleep."),
        [fetch("harpy_roost_down", 6), kill("Harpy Sky-Sentry", 3, zone=HOLLOW)],
        ("Pull the down from the nests. Mind the sentries; they watch from the high ledges."),
        ("Soft as a promise. Thank you. The spirits will be pleased. Take this."),
        [R(17, "Feather-Light Cloak", "back", "of the Eagle", "A cloak lined with soft down. It weighs almost nothing.", "cloth"),
         R(17, "Rohna's Totem-Charm", "neck", "of the Seer", "A small carved totem on a cord. It hums when spirits are near."),
         R(17, "Down-Stuffed Belt", "waist", "of the Whale", "A thick cloth belt. It's lighter than it looks, and warm.", "cloth")],
        nxt="nb_windcallers_perch"))
    a(Q("nb_windcallers_perch", "The Windcaller's Perch", G, 18,
        ("High in the gorge sits a perch where Windcaller Skreeva commands the winds that blow the harpies "
         "up and down the cliff. Rohna says the winds listen to her. She'd rather they listened to someone "
         "else."),
        [boss("Windcaller Skreeva", zone=HOLLOW), kill("Harpy Windcaller", 3, zone=HOLLOW)],
        ("She stands on the east ledge, above the middle of the gorge. Her Windcallers keep the air thick. "
         "Take them first, then her."),
        ("Skreeva's dead. The winds are quiet. I can hear them breathing. Take this."),
        [R(18, "Skreeva's Wind-Caller Robe", "chest", "of the Sorcerer", "A pale cloth robe that lifts in the faintest breeze.", "cloth"),
         R(18, "Perch-Warden's Totem", "off_hand", "of the Restorer", "A small wind-totem of grey stone. It hums softly.", "totem"),
         R(18, "Windcaller's Feather-Ring", "ring", "of the Prophet", "A ring of woven feather and silver wire. It's weightless.")],
        nxt="nb_harpy_matriarch"))
    a(Q("nb_harpy_matriarch", "The Harpy Matriarch", G, 20,
        ("At the top of the gorge sits the roost, a great bowl of nests, and in the centre of it, the "
         "Matriarch, mother of every harpy in the hills. Rohna says her cry is the one the earth keeps "
         "answering. End it, and the hollow will be quiet."),
        [boss("Harpy Matriarch", zone=HOLLOW), kill("Harpy", 5, zone=HOLLOW)],
        ("She won't leave the nest. She'll call every harpy in the roost the moment she sees you. Don't "
         "fight her with the whole flock watching."),
        ("The Matriarch's dead. The roost is silent, and the earth is quiet. I'll sing the spirits home. "
         "Take this, and my thanks."),
        [R(20, "Matriarch's Down-Mantle", "shoulder", "of the Restorer", "A soft white mantle woven from the Matriarch's own down. It hums with a lullaby.", "cloth"),
         R(20, "Roost-Breaker's Maul", "main_hand", "of the Gladiator", "A heavy two-handed maul with a nest-twig handle. It's rough, but it hits.", "mace_2h"),
         R(20, "Gorge-Warden's Greaves", "legs", "of the Bastion", "Mail greaves with feathered trim. They keep you steady on a cliff.", "mail"),
         R(20, "Earthcaller's Eagle-Eye Amulet", "neck", "of the Eagle", "A carved eagle of grey stone. Its eyes glow faintly when something circles above.")],
        xp=1300, gold=4800, span=3))
    return A


def main():
    Qs = quests()
    out = []
    ids = set()
    for q in Qs:
        assert q["quest_id"] not in ids, q["quest_id"]
        ids.add(q["quest_id"])
        rewards = q.pop("rewards")
        q["unique_item_defs"] = rewards
        q["gear_reward_gear_level"] = max(r["item_level"] for r in rewards)
        if max(r["item_level"] for r in rewards) >= 15:
            q["gear_reward_rarity"] = "rare"
        out.append(q)
    for q in out:
        n = q["next_quest_id"]
        assert n is None or n in ids, (q["quest_id"], n)
    names = [d["name"] for q in out for d in q["unique_item_defs"]]
    assert len(names) == len(set(names)), [n for n in names if names.count(n) > 1]
    OUT.write_text(json.dumps({"quests": out}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("northern barrens hub quests:", len(out), "items:", sum(len(q["unique_item_defs"]) for q in out))


if __name__ == "__main__":
    main()
