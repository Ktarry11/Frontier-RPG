#!/usr/bin/env python3
"""Hidden sellers, hidden caches and hidden paths (idempotent).

    PYTHONPATH=. python3 tools/build_secrets.py

Kyle, 14 Nov 2026: "Secret vendors... think of them like.... Grim Dawn hidden goodies!!!" and
"exploration is rewarded. Like pathways on maps that look like they can't be walked through, but
they can." See world/secrets.py for how a secret works at runtime.

Writes:
  data/world/secrets.json         every secret place (read by world/secrets.py)
  data/items/secret_uniques.json  the one-of-a-kind items hidden sellers carry ("unique:<id>")
  data/npcs/vendors.json          the hidden sellers themselves ("hidden": true, no map icon)

AUTHORED secrets are written out by hand below. Generated ones (glades cut into rock and trees,
islands with a ford, rooms in cave walls) come from data/world/secret_candidates.json, which
tools/find_secret_pockets.py writes.

Kyle asked not to be told where any of them are. Keep it that way in commit messages and replies:
counts, never places.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from build_durotar_content import make  # noqa: E402

UNIQUES_PATH = ROOT / "data/items/secret_uniques.json"
SECRETS_PATH = ROOT / "data/world/secrets.json"
VENDORS_PATH = ROOT / "data/npcs/vendors.json"


def price(ilvl, rarity):
    return int(ilvl * ilvl * (60 if rarity == "rare" else 140))


def unique(uid, name, slot, suffix, ilvl, flavor, rarity="rare", **kw):
    d = make(name, slot, suffix, ilvl, flavor, rarity=rarity, **kw)
    d["price"] = price(ilvl, rarity)
    return uid, d


# ---------------------------------------------------------------------------------------------
# AUTHORED
# ---------------------------------------------------------------------------------------------
#: Kyle, 14 Nov: "I do want 1 specifically in razor hill hidden behind a building so I can test
#: it. Let him sell a few potential rare weapons. Like lvl 9 to 12." Item levels 12-15 put the
#: required levels at 9-12.
RAZOR_HILL_UNIQUES = [
    unique("rh_quartermasters_mistake", "Quartermaster's Mistake", "main_hand", "of the Tiger", 12,
           "Logged as scrap. It isn't.", weapon_type="axe_1h"),
    unique("rh_sandpit_longbow", "Sandpit Longbow", "ranged", "of the Marksman", 13,
           "Strung with something that isn't sinew, and better for it.", weapon_type="bow"),
    unique("rh_gravel_tongue", "Gravel-Tongue", "ranged", "of Fiery Wrath", 13,
           "It mutters when it's warm. It's always warm.", weapon_type="wand"),
    unique("rh_thornjaw_maul", "Thornjaw Maul", "main_hand", "of the Bear", 14,
           "Somebody hammered raptor teeth into the head and never said why.", weapon_type="mace_2h"),
    unique("rh_ironbark_quarterstaff", "Ironbark Quarterstaff", "main_hand", "of the Owl", 14,
           "Cut from a tree that grew on the wrong side of the Barrens.", weapon_type="staff"),
    unique("rh_kneecapper", "Kneecapper", "main_hand", "of the Assassin", 15,
           "Short, ugly and very persuasive.", weapon_type="dagger"),
    unique("rh_barracks_door", "The Barracks Door", "off_hand", "of the Bulwark", 15,
           "Taken off its hinges one night. Nobody has noticed the draught.", weapon_type="shield"),
]

AUTHORED_VENDORS = [{
    "vendor_id": "secret_razorhill_fence",
    "name": "Rivet Nackle",
    "zone": "Razor Hill", "spot": (30, 10),
    "race": "goblin", "gender": "male", "appearance_variant": 3,
    "greeting": "Keep your voice down. The quartermaster thinks all of this went in the river. "
                "It didn't, and now it's yours, if your coin's good.",
    "uniques": RAZOR_HILL_UNIQUES,
    "supplies": ["healing_potion_minor", "sturdy_arrows"],
}]

#: The other hidden sellers. Each stands in a spot tools/find_secret_pockets.py found in its town,
#: behind a building if the town has one and in a hidden room if not. Two trades' worth of recipes
#: sold nowhere else, and three one-of-a-kind items at the town's level.
#:   (id, town, name, race, gender, greeting, [trades], [(item, slot, suffix, kind, type, flavor)])
SELLERS = [
    # ---- people living deep inside the hidden zones (world/hidden_zones.py). Kyle: "I WANT to be
    # rewarded for exploring." A secret inside a secret.
    # ---- the frontier zones, a secret inside a secret inside a secret. Kyle: "put EXTRA care into
    # frontier zones. They carry the name of the game." Their shelves are all epic.
    ("secret_hz_root_seedkeeper", "The World-Root Hollow", "The Seed-Keeper", "night_elf", "female",
     "You found the tree, and the hollow under it, and now the knot in the roots where I keep the "
     "seeds. Nobody's done all three. Take your time choosing. These grew a long while.",
     ["herbalism", "alchemy", "leatherworking"],
     [("Seed of the First Grove", "neck", "of the Restorer", "armor", None, "It's warm, and it's trying to grow."),
      ("World-Root Longbow", "ranged", "of the Sharpshooter", "weapon", "bow", "Strung with a root as fine as hair. It never slackens."),
      ("Barkskin Jerkin of the Hollow", "chest", "of the Beast", "armor", "leather", "Grown on the wearer, they say. Slowly."),
      ("Amberglow Staff", "main_hand", "of the Invoker", "weapon", "staff", "A drop of sap at its crown that never stops glowing.")]),
    ("secret_hz_vault_scribe", "The Palimpsest Vault", "The Unfinished Scribe", "forsaken", "male",
     "Oh. A reader. I haven't had a reader in... I couldn't tell you. I've been copying the same page. "
     "Buy something. Then go, before I start copying you.",
     ["inscription", "enchanting", "tailoring"],
     [("Robes of the Unfinished Page", "chest", "of the Archmage", "armor", "cloth", "The hem is still being written."),
      ("Scribe's Ruled Gauntlets", "hands", "of the Juggernaut", "armor", "plate", "Every knuckle ruled with a straight line."),
      ("Palimpsest Codex", "off_hand", "of the Sorcerer", "weapon", "tome", "Three books, one over the other, and all of them true."),
      ("Ink-Drinker", "main_hand", "of the Assassin", "weapon", "dagger", "It stains whatever it cuts. Permanently.")]),
    ("secret_hz_glass_vessa", "The Glasswaste", "Vessa Glassmouth", "blood_elf", "female",
     "You got past the kilns AND found the crack in the wall? Then you've earned a look at what "
     "I've made from the glass. Don't tell Durek where I live.",
     ["jewelcrafting", "blacksmithing"],
     [("Fused Glass Longblade", "main_hand", "of the Gladiator", "weapon", "sword_2h", "Glass, folded like steel. It sings when it cuts."),
      ("Glassblower's Leggings", "legs", "of the Sorcerer", "armor", "cloth", "Scorched at the knees and proud of it."),
      ("Kilnscale Hauberk", "chest", "of the Champion", "armor", "mail", "Little plates of glass, sewn on one by one.")]),
    ("secret_hz_pines_osric", "The Weeping Pines", "Osric the Unwept", "human", "male",
     "Nobody comes in here who isn't lost or looking. You don't look lost. What are you looking for?",
     ["leatherworking", "tailoring"],
     [("Fogwalker's Cloak", "back", "of the Wolf", "armor", None, "Grey wool that drinks the fog and gives it back."),
      ("Pine-Ghost Bow", "ranged", "of the Sharpshooter", "weapon", "bow", "Strung with a widow's hair. Don't ask whose."),
      ("Mereside Boots", "feet", "of the Physician", "armor", "leather", "Waterproof. That's rarer out here than you'd think.")]),
    ("secret_hz_caravan_amun", "The Buried Caravan", "Amun-Who-Stayed", "human", "male",
     "I was the caravan's last guard. I'm still guarding it. Buy something, and I'll pretend I didn't see you.",
     ["blacksmithing", "engineering"],
     [("Caravan Guard's Kopesh", "main_hand", "of the Vanquisher", "weapon", "sword_1h", "Sand-polished for three hundred years."),
      ("Sun-Bleached Turban", "head", "of the Invoker", "armor", "cloth", "It keeps the head cool, and the thoughts clear."),
      ("Duneplate Sabatons", "feet", "of the Defender", "armor", "plate", "Every step leaves a perfect print.")]),
    ("secret_brill_grisle", "Brill", "Mother Grisle", "forsaken", "female",
     "You found the back of the town hall. Most people never think to look behind anything. "
     "Buy something before you start telling people.",
     ["tailoring", "leatherworking"],
     [("Grisle's Stitched Mantle", "shoulder", "of the Owl", "armor", "cloth", "Stitched from three other mantles. You can see the seams if you look."),
      ("Embalmer's Scalpel", "main_hand", "of the Assassin", "weapon", "dagger", "Very sharp. Very clean. Mostly."),
      ("Bonepicker Gloves", "hands", "of the Monkey", "armor", "leather", "The fingertips are worn through from careful work.")]),
    ("secret_uc_edwin", "Undercity", "Quiet Edwin", "forsaken", "male",
     "I sell to people who know where to stand. You know where to stand. That's all the introduction we need.",
     ["engineering", "blacksmithing"],
     [("Sewer-Lantern Staff", "main_hand", "of the Sorcerer", "weapon", "staff", "The lantern still lights. Nobody has ever filled it."),
      ("Rat King's Buckler", "off_hand", "of the Bulwark", "weapon", "shield", "Gnawed round the rim, and none the weaker for it."),
      ("Drainwalker Boots", "feet", "of the Tiger", "armor", "leather", "They never quite dry out. They never quite need to.")]),
    ("secret_org_gashna", "Orgrimmar", "Gashna Two-Coins", "orc", "female",
     "The Warchief's quartermasters don't like what I sell, so I sell it here, quietly. "
     "You didn't see me and I didn't see you.",
     ["blacksmithing", "leatherworking"],
     [("Gashna's Spare Axe", "main_hand", "of the Champion", "weapon", "axe_2h", "She calls it her spare. Nobody has seen the first one."),
      ("Cleft-Shadow Hood", "head", "of the Bandit", "armor", "leather", "Smells of incense and bad decisions."),
      ("Hammer of Old Debts", "main_hand", "of the Squire", "weapon", "mace_1h", "Every dent is somebody who paid late.")]),
    ("secret_xroads_tazzle", "Crossroads", "Teeny Tazzle", "goblin", "male",
     "Customs, tariffs, inspections. I skip all of that and pass the savings on to you.",
     ["engineering", "jewelcrafting"],
     [("Tariff-Dodger's Boomstick", "ranged", "of the Marksman", "weapon", "gun", "Fires straight, mostly. Sounds expensive every time."),
      ("Bribe-Lined Vest", "chest", "of the Eagle", "armor", "mail", "There are coins sewn into the lining. Don't spend them."),
      ("Caravan Ledger", "off_hand", "of Intellect", "weapon", "tome", "Every column adds up to somebody else's loss.")]),
    ("secret_taurajo_brannoch", "Camp Taurajo", "Old Hoof Brannoch", "tauren", "male",
     "I carve what the trading post won't buy. Some of it's better than what they do sell.",
     ["woodworking", "leatherworking"],
     [("Plainsrunner Longbow", "ranged", "of the Hunt", "weapon", "bow", "Carved by hand, by somebody who has missed before and didn't like it."),
      ("Kodo-Hide Bracers", "wrist", "of the Bear", "armor", "mail", "Stiff for a month, then never again."),
      ("Brannoch's Walking Stick", "main_hand", "of the Elder", "weapon", "staff", "He says he doesn't need it any more. He's lying.")]),
    ("secret_ratchet_lissa", "Ratchet", "Lissa Undertow", "goblin", "female",
     "Salvage rights are a matter of who gets there first. I got there first.",
     ["engineering", "tailoring"],
     [("Wreck-Diver's Goggles", "head", "of the Falcon", "armor", "mail", "The left lens has a crack shaped like a shark."),
      ("Barnacled Cutlass", "main_hand", "of the Duelist", "weapon", "sword_1h", "Six weeks on the seabed and it still holds an edge."),
      ("Brine-Soaked Sash", "waist", "of the Prophet", "armor", "cloth", "Salt has worked into every thread. It hums at high tide.")]),
    ("secret_splinter_grokka", "Splintertree Post", "Grokka the Quiet", "orc", "male",
     "The lumber bosses think I quit. I didn't. I just moved round the back.",
     ["woodworking", "enchanting"],
     [("Felled Ancient's Branch", "main_hand", "of the Restorer", "weapon", "staff", "Cut from a tree that was older than the Horde. It hasn't forgiven anyone."),
      ("Splintered Warboard", "off_hand", "of the Defender", "weapon", "shield", "Made of the same planks as the palisade."),
      ("Sawdust Leggings", "legs", "of the Boar", "armor", "leather", "They never stop shedding.")]),
    ("secret_astranaar_sevalis", "Astranaar", "Sevalis Moonwhisper", "night_elf", "female",
     "The Sentinels would call this smuggling. I call it keeping old things in the right hands.",
     ["enchanting", "jewelcrafting"],
     [("Moonsilver Circlet", "head", "of the Seer", "armor", "cloth", "Cold even in sunlight."),
      ("Glaive of the Quiet Grove", "main_hand", "of the Tiger", "weapon", "sword_1h", "Older than Astranaar. Possibly older than the trees."),
      ("Owlfeather Cloak", "back", "of the Owl", "armor", None, "Every feather was given, not taken. She's sure of it.")]),
    ("secret_sepulcher_ashmund", "The Sepulcher", "Brother Ashmund", "forsaken", "male",
     "Grave goods. Everyone assumes they stay buried. I don't make that assumption.",
     ["leatherworking", "tailoring"],
     [("Ashmund's Burial Wraps", "chest", "of the Necromancer", "armor", "cloth", "Somebody was buried in these. They won't be needing them."),
      ("Gravewarden's Spade", "main_hand", "of Strength", "weapon", "polearm", "It digs. It also does the other thing."),
      ("Coffin-Nail Ring", "ring", "of Stamina", "armor", None, "Bent into a loop by somebody with very strong hands.")]),
    ("secret_tarrenmill_calloway", "Tarren Mill", "Widow Calloway", "forsaken", "female",
     "Mind the stairs. Nobody else uses them, which is the whole point of them.",
     ["tailoring", "blacksmithing"],
     [("Calloway's Mourning Veil", "head", "of the Invoker", "armor", "cloth", "Black lace, very fine, very old."),
      ("Millstone Crusher", "main_hand", "of the Bear", "weapon", "mace_2h", "Part of the old mill. The rest of it is still in the river."),
      ("Hillsbrad Harvest Gloves", "hands", "of the Physician", "armor", "leather", "Green-stained to the wrist.")]),
    ("secret_hammerfall_mog", "Hammerfall", "Mog Halfear", "orc", "male",
     "Arathi's full of things nobody's claimed. I claim them. Then I sell them.",
     ["blacksmithing", "leatherworking"],
     [("Stromgarde Trophy Blade", "main_hand", "of the Gladiator", "weapon", "sword_2h", "Pulled from a wall in Stromgarde. The wall didn't want to let go."),
      ("Ogre-Tooth Pauldrons", "shoulder", "of the Soldier", "armor", "mail", "The teeth are real. The ogre was not consulted."),
      ("Highland Stalker's Bow", "ranged", "of the Sharpshooter", "weapon", "bow", "Strung tight enough to hum in the wind.")]),
    ("secret_bootybay_vell", "Booty Bay", "Pocket Vell", "goblin", "female",
     "Everything in Booty Bay's for sale. The good stuff's just harder to find.",
     ["engineering", "jewelcrafting"],
     [("Smuggler's Hand Cannon", "ranged", "of the Marksman", "weapon", "gun", "Small enough to hide, loud enough to regret."),
      ("Revilgaz's Missing Ring", "ring", "of the Tiger", "armor", None, "The Baron says he never lost a ring. Vell says otherwise."),
      ("Bilge-Rat Jerkin", "chest", "of the Bandit", "armor", "leather", "Waterproof, smell-proof, conscience-proof.")]),
    ("secret_gromgol_zuni", "Grom'gol", "Zuni Hushfang", "troll", "female",
     "The jungle gives up its treasures to the patient. I'm patient. You pay.",
     ["leatherworking", "woodworking"],
     [("Hushfang's Fetish Staff", "main_hand", "of the Wellspring", "weapon", "staff", "The shrunken thing on top nods along when you talk."),
      ("Raptor-Scale Leggings", "legs", "of the Monkey", "armor", "leather", "Still warm. Don't ask."),
      ("Ziggurat Ward", "off_hand", "of the Warder", "weapon", "shield", "Carved stone, carried by somebody very strong once.")]),
    ("secret_freewind_talo", "Freewind Post", "Talo Skyhide", "tauren", "male",
     "The wind carries off a lot of things. I find where it puts them down.",
     ["leatherworking", "woodworking"],
     [("Windcaught Mantle", "shoulder", "of the Eagle", "armor", "mail", "Found on a spire nobody can climb. Talo won't say how."),
      ("Needlepoint Spear", "main_hand", "of the Spearhead", "weapon", "polearm", "Long enough to reach across a rope bridge, and he has."),
      ("Skyhide Wristwraps", "wrist", "of the Physician", "armor", "leather", "Soft as a cloud and about as warm.")]),
    ("secret_stw_fizzby", "Steamwheedle Port", "Fizzby Crankloot", "goblin", "male",
     "Off the books, off the docks, off the record. Take your pick.",
     ["engineering", "blacksmithing"],
     [("Crankloot's Overclocked Rifle", "ranged", "of the Sharpshooter", "weapon", "gun", "Runs hot. Runs very hot."),
      ("Gearbox Gauntlets", "hands", "of the Juggernaut", "armor", "plate", "Every knuckle is a cog."),
      ("Dune-Sealed Robes", "chest", "of the Prophet", "armor", "cloth", "Not one grain of sand gets in. Fizzby guarantees it.")]),
    ("secret_echo_zenji", "Echo Isles", "Mama Zenji", "troll", "female",
     "The spirits told me you'd come round the back. They don't usually bother telling me anything.",
     ["leatherworking", "tailoring"],
     [("Zenji's Bone Charm Staff", "main_hand", "of the Owl", "weapon", "staff", "Every bone on it belonged to somebody who owed her."),
      ("Tidecaller's Sandals", "feet", "of the Seer", "armor", "cloth", "Damp. Always damp."),
      ("Darkspear Throwing Glaive", "ranged", "of the Monkey", "weapon", "thrown", "It comes back. Usually.")],
     {"meals": [("Deepwater Brine Stew", "Slow-cooked the way Zenji's grandmother did it, which is to say for far longer than you'd think."),
                ("Reef-Smoked Mackerel", "Smoked over driftwood and kelp until it tastes of the whole sea at once."),
                ("Zenji's Salted Roe", "A spoonful is plenty. Two is showing off.")]}),
    ("secret_onyx_dagna", "Onyxhollow", "Dagna Coalbeard", "dwarf", "female",
     "My cousin runs the forge. I run what falls off the back of it.",
     ["blacksmithing", "jewelcrafting"],
     [("Fell-Off-the-Forge Warhammer", "main_hand", "of the Vanquisher", "weapon", "mace_2h", "It fell off the forge. Onto a cart. Which drove here."),
      ("Coalbeard's Heirloom Plate", "chest", "of the Bastion", "armor", "plate", "Three generations of Coalbeards wore it. Two survived."),
      ("Black Hollow Signet", "ring", "of the Champion", "armor", None, "Onyx, set in something darker.")]),
    ("secret_kael_lirael", "Kael's Bastion", "Lirael Sunstrand", "blood_elf", "female",
     "The Codex indexes everything. Almost everything. What it missed ended up with me, and I'd rather it stayed that way.",
     ["enchanting", "tailoring"],
     [("Unindexed Spellblade", "main_hand", "of Arcane Wrath", "weapon", "sword_1h", "There's no entry for it in any catalogue. She checked."),
      ("Marginalia Gloves", "hands", "of the Sorcerer", "armor", "cloth", "Ink-stained. The ink moves."),
      ("Sunstrand Pendant", "neck", "of Intellect", "armor", None, "Warm when somebody lies to you.")]),
    # ---- more hidden sellers, so the creatures stay rare (Kyle: monsters "5% max")
    ("secret_durotar_grallik", "Durotar", "Hermit Grallik", "orc", "male",
     "I left Razor Hill because it got loud. If you found me, you're quiet enough to buy something.",
     ["leatherworking", "blacksmithing"],
     [("Scorpid-Tail Flail", "main_hand", "of the Tiger", "weapon", "mace_1h", "The barb still twitches in the heat."),
      ("Red Wastes Wraps", "wrist", "of the Monkey", "armor", "leather", "Sun-bleached and sand-scoured."),
      ("Hermit's Lantern Staff", "main_hand", "of the Owl", "weapon", "staff", "He reads by it. He doesn't read much.")]),
    ("secret_nbarrens_mirela", "Northern Barrens", "Mirela Sandsong", "tauren", "female",
     "The plains keep whatever travellers drop. I just walk along behind them.",
     ["woodworking", "leatherworking"],
     [("Thunderhoof Maul", "main_hand", "of the Bear", "weapon", "mace_2h", "Heavy enough to stop a kodo. It has."),
      ("Sandsong Shawl", "back", "of the Owl", "armor", None, "Woven from kodo hair and patience."),
      ("Plainswalker Boots", "feet", "of the Eagle", "armor", "mail", "Resoled six times and still going.")]),
    ("secret_sbarrens_snitch", "Southern Barrens", "Snitch Grimtooth", "goblin", "male",
     "Bael'dun had more in its vaults than the dwarves ever let on. Had, I said.",
     ["engineering", "blacksmithing"],
     [("Vault-Cracker Hammer", "main_hand", "of Strength", "weapon", "mace_1h", "Built for doors. Works on most things that aren't doors too."),
      ("Bael'dun Blunderbuss", "ranged", "of the Marksman", "weapon", "gun", "Dwarven make. Goblin improvements. Mostly improvements."),
      ("Borrowed Ironforge Belt", "waist", "of the Soldier", "armor", "plate", "Snitch says borrowed. Nobody's asked for it back.")]),
    ("secret_ashen_kyrenne", "Ashenvale East", "Kyrenne Shadowbark", "night_elf", "female",
     "The Horde cuts down the forest. I sell what it leaves behind to whoever finds me, and I don't ask which side they're on.",
     ["tailoring", "enchanting"],
     [("Felscorched Robe", "chest", "of Shadow Wrath", "armor", "cloth", "The hem is singed green and won't wash out."),
      ("Shadowbark Recurve", "ranged", "of the Hunt", "weapon", "bow", "Carved from a tree that died standing."),
      ("Satyrbane Glaive", "main_hand", "of the Champion", "weapon", "sword_1h", "Made for satyrs. It isn't fussy.")]),
    ("secret_needles_skyfeather", "Southern Thousand Needles", "Old Skyfeather", "tauren", "male",
     "Up here the only visitors are birds and fools. You don't look much like a bird.",
     ["leatherworking", "woodworking"],
     [("Mesa Runner's Jerkin", "chest", "of the Falcon", "armor", "leather", "Cut for climbing. Stitched for falling."),
      ("Spire-Climber Gloves", "hands", "of the Soldier", "armor", "mail", "Grip like a hawk's foot."),
      ("Skyfeather Totem", "ranged", "of the Elder", "weapon", "totem", "Carved from a spire that fell in a storm.")]),
    ("secret_flats_mabs", "The Shimmering Flats", "Grease Monkey Mabs", "goblin", "female",
     "Pit crews throw out better parts than most shops sell. I don't throw anything out.",
     ["engineering", "tailoring"],
     [("Racing Goggles", "head", "of the Falcon", "armor", "leather", "The salt never quite comes off the lenses."),
      ("Nitro-Boosted Boomstick", "ranged", "of the Sharpshooter", "weapon", "gun", "Mabs says it's perfectly safe. Mabs is missing two fingers."),
      ("Crash-Padded Leggings", "legs", "of the Bear", "armor", "mail", "Designed after the third crash. Tested on the fourth.")]),
    ("secret_tanaris_ahmiru", "Northern Tanaris", "Ahmiru Dustwalker", "troll", "male",
     "The desert buries everything in the end. I just get there before it's finished.",
     ["jewelcrafting", "leatherworking"],
     [("Sunscorched Khopesh", "main_hand", "of the Gladiator", "weapon", "sword_1h", "The grip is too hot to hold at noon. Hold it anyway."),
      ("Dune-Sealed Leggings", "legs", "of the Monkey", "armor", "leather", "Not one grain of sand gets in. Ahmiru guarantees it, loudly."),
      ("Sandworm Tooth Pendant", "neck", "of Stamina", "armor", None, "Big tooth. Bigger worm.")]),
    ("secret_nstv_ezra", "Northern Stranglethorn", "Ezra Blackpowder", "human", "male",
     "Booty Bay charges a landing fee. I don't have a landing, so I don't charge one.",
     ["engineering", "blacksmithing"],
     [("Smuggler's Hook Blade", "main_hand", "of the Duelist", "weapon", "sword_1h", "Good for rigging, better for arguments."),
      ("Powder-Burned Gauntlets", "hands", "of the Soldier", "armor", "mail", "Black to the elbow and proud of it."),
      ("Jungle-Run Musket", "ranged", "of the Marksman", "weapon", "gun", "Wrapped in oilcloth for the wet season, which is every season.")]),
    ("secret_cstv_jalu", "Central Stranglethorn", "Mama Jalu", "troll", "female",
     "The old temples are full of things the Gurubashi forgot. I remember them for them.",
     ["tailoring", "leatherworking"],
     [("Zandali Bone Fetish", "off_hand", "of the Necromancer", "weapon", "tome", "It rattles when nobody is moving it."),
      ("Jalu's Ritual Mask", "head", "of the Seer", "armor", "leather", "The eyes follow you. That's the point."),
      ("Gurubashi Throwing Axe", "ranged", "of the Monkey", "weapon", "thrown", "Balanced for a throw and a long walk to fetch it.")]),
    ("secret_arathiw_wren", "Arathi West", "Tobias Wren", "human", "male",
     "Stromgarde's quartermasters sold everything that wasn't nailed down. I bought the nails.",
     ["blacksmithing", "leatherworking"],
     [("Stromgarde Longsword", "main_hand", "of the Champion", "weapon", "sword_2h", "Old Stromgarde steel. They don't make it like this any more because there's nobody left to."),
      ("Highland Tabard Coat", "chest", "of the Soldier", "armor", "mail", "The crest has been unpicked. You can still see where it was."),
      ("Wren's Crossbow", "ranged", "of the Hunt", "weapon", "crossbow", "He says it's never missed. He says a lot of things.")]),
    ("secret_arathie_brakka", "Arathi East", "Brakka Coldwater", "orc", "female",
     "Ogres don't count their hoards. That's how I've lived this long.",
     ["blacksmithing", "leatherworking"],
     [("Ogre-Hide Belt", "waist", "of the Bear", "armor", "leather", "One belt. One very large ogre."),
      ("Boulderfist Club", "main_hand", "of Strength", "weapon", "mace_2h", "Two rocks and a tree. Ogre craftsmanship."),
      ("Coldwater Shield", "off_hand", "of the Defender", "weapon", "shield", "Still damp from the river she pulled it out of.")]),
    ("secret_spnorth_moll", "Silverpine North", "Gravedigger Moll", "forsaken", "female",
     "The dead don't need their boots. I've asked them, very politely.",
     ["leatherworking", "tailoring"],
     [("Dead Man's Boots", "feet", "of the Tiger", "armor", "leather", "Broken in. Thoroughly."),
      ("Pyrewood Shroud", "back", "of the Necromancer", "armor", None, "It smells faintly of smoke and somebody's grandmother."),
      ("Moll's Shovel Blade", "main_hand", "of Strength", "weapon", "polearm", "Sharpened on both edges, for reasons Moll keeps to herself.")]),
    ("secret_fenris_ferrin", "Fenris Isle", "Ferrin the Ferryless", "forsaken", "male",
     "I used to run a boat out here. Then the boat sank, and I stayed with it, mostly.",
     ["tailoring", "engineering"],
     [("Bloodmoon Charm", "neck", "of the Seer", "armor", None, "Red under any moon."),
      ("Fenris Keep Signet", "ring", "of the Champion", "armor", None, "The keep's seal. The keep doesn't need it any more."),
      ("Ferryman's Oar-Blade", "main_hand", "of the Breaker", "weapon", "polearm", "An oar, mostly. The rest is spite and an iron edge.")]),
    ("secret_hillse_tamsin", "Eastern Hillsbrad", "Hedgewitch Tamsin", "human", "female",
     "The Forsaken think I left. The Alliance thinks I'm dead. Both of those suit me fine.",
     ["tailoring", "enchanting"],
     [("Hedgewitch's Bramble Staff", "main_hand", "of the Restorer", "weapon", "staff", "Still sprouting. She keeps meaning to trim it."),
      ("Thornwoven Gloves", "hands", "of the Prophet", "armor", "cloth", "Prickly on the outside, kind on the inside."),
      ("Witch-Knot Amulet", "neck", "of Intellect", "armor", None, "Tied in a knot nobody else in Hillsbrad remembers how to tie.")]),
    ("secret_dk_grubbs", "Deathknell", "Grubbs the Digger", "forsaken", "male",
     "I dig graves. Sometimes I dig them up again. Don't look at me like that, it's honest work.",
     ["leatherworking", "blacksmithing"],
     [("Grubbs' Shovel", "main_hand", "of Strength", "weapon", "polearm", "Dug a lot of holes. Filled in most of them."),
      ("Burial Gloves", "hands", "of the Monkey", "armor", "leather", "Never wash them. Grubbs certainly doesn't."),
      ("Lantern of the Dug-Up", "off_hand", "of Intellect", "weapon", "tome", "A ledger of everyone he's dug up, and what they had on them.")]),
    ("secret_vot_kazzik", "Valley of Trials", "Kazzik the Runaway", "goblin", "male",
     "Don't tell the overseers I'm here. I'm supposed to be shovelling something somewhere.",
     ["engineering", "leatherworking"],
     [("Runaway's Wrench", "main_hand", "of the Tiger", "weapon", "mace_1h", "He took it when he ran. He says it was owed."),
      ("Shovelling Gloves", "hands", "of the Bear", "armor", "leather", "Never actually used for shovelling."),
      ("Spare Slingshot", "ranged", "of the Monkey", "weapon", "thrown", "For the boar that chased him in here.")]),
    ("secret_strand_kezz", "The Black Strand", "Saltjaw Kezz", "goblin", "female",
     "Everything on this beach washed up from somewhere. Some of it washed up from very deep.",
     ["engineering", "jewelcrafting"],
     [("Deepwreck Harpoon", "main_hand", "of the Spearhead", "weapon", "polearm", "Barbed for something much bigger than you."),
      ("Abyssal Diver's Helm", "head", "of the Juggernaut", "armor", "plate", "Brass and glass. The glass is cracked from the inside."),
      ("Kelp-Stained Cord", "waist", "of the Sorcerer", "armor", "cloth", "Still smells of low tide.")]),
    ("secret_cinder_varga", "Cinderwharf", "Ashfoot Varga", "orc", "female",
     "The wharf burns down every few years. I'm the one who sorts through what's left.",
     ["blacksmithing", "leatherworking"],
     [("Ashforged Greataxe", "main_hand", "of the Vanquisher", "weapon", "axe_2h", "Forged in a fire nobody lit on purpose."),
      ("Cinder-Proof Gauntlets", "hands", "of the Bastion", "armor", "plate", "She's put her hands in the fire to prove it. Twice."),
      ("Wharfwatcher's Rifle", "ranged", "of the Sharpshooter", "weapon", "gun", "Smoke-blackened and dead accurate.")]),
    ("secret_glitter_nim", "Glittervein", "Nim Copperbolt", "gnome", "male",
     "Everybody else dug for gold. I dug for the things the gold was sitting on.",
     ["jewelcrafting", "engineering"],
     [("Gem-Studded Pick", "main_hand", "of the Champion", "weapon", "axe_1h", "More gems in the handle than most mines have left."),
      ("Copperbolt's Loupe", "head", "of the Seer", "armor", "cloth", "Sees the flaw in every stone and most people."),
      ("Glittervein Band", "ring", "of the Eagle", "armor", None, "Cut from a seam that isn't on any map.")]),
    ("secret_saltspur_hewitt", "Saltspur Landing", "Old Barnacle Hewitt", "human", "male",
     "Fish don't care who wins the war. Neither do I, as long as you're buying.",
     ["leatherworking", "tailoring"],
     [("Hewitt's Gaff Hook", "main_hand", "of the Tiger", "weapon", "polearm", "Landed a shark with it once. The shark's still upset."),
      ("Oilskin Sou'wester", "head", "of the Eagle", "armor", "leather", "Keeps the rain off and the gossip in."),
      ("Net-Weaver's Gloves", "hands", "of the Owl", "armor", "cloth", "Fingerless, for knots.")]),
    ("secret_tempest_ilse", "Tempest Shallows", "Stormwatcher Ilse", "dwarf", "female",
     "I came to study the storm. The storm studied me back, so I stayed.",
     ["enchanting", "jewelcrafting"],
     [("Stormcaller's Rod", "main_hand", "of Spellstorm", "weapon", "staff", "The tip crackles before every storm. It's crackling now."),
      ("Lightning-Rod Pauldrons", "shoulder", "of the Falcon", "armor", "mail", "Not recommended in a thunderstorm. Ilse wears them anyway."),
      ("Tempest-Glass Pendant", "neck", "of the Sorcerer", "armor", None, "Glass made where lightning hit the sand.")]),
    ("secret_underdark_haldur", "The Crystalline Underdark", "Haldur Deepdelve", "dwarf", "male",
     "Down here nobody asks where things came from. That's the best thing about down here.",
     ["blacksmithing", "jewelcrafting"],
     [("Crystal-Edged Axe", "main_hand", "of the Tiger", "weapon", "axe_1h", "The edge is a crystal that grew there. Haldur swears it."),
      ("Deepdelve's Hauberk", "chest", "of the Soldier", "armor", "mail", "Three generations of Deepdelves. One very long tunnel."),
      ("Glowcap Lantern", "off_hand", "of the Prophet", "weapon", "tome", "Lit by mushrooms. Don't eat the lamp.")]),

]

#: SELLERS WHO ARE NOT PEOPLE - and only a few. Kyle, 14 Nov: "Only some of them are monsters though.
#: Maybe 5% max. They should feel unique not the norm." Keep these at one in twenty of all hidden sellers.
#: Kyle, 14 Nov: "vendors found in hidden areas DONT have to be traditional
#: sprites. Like, you can have a Naga vendor selling unique cooking recipes. Or a fire elemental with a
#: unique enchant... Or a rat that just squeaks at you and then opens its trade for something other
#: than gold. Don't be shy." Each stands in a hidden room in its zone, is drawn as the creature, and
#: (where "barter" is set) wants something other than coin.
#:   (id, zone, name, creature sprite, barter currency or None, greeting, uniques, extras)
#:   extras: {"meals": [(name, description)], "enchant": {...}, "trades": [...]}
CREATURE_SELLERS = [
    ("secret_uc_squeak", "Undercity", "Squeak", "rat_plague_1", ("cook_cheese", "Sharp Cheese", 3),
     "[A plague rat sits up on its haunches. It sniffs at your pack, then at you, and squeaks twice. "
     "It clearly wants the cheese.]",
     [("Gnawed Signet", "ring", "of the Monkey", "armor", None, "Somebody's seal ring. Somebody's teeth marks."),
      ("Sewer-Slick Slippers", "feet", "of the Owl", "armor", "cloth", "Slightly damp. Slightly chewed. Very comfortable."),
      ("A Very Good Stick", "ranged", "of Shadow Wrath", "weapon", "wand", "Squeak's favourite. It's giving it up for you, and that should mean something.")],
     {}),
    ("secret_sands_cinder", "The Abyssal Sands", "Cinder-That-Listens", "elemental_fire_2", ("crystal_emberglass", "Emberglass", 2),
     "[The fire leans toward you as you come in, the way a cat does.] Glass. Bring me glass that remembers "
     "burning, and I'll give you a little of my heat to carry.",
     [("Ashheart Mantle", "back", "of Fiery Wrath", "armor", None, "Warm on the coldest night. Uncomfortably warm on every other.")],
     {"enchant": {"id": "enchant_weapon_living_ember", "title": "Living Ember", "group": "weapon",
                  "describe": "Your attacks have a chance to set a living ember on the target, burning it for 70 fire damage.",
                  "chance": 18, "damage": 70, "level": 44, "skill": 225}}),
]

#: ISLANDS BAKED INTO A ZONE'S PAINTING. A painted zone cannot grow land at runtime, so these are real
#: landforms in the zone module (see its ISLANDS and FORDS, keys "secret_*"), baked; this only tells the
#: map to lie about them and puts a cache on each.  (zone, module, island key, ford key)
BAKED_ISLANDS = [
    # (zone, zone module, island centre and reach (cx, cy, r), ford polyline, ford width)
    ("Echo Isles", "tools.handbuilt_echo_isles", (23, 9, 9), [(24, 37), (23, 27), (22, 16)], 2.4),
    ("Echo Isles", "tools.handbuilt_echo_isles", (144, 148, 8), [(140, 119), (141, 130), (142, 141)], 2.4),
    ("Arathi East", "tools.handbuilt_arathi_east", (151, 10, 10), [(139, 33), (143, 26), (147, 18)], 2.4),
]


def _is_frontier(zone):
    try:
        reg = json.loads((ROOT / "data/world/hidden_zones.json").read_text(encoding="utf-8"))["zones"]
    except (OSError, ValueError, KeyError):
        return False
    return (reg.get(zone) or {}).get("kind") == "frontier"


def _hidden_doors():
    """[(hidden zone, (parent map, its portal x, y))] for every hidden zone whose door is a room in
    its parent's wall. (A door in a baked island is placed with that island.)"""
    out = []
    try:
        reg = json.loads((ROOT / "data/world/hidden_zones.json").read_text(encoding="utf-8"))["zones"]
    except (OSError, ValueError, KeyError):
        return out
    from tools.handbuilt_hidden_layers import PORTALS
    portals = dict(PORTALS)
    try:
        from tools.handbuilt_skull_zones import PORTALS as SKULL_PORTALS, ISLAND_DOORS
    except ImportError:
        SKULL_PORTALS, ISLAND_DOORS = {}, {}
    portals.update(SKULL_PORTALS)
    try:
        from tools.handbuilt_skull_zones import placed_doors
        placed = placed_doors()
    except ImportError:
        placed = {}
    for zname, info in sorted(reg.items()):
        if zname in ISLAND_DOORS or zname in placed or zname not in portals:
            continue
        out.append((zname, (info["parent"], *portals[zname])))
    return out


def _placed_door_secrets():
    """Doors placed by hand in a skull zone's own layout (behind its great tree): kind "behind",
    so the renderer draws the tree back over the door's glow."""
    try:
        from tools.handbuilt_skull_zones import placed_doors
        from tools.handbuilt_hidden_layers import PORTALS
    except ImportError:
        return []
    out = []
    for to, (parent, (x, y)) in sorted(placed_doors().items()):
        if to not in PORTALS:
            continue
        tx, ty = PORTALS[to]
        out.append({"id": "door_" + "".join(ch for ch in to.lower().replace(" ", "_") if ch.isalnum() or ch == "_"),
                    "zone": parent, "kind": "behind", "passage": [],
                    "area": [[x + dx, y + dy] for dx in (-2, -1, 0, 1, 2) for dy in (-3, -2, -1, 0)],
                    "mask": None, "cache": None, "vendor": None,
                    "door": {"x": x, "y": y, "to": to, "tx": tx, "ty": ty},
                    "found_text": "There's a hollow in the roots, and it goes down a very long way."})
    return out


def _island_door(zone, module, isle, centre, isle_at):
    """A door on a secret island, if a hidden zone's way in is meant to stand there: a dry tile
    near the middle, not the cache's, with dry ground two tiles north for coming back out."""
    try:
        from tools.handbuilt_skull_zones import ISLAND_DOORS, PORTALS
    except ImportError:
        return None
    to = next((h for h, (parent, at) in ISLAND_DOORS.items()
               if parent == zone and tuple(at) == tuple(isle_at[:2])), None)
    if to is None:
        return None
    import importlib
    import numpy as np
    M = importlib.import_module(module)
    dry = {p for p in isle if int(M.tile_kind(np.array([p[0] + 0.5]), np.array([p[1] + 0.5]))[0]) == 0}
    ok = [p for p in dry if p != tuple(centre) and (p[0], p[1] - 2) in dry and (p[0], p[1] - 1) in dry
          and abs(p[0] - centre[0]) + abs(p[1] - centre[1]) >= 2]
    if not ok:
        return None
    x, y = min(ok, key=lambda p: (abs(p[0] - centre[0]) + abs(p[1] - centre[1]), p))
    tx, ty = PORTALS[to]
    return {"x": x, "y": y, "to": to, "tx": tx, "ty": ty}


def _baked_island(module, isle, pts, w):
    """(island tiles, ford tiles, centre) from the zone's own landform functions."""
    import importlib
    import numpy as np
    M = importlib.import_module(module)
    cx0, cy0, r = isle
    kind_at = lambda x, y: int(M.tile_kind(np.array([x + 0.5]), np.array([y + 0.5]))[0])  # noqa: E731
    near = [(x, y) for y in range(cy0 - r, cy0 + r + 1) for x in range(cx0 - r, cx0 + r + 1)
            if (x - cx0) ** 2 + (y - cy0) ** 2 <= r * r]
    kinds = {p: kind_at(*p) for p in near}
    isle_tiles = [p for p, k in kinds.items() if k in (0, 1)]
    land = [p for p, k in kinds.items() if k == 0]
    start = pts[0]
    ford = []
    for y in range(int(min(p[1] for p in pts)) - 3, int(max(p[1] for p in pts)) + 4):
        for x in range(int(min(p[0] for p in pts)) - 3, int(max(p[0] for p in pts)) + 4):
            px, py = x + 0.5, y + 0.5
            d = min(_seg_dist(px, py, a, b) for a, b in zip(pts, pts[1:]))
            # a hidden ford is exactly its own field; the start of an old open one is the shore's
            if hasattr(M, "secret_ford_field"):
                if float(M.secret_ford_field(np.array([px]), np.array([py]))[0]) > 0 and kind_at(x, y) == 1:
                    ford.append((x, y))
            elif d <= w / 2 + 0.6 and (px - start[0]) ** 2 + (py - start[1]) ** 2 > 9 and kind_at(x, y) == 1:
                ford.append((x, y))
    cx = sum(p[0] for p in land) / len(land)
    cy = sum(p[1] for p in land) / len(land)
    centre = min(land, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
    # The island is everything that isn't deep water joined to its middle, not just a disc round
    # it: its shallow ring shows on screen too, and the check that nobody can see it from the
    # mainland (tools/qa_secrets.py) needs all of it. The ford is the way in, not the island.
    fset, seen, todo = set(ford), {centre}, [centre]
    lim = r + 10
    while todo:
        x, y = todo.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in seen or n in fset or abs(n[0] - cx0) > lim or abs(n[1] - cy0) > lim:
                continue
            if n[0] < 0 or n[1] < 0 or n[0] >= M.W or n[1] >= M.H or kind_at(*n) == 2:
                continue
            seen.add(n)
            todo.append(n)
    isle_tiles = sorted(seen)
    return isle_tiles, ford, centre


def _seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    return ((px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2) ** 0.5


FOUND = {
    "behind": ["Somebody's been hiding back here.", "There's more behind here than it looks.",
               "Nobody comes round this side. Somebody does."],
    "glade": ["There's a way through.", "This wall isn't a wall.", "You've found a way nobody marked.",
              "The rock gives way."],
    "island": ["Land, where the map shows only water.", "There's ground out here."],
}


def _level(zone, levels):
    band = levels.get(zone)
    return band[1] if band else 20


def _secret_recipes(seller_id, surname, trades, level):
    """Two recipes sold only by this seller: the best gear recipe of each trade near this level,
    made under the seller's name a step better than the common version."""
    from world.recipe_manager import _load_all_recipes
    allr = _load_all_recipes()
    want = level * 5
    out = []
    for trade in trades:
        pool = [(rid, r) for rid, (p, r) in allr.items() if p == trade and not r.get("secret")
                and (r.get("output") or {}).get("kind") in ("armor", "weapon")
                and r.get("skill_required", 0) <= max(25, want)]
        if not pool:
            continue
        rid, base = max(pool, key=lambda kv: (kv[1].get("skill_required", 0), kv[0]))
        new = json.loads(json.dumps(base))
        new["name"] = f"{surname}'s {base['name']}"
        new["source"] = "vendor"
        new["secret"] = True
        new["sold_by"] = [seller_id]
        o = new["output"]
        o["rarity"] = "epic" if o.get("rarity") == "rare" else "rare"
        o["item_level"] = int(o.get("item_level", level)) + 2
        out.append((trade, f"secret_{seller_id.split('_', 1)[1]}_{rid}", new))
    return out


#: Where each profession's recipes live, so a secret recipe goes in the file that profession reads.
FLAT = {"blacksmithing": "data/blacksmithing/recipes.json", "leatherworking": "data/leatherworking/recipes.json",
        "jewelcrafting": "data/jewelcrafting/recipes.json", "enchanting": "data/enchanting/recipes.json",
        "runecrafting": "data/runecrafting/recipes.json"}
NESTED = "data/crafting/recipes.json"


def _write_recipes(recipes):
    """Remove every old secret recipe, then add these. recipes: [(trade, id, recipe)]."""
    docs = {}
    for trade, path in FLAT.items():
        docs[path] = json.loads((ROOT / path).read_text(encoding="utf-8"))
        r = docs[path]["recipes"]
        for k in [k for k, v in r.items() if isinstance(v, dict) and v.get("secret")]:
            del r[k]
    nested = json.loads((ROOT / NESTED).read_text(encoding="utf-8"))
    for prof in nested["professions"].values():
        r = prof.get("recipes", {})
        for k in [k for k, v in r.items() if isinstance(v, dict) and v.get("secret")]:
            del r[k]
    for trade, rid, rec in recipes:
        if trade in FLAT:
            docs[FLAT[trade]]["recipes"][rid] = rec
        else:
            nested["professions"].setdefault(trade, {"recipes": {}})["recipes"][rid] = rec
    for path, doc in docs.items():
        (ROOT / path).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / NESTED).write_text(json.dumps(nested, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


CONSUMABLES = ROOT / "data/consumables/consumable_types.json"
ENCHANTS = ROOT / "data/enchanting/enchants.json"
MATERIALS = ROOT / "data/gathering/materials.json"


def _secret_meals(seller_id, meals, level, cons_doc, cook_recipes):
    """Unique cooking recipes: the best cooked meal for this level, made better, under a new name."""
    base_pool = [m for m in cons_doc["cooked_meals"] if not m["consumable_id"].startswith("secret_")
                 and m.get("required_level", 1) <= level]
    base_pool.sort(key=lambda m: (m.get("required_level", 1), m.get("effect_value", 0)))
    out = []
    for i, (name, desc) in enumerate(meals):
        base = base_pool[-1 - (i % min(3, len(base_pool)))]
        cid = f"secret_{seller_id.split('_', 2)[-1]}_{i}"
        meal = json.loads(json.dumps(base))
        meal["consumable_id"] = cid
        meal["name"] = name
        meal["effect_value"] = int(base.get("effect_value", 100) * 1.3)
        bonus = {k: v + 2 for k, v in (base.get("stat_bonuses") or {"stamina": 2}).items()}
        meal["stat_bonuses"] = bonus
        stat = ", ".join(f"+{v} {k.replace('_', ' ').title()}" for k, v in bonus.items())
        meal["description"] = (f"{desc} Restores {meal['effect_value']} health over "
                               f"{meal.get('effect_duration', 20)} seconds while you rest, and leaves you well fed "
                               f"({stat}) for 30 minutes.")
        rec_base = next((r for r in cook_recipes.values()
                         if (r.get("output") or {}).get("consumable_id") == base["consumable_id"]), None)
        recipe = json.loads(json.dumps(rec_base)) if rec_base else {
            "inputs": {"meat_stringy": 2}, "skill_required": level * 5, "skill_range": [0, 0, 0, 0]}
        recipe.update({"name": name, "source": "vendor", "secret": True, "sold_by": [seller_id]})
        recipe["output"] = {"kind": "consumable", "consumable_id": cid, "count": 1}
        # its picture is the dish it was made from (assets/icons/consumables/<id>.png)
        import shutil
        src = ROOT / f"assets/icons/consumables/{base['consumable_id']}.png"
        if src.exists():
            shutil.copyfile(src, ROOT / f"assets/icons/consumables/{cid}.png")
        out.append((meal, ("cooking", f"secret_recipe_{cid}", recipe)))
    return out


def _secret_enchant(seller_id, e, ench_doc, mat_doc):
    """A unique enchantment: its definition, its scroll, and the formula for enchanters."""
    eid = e["id"]
    ench_doc["enchants"][eid] = {
        "name": f"Enchant Weapon: {e['title']}", "title": e["title"], "group": e["group"],
        "family": "secret", "tier": 4, "rank": 0, "level": e["level"], "skill": e["skill"], "stats": {},
        "proc": {"trigger": "on_weapon_swing", "chance": e["chance"], "icd": 0, "damage_flat": e["damage"],
                 "school": "fire", "describe": e["describe"]},
        "hybrid": False, "secret": True}
    mat_doc["materials"][eid] = {
        "name": f"Enchant Weapon: {e['title']}", "material_type": "enchant_scroll", "profession": "enchanting",
        "tier": "late", "description": "A scroll holding an enchantment you won't find written down anywhere else. "
                                       "Read it onto gear with the Enchant button in your bags.",
        "stack_limit": 20, "sell_price": e["level"] * 40, "icon_id": "enchant_scroll", "secret": True}
    recipe = {"name": f"Enchant Weapon: {e['title']}",
              "inputs": {"crystal_emberglass": 3, "herb_firebloom": 2},
              "skill_required": e["skill"], "skill_range": [e["skill"], e["skill"] + 10, e["skill"] + 20, e["skill"] + 30],
              "output": {"kind": "material", "material_id": eid},
              "tool": ["runed_truesilver_rod", "runed_arcanite_rod"],
              "source": "vendor", "secret": True, "sold_by": [seller_id]}
    return ("enchanting", f"secret_formula_{eid}", recipe)


def main():
    levels = json.loads((ROOT / "data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]
    cand_path = ROOT / "data/world/secret_candidates.json"
    cands = json.loads(cand_path.read_text(encoding="utf-8")) if cand_path.exists() else {}
    uniques, recipes, secrets = {}, [], []
    pending_meals = []      # (seller, meals, level, their stock list): made once the cookbook is loaded
    vendors_doc = json.loads(VENDORS_PATH.read_text(encoding="utf-8"))
    vendors = [v for v in vendors_doc["vendors"] if not v["vendor_id"].startswith("secret_")]
    from entities.consumable_manager import get_consumable_manager
    cm = get_consumable_manager()
    taken = {}      # zone -> spots used

    def add_vendor(vid, name, zone, spot, race, gender, greeting, stock, level, kind):
        zone_key = zone.lower().replace(" ", "_").replace("'", "")
        vendors.append({
            "vendor_id": vid, "name": name, "zone": zone_key, "x": spot[0], "y": spot[1],
            "tile_sprite": "npc", "sells": stock, "buys_from_player": True, "faction": "neutral",
            "gear_level": level, "sells_gear": False, "race": race, "gender": gender,
            "appearance_variant": 2, "greeting": greeting, "hidden": True})
        taken.setdefault(zone, []).append(tuple(spot))

    # the one Kyle asked for by name
    for v in AUTHORED_VENDORS:
        stock = []
        for uid, d in v["uniques"]:
            uniques[uid] = d
            stock.append(f"unique:{uid}")
        stock += [s for s in v.get("supplies", []) if cm.has_consumable(s)]
        add_vendor(v["vendor_id"], v["name"], v["zone"], v["spot"], v["race"], v["gender"],
                   v["greeting"], stock, 12, "behind")
        secrets.append({"id": v["vendor_id"], "zone": v["zone"], "kind": "behind", "passage": [],
                        "area": [list(v["spot"])], "mask": None, "cache": None,
                        "vendor": v["vendor_id"], "found_text": FOUND["behind"][0]})

    def use(zone, cand):
        """Kyle, 14 Nov 2026: "Our maps are huge. Don't compress secrets so they're obvious and
        boring." So secrets in one map keep a third of the map's size apart: find one and the next
        is somewhere else entirely, not round the corner."""
        spot = tuple(cand["spot"])
        gap = max(12, int((cand.get("map_area") or 0) ** 0.5 / 3))
        if any(abs(spot[0] - t[0]) + abs(spot[1] - t[1]) < gap for t in taken.get(zone, [])):
            return False
        return True

    # hidden sellers, each in its own town
    for entry in SELLERS:
        vid, zone, name, race, gender, greeting, trades, items = entry[:8]
        extras = entry[8] if len(entry) > 8 else {}
        opts = [c for c in cands.get(zone, []) if c["kind"] in ("behind", "glade") and use(zone, c)]
        opts.sort(key=lambda c: (c["kind"] != "behind", -c["depth"]))
        if not opts:
            print(f"  no hidden spot for {name} in {zone}")
            continue
        c = opts[0]
        level = _level(zone, levels)
        # inside a hidden zone the shelves sit as high as its drops (world/hidden_zones.py)
        ilvl = max(10, level + (9 if _is_frontier(zone) else 6 if vid.startswith("secret_hz_") else 3))
        stock = []
        for (iname, slot, suffix, kind, typ, flavor) in items:
            uid = vid.replace("secret_", "") + "_" + iname.lower().replace("'", "").replace(" ", "_").replace("-", "_")
            kw = {}
            if kind == "weapon":
                kw["weapon_type"] = typ
            elif typ:
                kw["armor_type"] = typ
            rarity = "epic" if level >= 45 or _is_frontier(zone) else "rare"
            _, d = unique(uid, iname, slot, suffix, ilvl, flavor, rarity=rarity, **kw)
            uniques[uid] = d
            stock.append(f"unique:{uid}")
        surname = name.split()[-1] if " " in name else name
        for trade, rid, rec in _secret_recipes(vid, surname, trades, level):
            recipes.append((trade, rid, rec))
            stock.append(rid)
        if extras.get("meals"):
            pending_meals.append((vid, extras["meals"], level, stock))
        add_vendor(vid, name, zone, c["spot"], race, gender, greeting, stock, level, c["kind"])
        secrets.append({"id": vid, "zone": zone, "kind": c["kind"], "passage": c["passage"],
                        "area": c["area"] if c["kind"] != "behind" else [c["spot"]],
                        "mask": c.get("mask"), "cache": None, "vendor": vid,
                        "found_text": FOUND[c["kind"]][len(secrets) % len(FOUND[c["kind"]])]})

    # sellers who are not people
    cons_doc = json.loads(CONSUMABLES.read_text(encoding="utf-8"))
    cons_doc["cooked_meals"] = [m for m in cons_doc["cooked_meals"] if not m["consumable_id"].startswith("secret_")]
    ench_doc = json.loads(ENCHANTS.read_text(encoding="utf-8"))
    for k in [k for k, v in ench_doc["enchants"].items() if isinstance(v, dict) and v.get("secret")]:
        del ench_doc["enchants"][k]
    mat_doc = json.loads(MATERIALS.read_text(encoding="utf-8"))
    for k in [k for k, v in mat_doc["materials"].items() if isinstance(v, dict) and v.get("secret")]:
        del mat_doc["materials"][k]
    cook_recipes = json.loads((ROOT / NESTED).read_text(encoding="utf-8"))["professions"]["cooking"]["recipes"]
    for (pvid, meals, plevel, pstock) in pending_meals:
        for meal, rec in _secret_meals(pvid, meals, plevel, cons_doc, cook_recipes):
            cons_doc["cooked_meals"].append(meal)
            recipes.append(rec)
            pstock.append(rec[1])
    for (vid, zone, name, sprite, barter, greeting, items, extras) in CREATURE_SELLERS:
        opts = [c for c in cands.get(zone, []) if c["kind"] == "glade" and use(zone, c)]
        opts.sort(key=lambda c: -c["depth"])
        if not opts:
            print(f"  no hidden room for {name} in {zone}")
            continue
        c = opts[0]
        level = _level(zone, levels)
        stock, prices = [], {}
        for (iname, slot, suffix, kind, typ, flavor) in items:
            uid = vid.replace("secret_", "") + "_" + "".join(ch for ch in iname.lower().replace(" ", "_") if ch.isalnum() or ch == "_")
            kw = {"weapon_type": typ} if kind == "weapon" else ({"armor_type": typ} if typ else {})
            _, d = unique(uid, iname, slot, suffix, level + 3, flavor, rarity="epic" if level >= 45 else "rare", **kw)
            uniques[uid] = d
            stock.append(f"unique:{uid}")
            prices[f"unique:{uid}"] = (barter[2] + 2) if barter else None
        for meal, rec in _secret_meals(vid, extras.get("meals", []), level, cons_doc, cook_recipes):
            cons_doc["cooked_meals"].append(meal)
            recipes.append(rec)
            stock.append(rec[1])
            prices[rec[1]] = barter[2] if barter else None
        if extras.get("enchant"):
            rec = _secret_enchant(vid, extras["enchant"], ench_doc, mat_doc)
            recipes.append(rec)
            stock += [extras["enchant"]["id"], rec[1]]
            prices[extras["enchant"]["id"]] = barter[2] if barter else None
            prices[rec[1]] = (barter[2] * 3) if barter else None
        if extras.get("trades"):
            for trade, rid, rec in _secret_recipes(vid, name.split()[-1], extras["trades"], level):
                recipes.append((trade, rid, rec))
                stock.append(rid)
                prices[rid] = (barter[2] + 1) if barter else None
        add_vendor(vid, name, zone, c["spot"], "goblin", "male", greeting, stock, level, "glade")
        v = vendors[-1]
        v["creature_sprite"] = sprite
        if barter:
            v["barter"] = {"currency": barter[0], "name": barter[1], "default": barter[2],
                           "prices": {k: n for k, n in prices.items() if n}}
            v["buys_from_player"] = False
        secrets.append({"id": vid, "zone": zone, "kind": "glade", "passage": c["passage"], "area": c["area"],
                        "mask": c.get("mask"), "cache": None, "vendor": vid,
                        "found_text": "Something in here is watching you. It doesn't look hostile."})
    CONSUMABLES.write_text(json.dumps(cons_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ENCHANTS.write_text(json.dumps(ench_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MATERIALS.write_text(json.dumps(mat_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # islands baked into the painting: a cache on each, and the map shows only sea
    for n_isle, (zone, module, isle_at, ford_pts, ford_w) in enumerate(BAKED_ISLANDS):
        isle, ford, centre = _baked_island(module, isle_at, ford_pts, ford_w)
        ik = f"isle_{n_isle}"
        level = _level(zone, levels)
        secrets.append({"id": f"{zone.lower().replace(' ', '_')}_{ik}", "zone": zone, "kind": "baked_island",
                        "passage": [list(p) for p in ford], "area": [list(p) for p in isle], "mask": "deep_water",
                        "cache": {"x": centre[0], "y": centre[1], "level": level}, "vendor": None,
                        "found_text": FOUND["island"][len(secrets) % len(FOUND["island"])]})
        # a hidden zone whose door stands on this island (tools/handbuilt_skull_zones.ISLAND_DOORS)
        door = _island_door(zone, module, isle, centre, isle_at)
        if door:
            secrets[-1]["door"] = door
        taken.setdefault(zone, []).append(tuple(centre))

    # SECRET DOORS to the hidden zones (world/hidden_zones.py). Each is a room in the wall of its
    # parent map, reached by a path that looks like rock, with the way in standing in the room.
    # The door is the bottom-middle tile of the room; coming back out you arrive two tiles north
    # of it (world/portal_manager._offset_spawn), in the middle of the room.
    for zname, door_at in _hidden_doors():
        parent, tx, ty = door_at
        opts = [c for c in cands.get(parent, []) if c["kind"] == "glade" and use(parent, c)]
        opts.sort(key=lambda c: -c["depth"])
        if not opts:
            print(f"  no hidden room for the door to a hidden zone in {parent}")
            continue
        c = opts[0]
        sx, sy = c["spot"]
        secrets.append({"id": "door_" + "".join(ch for ch in zname.lower().replace(" ", "_") if ch.isalnum() or ch == "_"),
                        "zone": parent, "kind": "glade", "passage": c["passage"], "area": c["area"],
                        "mask": c.get("mask"), "cache": None, "vendor": None,
                        "door": {"x": sx, "y": sy + 1, "to": zname, "tx": tx, "ty": ty},
                        "found_text": ("The air changes. Nobody has ever stood where you're standing, and "
                                       "the way on goes deeper than anything you know."
                                       if _is_frontier(zname) else
                                       "There's a way down here. It goes a long way down.")})
        taken.setdefault(parent, []).append((sx, sy))

    for sec in _placed_door_secrets():
        secrets.append(sec)
        taken.setdefault(sec["zone"], []).append((sec["door"]["x"], sec["door"]["y"]))

    # caches everywhere else: up to three a map, one in a town
    n = 0
    for zone, cs in sorted(cands.items()):
        level = _level(zone, levels)
        # two a map, three on a big one; plenty, but each one still worth finding
        size = cs[0].get("map_area") or (max(c["spot"][0] for c in cs) * max(c["spot"][1] for c in cs))
        limit = 3 if size >= 30000 else 2
        placed = 0
        for c in sorted(cs, key=lambda c: (c["kind"] == "behind", -c["depth"])):
            if placed >= limit or not use(zone, c):
                continue
            n += 1
            sid = f"cache_{n:03d}"
            spot = list(c["spot"])
            secrets.append({"id": sid, "zone": zone, "kind": c["kind"], "passage": c["passage"],
                            "area": c["area"] if c["kind"] != "behind" else [spot],
                            "mask": c.get("mask"), "ground": c.get("ground"), "shallow": c.get("shallow"),
                            "cache": {"x": spot[0], "y": spot[1], "level": level}, "vendor": None,
                            "found_text": FOUND[c["kind"]][n % len(FOUND[c["kind"]])]})
            taken.setdefault(zone, []).append(tuple(spot))
            placed += 1

    _write_recipes(recipes)
    vendors_doc["vendors"] = vendors
    VENDORS_PATH.write_text(json.dumps(vendors_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    UNIQUES_PATH.write_text(json.dumps({
        "_notes": "One-of-a-kind items carried by hidden sellers. Written by tools/build_secrets.py; "
                  "a seller lists one as \"unique:<id>\" (world/vendor_stock.make_unique).",
        "items": uniques}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECRETS_PATH.write_text(json.dumps({
        "_notes": "Hidden places. Written by tools/build_secrets.py, read by world/secrets.py. "
                  "Kyle asked not to be told where these are.",
        "secrets": secrets}, ensure_ascii=False) + "\n", encoding="utf-8")
    from collections import Counter
    kinds = Counter(s["kind"] for s in secrets)
    print(f"{len(secrets)} secrets ({dict(kinds)}): {sum(1 for v in vendors if v.get('hidden'))} hidden sellers, "
          f"{sum(1 for s in secrets if s.get('cache'))} caches, {len(uniques)} one-of-a-kind items, "
          f"{len(recipes)} secret recipes, across {len({s['zone'] for s in secrets})} maps")


if __name__ == "__main__":
    main()
