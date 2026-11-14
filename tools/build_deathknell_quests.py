"""
Deathknell quest pass (2026-10-22).  Idempotent.

    python3 tools/build_deathknell_quests.py

* Removes the six broken dk_* quests from forsaken_lands.json (their kill objectives used the display-name zone
  "Deathknell" and their explores had no target, so they could never complete) and writes data/quests/deathknell.json.
* Adds the five new NPCs (ambient_npcs.json; positions come from tools/handbuilt_deathknell.NPC_POSITIONS via
  tools/sync_deathknell_npcs.py) and the fetch-item drops (data/creatures/quest_drops.json).

MAP (100x90 valley)   Village square (50,42): Krell (50,38), Instructor (43,42), Mordo (58,41)
  Deathknell Graves ..... (36-64, 50-65)   the Newly Risen (53,60)
  Shadow Grave .......... (33-67, 66-86)   crypt-yard south; Sexton Marrow (47,72)
  The Overrun Claim ..... (7-33, 11-31)    goldmine camp NW; Foreman Gresk (23,24); cave Night Web's Hollow (17,21)
  Weeping Pond .......... (13-33, 55-68)   west; Mourner Isolde (30,60)
  Burned Farmstead ...... (68-86, 64-77)   south-east; Gardener Orrel (73,68)
  Scarlet Forecourt ..... (72-91, 15-28)   north-east; Scout Verrick (72,28); cave Scarlet Crypt (83,19)
  Valley exit ........... east (96,47)     -> Western Tirisfal -> portal (40,40) -> Brill (Deathguard Rennick at (35,33))
Levels  Krell 1-6 main chain | each other giver a short chain whose finale is a rare / cave boss
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import item, kill, fetch    # noqa: E402
from entities.loot_generator import LootGenerator           # noqa: E402

LG = LootGenerator()
OUT = ROOT / "data/quests/deathknell.json"
OLD = ROOT / "data/quests/forsaken_lands.json"
NPCS = ROOT / "data/npcs/ambient_npcs.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
DK, NWH, CRYPT = "deathknell", "night_webs_hollow", "scarlet_crypt"


def vk(target, count, alt=None):          # valley kill
    return kill(target, count, alt=alt, zone=DK)


def ck(target, count, zone):              # cave kill
    return kill(target, count, zone=zone)


def boss(target, zone=DK):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def explore(zone, x, y, radius=6):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


_ABBR = {"strength": "Str", "agility": "Agi", "intellect": "Int", "stamina": "Sta", "spirit": "Spi",
         "hit_rating": "Hit", "spell_power": "SP", "healing_power": "HP", "mp5": "MP5",
         "crit_chance_physical": "Crit", "crit_chance_spell": "Crit", "attack_power": "AP",
         "defense_rating": "Def", "dodge_rating": "Dodge", "parry_rating": "Parry", "block_rating": "Block",
         "block_value": "BV", "armor": "Armor", "spell_penetration": "Pen"}
_SLOTN = {"head": "Helm", "neck": "Necklace", "shoulder": "Shoulders", "back": "Cloak", "chest": "Chest",
          "wrist": "Bracers", "hands": "Gloves", "waist": "Belt", "legs": "Legs", "feet": "Boots",
          "ring": "Ring", "main_hand": "Weapon", "off_hand": "Off-hand", "ranged": "Ranged"}


def label(slot, suffix, armor, weapon):
    stats = "/".join(_ABBR.get(s, s) for s in LG.gear_suffixes[suffix]["stats"])
    base = (weapon or "").replace("_1h", "").replace("_2h", "").replace("_", " ").title() or \
        ((armor or "").title() + " " + _SLOTN[slot]).strip()
    return f"{base} ({stats})"


def pack(ilvl, req, rarity, specs):
    """specs: (name, slot, suffix, flavor, kind) where kind is 'cloth'/'leather'/... or a weapon_type."""
    out = []
    for (name, slot, suffix, flavor, kind) in specs:
        armor = kind if kind in ("cloth", "leather", "mail", "plate", "accessory") else None
        weapon = None if armor or kind is None else kind
        out.append(item(name, slot, suffix, ilvl, flavor, label(slot, suffix, armor, weapon),
                        armor=armor, weapon=weapon, req=req, rarity=rarity))
    return out


def Q(qid, title, giver, lo, hi, desc, objs, xp, gold, accept, done, rew, nxt=None):
    return dict(quest_id=qid, title=title, giver_npc_id=giver, zone=DK, level_min=lo, level_max=hi,
                description=desc, objectives=objs, reward_exp=xp, reward_gold=gold,
                accept_text=accept, turn_in_text=done, next_quest_id=nxt, rewards=rew)


KRELL, INSTR, RISEN = "dk_quest_overseer", "dk_elder", "dk_risen"
MARROW, GRESK, ISOLDE = "dk_sexton_marrow", "dk_foreman_gresk", "dk_mourner_isolde"
ORREL, VERRICK = "dk_gardener_orrel", "dk_scout_verrick"


def quests():
    Z = []
    A = Z.append

    # ============================== OVERSEER KRELL - the main road out ==============================
    A(Q("dk_first_steps", "First Steps in Undeath", KRELL, 1, 3,
        "Overseer Krell says the dead don't get a day off just because they only just died. The Mangy Duskbats nesting "
        "round the village treeline are as gentle a test as the valley offers. Prove the body still answers, even if "
        "the mind is still catching up.",
        [vk("Mangy Duskbat", 5)], 180, 300,
        "You woke up dead. Congratulations. Now go prove the rest of you still works - the duskbats won't test you hard.",
        "Still standing. Good. That's most of the battle, this early.",
        pack(3, 1, "common", [
            ("Newly Risen's Wraps", "wrist", "of Stamina", "Strips of burial linen. Better than nothing, which is what you came with.", "cloth"),
            ("Krell's Spare Cudgel", "main_hand", "of Strength", "Overseer-issue. Heavy, plain, and surprisingly good at getting a point across.", "mace_1h"),
            ("Shroud-Cord Belt", "waist", "of the Monkey", "A burial cord. It holds up your trousers and your dignity.", "leather"),
        ]), "dk_scavenger_scraps"))
    A(Q("dk_scavenger_scraps", "Stolen Supplies", KRELL, 1, 4,
        "The village stores have been shrinking, and not because anyone in Deathknell eats. Ragged scavengers have been "
        "dragging off salt tins, rope, bandages - whatever glints. Krell wants every piece back; the Dark Lady's "
        "bookkeeping is meticulous and so is his.",
        [fetch("stolen_village_scrap", 5)], 200, 400,
        "Birds. A man dies, rises, goes to work, and the birds are robbing him. Bring me five scraps back.",
        "That's the rope. That's the salt. That's - what is that? Never mind. Good work.",
        pack(3, 1, "common", [
            ("Scavenger's Sinew Cord", "back", "of the Wolf", "Braided from whatever the birds left behind.", "leather"),
            ("Salt-Stained Gloves", "hands", "of the Bear", "Rough cloth, stiff with salt. Itch is an acquired taste.", "cloth"),
            ("Krell's Ration Pouch Ring", "ring", "of the Eagle", "A drawstring-ring that proves even the dead hoard.", None),
        ]), "dk_stray_cull"))
    A(Q("dk_stray_cull", "Strays at the Gate", KRELL, 2, 4,
        "Dogs and rats came to the graveyard the way they always do - for what's in the ground. Something in the soil "
        "has sickened them. The plagued strays now tear at the gravediggers and the Newly Risen alike, and the rats "
        "carry it into the village stores. Krell wants them thinned before it spreads.",
        [vk("Plagued Stray", 5), vk("Grave Rat", 3)], 250, 550,
        "They bite, and then you rot a little faster than you were already rotting. Cull them. Seven strays, four rats.",
        "Fewer teeth in the dark. I can sleep - metaphorically - a little easier. Take something from the pile.",
        pack(4, 2, "uncommon", [
            ("Plaguebitten Cap", "head", "of the Whale", "A hat for a bad week. The bite marks are original.", "cloth"),
            ("Stray-Tooth Pendant", "neck", "of the Tiger", "Strung on gut. It clacks when you walk, like a very small funeral.", None),
            ("Ratcatcher's Boots", "feet", "of Agility", "Soft-soled and quiet. They have seen a lot of rats.", "leather"),
        ]), "dk_claim_spiders"))
    A(Q("dk_claim_spiders", "The Overrun Claim", KRELL, 3, 5,
        "The old goldmine to the north-west was a decent little operation until the spiders arrived. Now the camp is "
        "web, bone and bad news - and Foreman Gresk is still there, which is its own kind of miracle. Clear the claim's "
        "spiders so Gresk can breathe, then see what he needs.",
        [vk("Claim Spider", 6)], 340, 850,
        "North-west, past the old gold-road. Eight spiders. Then talk to Gresk - he's at the mine camp, he's cranky, and he's right.",
        "Eight? Good. The Dark Lady has plans for that gold, and none of them include spiders.",
        pack(5, 3, "uncommon", [
            ("Spiderbite Jerkin", "chest", "of the Monkey", "Layered hide, punctured in six places and patched in all of them.", "leather"),
            ("Goldmine Foreman's Spade", "main_hand", "of Strength", "A shovel by trade and a mace by necessity.", "mace_1h"),
            ("Silkweaver's Mantle", "shoulder", "of the Owl", "Spun by something larger than you and a good deal more patient.", "cloth"),
            ("Mineshaft Ring", "ring", "of the Falcon", "Cheap gold, but it knows when a roof is about to come down.", None),
        ]), "dk_scout_hollow"))
    A(Q("dk_scout_hollow", "Into the Hollow", KRELL, 4, 6,
        "The spiders aren't just wandering in - they're being fed. A web-choked cave beside the claim, Night Web's "
        "Hollow, pours them out like a spring. Krell wants eyes on the cave's inner strand before anyone commits to "
        "a fight, because someone in the Undercity asks questions, and he'd like to have the answers.",
        [explore(NWH, 28, 34, 6)], 360, 900,
        "Past the claim's camp there's a cave mouth wrapped in web. Walk the spiral and keep walking until you reach the inner "
        "strand. Do not poke anything. Come back and tell me what you saw.",
        "A broodmother. Of course there's a broodmother. All right - now we know. Next time we go in with a purpose.",
        pack(5, 3, "uncommon", [
            ("Hollow-Scout's Cloak", "back", "of the Monkey", "Dust-grey and web-torn. It makes you forgettable.", "cloth"),
            ("Webwalker Treads", "feet", "of the Wolf", "Soles lined with something that does not stick to silk.", "leather"),
            ("Silk-Spun Gloves", "hands", "of the Eagle", "They smell faintly of cave. They fit better than they should.", "cloth"),
        ]), "dk_neshka"))
    A(Q("dk_neshka", "Broodmother Nesh'ka", KRELL, 5, 7,
        "At the centre of the Hollow, wrapped in her own silk, sits Nesh'ka. Every spider the claim has ever "
        "seen came from her, and while she lives the cave will keep filling the valley. Krell does not need a "
        "diplomatic solution. He needs a corpse, and a handful of her brood for the report.",
        [boss("Broodmother Nesh'ka", NWH), ck("Night Web Spider", 5, NWH)], 620, 1800,
        "She's in the heart of the spiral. She stings, she poisons, and she wraps you. Kill the spiders on the way in and "
        "keep your head. The Dark Lady's name be with you, or whatever passes for luck down here.",
        "Dead. Properly dead. You have more teeth than I thought. I'll note it in the report - favourably, for once.",
        pack(8, 5, "uncommon", [
            ("Nesh'ka's Silkguard Vest", "chest", "of the Owl", "Silk, woven tight, and hers. Her bite didn't pierce it. It might not pierce yours.", "cloth"),
            ("Brood-Slayer's Fang", "main_hand", "of Agility", "A broken stinger, still tipped with something unkind.", "dagger"),
            ("Carapace Round Shield", "off_hand", "of Stamina", "Shell plate on a wood frame. It rings when struck.", "shield"),
            ("Hollow-Won Hauberk", "chest", "of the Bear", "Chain made from a hundred small sacrifices. Most of them were spiders.", "mail"),
        ]), "dk_to_brill"))
    A(Q("dk_to_brill", "Word for Brill", KRELL, 6, 8,
        "The valley is quiet for the first time since you were sewn together, and that is Krell's cue to be rid of you. "
        "The road east leaves Deathknell for the Tirisfal Glades; follow it to the portal in the glade's heart and it "
        "brings you to Brill, the Forsaken's first real town. Krell has written a note for Deathguard Rennick. It says "
        "'Take this one, they bite.' He is not sorry.",
        [explore("brill", 35, 33, 6)], 540, 1500,
        "Take the east road out of the valley, cross the Tirisfal Glades, and follow the road into Brill. Find Deathguard "
        "Rennick and show him my note. Tell him I didn't ruin you. He won't believe it.",
        "You made it out of the valley. Farther than most. The rest of the Forsaken are going to find you very inconvenient. Good.",
        pack(8, 6, "uncommon", [
            ("Krell's Farewell Cloak", "back", "of the Whale", "He's never admitted it, but he sewed the hem himself.", "cloth"),
            ("Overseer's Sturdy Boots", "feet", "of the Bear", "Heavy-soled and ugly. They'll take you anywhere.", "mail"),
            ("Deathknell Graduate's Signet", "ring", "of the Gorilla", "Struck from a grave marker. It's tradition. Nobody likes it.", None),
            ("Valley-Walker's Spear", "main_hand", "of the Tiger", "Ash-wood haft, iron head. It has walked out of the valley before.", "polearm"),
        ])))

    # ============================== THE NEWLY RISEN - the graves ==============================
    A(Q("dk_risen_grave_dwellers", "Restless in the Ground", RISEN, 1, 3,
        "The woman beside the graves can't remember her own name, but she remembers the sound they make - the scratching "
        "from underneath. Grave-Dwellers, freshly risen and not yet coherent, claw their way out of the mass grave and "
        "wander the field in the dark. She wants them put back where they belong.",
        [vk("Restless Grave-Dweller", 5)], 180, 300,
        "They don't know they're dead yet. Please - quickly, before they figure it out.",
        "Thank you. I think I knew one of them. I don't know which. Please - take this. It doesn't feel like mine.",
        pack(3, 1, "common", [
            ("Risen Mourner's Shawl", "shoulder", "of the Owl", "Black wool, moth-eaten. Somebody once cried into it.", "cloth"),
            ("Gravefield Spade", "main_hand", "of Strength", "Left behind. Still sharp. Still muddy.", "mace_1h"),
            ("Dirt-Caked Boots", "feet", "of the Bear", "Clay between every stitch. They will never come clean.", "leather"),
        ]), "dk_risen_grave_markers"))
    A(Q("dk_risen_grave_markers", "Names on the Stones", RISEN, 2, 4,
        "Grave markers are meant to be names. Up here they're mostly splinters, and the restless dead keep tearing them "
        "out of the ground and carrying them off, as though they still wanted to read their own. The Newly Risen "
        "thinks if she can gather enough of them, she might find hers.",
        [fetch("weathered_grave_marker", 5)], 240, 600,
        "The Grave-Dwellers carry them. I think they're looking, too. Please bring five back - I'll sort them by hand.",
        "...Not one of them is mine. But this one has a name I almost - no. Never mind. Thank you.",
        pack(4, 2, "uncommon", [
            ("Etched Marker Charm", "neck", "of the Eagle", "A splinter of oak with half a name. You'll never read the other half.", None),
            ("Mourner's Veil", "head", "of the Whale", "Gauze meant to hide a face. Nobody here is vain about theirs.", "cloth"),
            ("Marker-Stake Dagger", "main_hand", "of Agility", "A grave stake, sharpened. Practical and bleak.", "dagger"),
        ]), "dk_risen_mawgrin"))
    A(Q("dk_risen_mawgrin", "The Gaunt Alpha", RISEN, 3, 5,
        "One of the plagued strays has grown larger than the rest - a gaunt, grey dog that leads the others through the "
        "graves at night, and drags off whatever it likes. The villagers call it Mawgrin. The Newly Risen calls it "
        "'the one who sits on my grave'.",
        [boss("Mawgrin the Gaunt"), vk("Plagued Stray", 4)], 400, 1000,
        "He's out in the field. You'll hear him first. He's bigger than the others and angrier than he looks.",
        "...Gone? That's - good. That's very good. I can sit by my grave in peace. Please - take whatever you like.",
        pack(6, 3, "uncommon", [
            ("Mawgrin's Hide Cloak", "back", "of the Wolf", "Mangy fur and a smell like regret.", "leather"),
            ("Gaunt-Tooth Choker", "neck", "of the Bear", "Fangs on a leather thong. They've held up better than you'd expect.", None),
            ("Gravehound Gauntlets", "hands", "of the Tiger", "Mail studded with teeth. They bite on both ends.", "mail"),
            ("Plague-Bitten Mace", "main_hand", "of Strength", "Dented, notched, and still keen to hit something.", "mace_1h"),
        ])))

    # ============================== DEATH KNIGHT INSTRUCTOR - drill ==============================
    A(Q("dk_instructor_bones", "Drill: Bones", INSTR, 2, 4,
        "The Instructor believes a Forsaken learns by hitting things that are already dead. Rattlecage Skeletons - "
        "crypt-dwellers, long dead and bad-tempered about it - pace the Shadow Grave to the south, and they make the "
        "best sparring partners the valley offers. They never complain and they never stay down.",
        [vk("Rattlecage Skeleton", 6)], 280, 700,
        "Shadow Grave, south of the graves. Skeletons. Hit them until they stop. Then hit them a little more.",
        "Not graceful. Not clever. But you're upright and they aren't, and that is the entire syllabus.",
        pack(4, 2, "uncommon", [
            ("Drillmaster's Bracers", "wrist", "of the Bear", "Plate for knuckles. The Instructor swears they're lucky.", "plate"),
            ("Rattlecage Femur Club", "main_hand", "of Strength", "A genuine femur. The previous owner objects.", "mace_1h"),
            ("Marching-Band Tabard", "chest", "of the Tiger", "Don't ask. It was in the Instructor's trunk.", "mail"),
        ]), "dk_instructor_wights"))
    A(Q("dk_instructor_wights", "Wights of Shadow Grave", INSTR, 3, 5,
        "Wights are a different kind of dead - the kind that never got the Dark Lady's gift of will, just hunger. "
        "They haunt the Shadow Grave's old stones and drain the living of whatever's left. The Instructor wants "
        "them put down before they wander up into the village proper.",
        [vk("Shadow Grave Wight", 6)], 350, 900,
        "They aren't like us. No will behind the eyes. Just hunger wearing a corpse. Put them down.",
        "That's the kind of mercy they can't thank you for, but it's mercy all the same. Take your pick.",
        pack(5, 3, "uncommon", [
            ("Shadow Grave Wraps", "hands", "of the Owl", "Taken off a wight that had no more use for hands.", "cloth"),
            ("Wight-Bone Bracers", "wrist", "of Stamina", "Bleached and shaped. They'd have stopped a blade once.", "mail"),
            ("Graveside Belt", "waist", "of the Whale", "A cord of knotted grave-linen. Good luck is optional.", "leather"),
            ("Withering Rod", "main_hand", "of Intellect", "A staff that remembers being dead. It remembers fondly.", "staff"),
        ]), "dk_instructor_ossric"))
    A(Q("dk_instructor_ossric", "The Unburied", INSTR, 4, 6,
        "One of the Shadow Grave's dead refuses to stay in his hole. Ossric was a sexton once - he buried half the "
        "village. Now he rises every night with the spade still in his hand, searching for the grave nobody dug for him. "
        "The Instructor would very much like someone to dig it.",
        [boss("Ossric the Unburied"), vk("Wretched Zombie", 3)], 460, 1200,
        "He's in the crypt-yard, by the old headstones. Zombies follow him around like mourners. Clear the mourners, then Ossric.",
        "Finally. He can rest. And for what it's worth - you did that well. Take something from the pile. I mean it.",
        pack(7, 4, "uncommon", [
            ("Ossric's Shroud-Wrap", "chest", "of the Owl", "Burial linen that never decayed. It remembers the man.", "cloth"),
            ("Sexton's Iron Spade", "main_hand", "of the Bear", "A working tool, still crusted. It's as heavy as the job.", "mace_1h"),
            ("Boneplate Pauldrons", "shoulder", "of Strength", "Fused vertebrae and iron. They rattle against your neck.", "plate"),
            ("Burial Bell Charm", "neck", "of the Eagle", "It chimes for the dead. It's chiming right now.", None),
        ])))

    # ============================== SEXTON MARROW - the yard ==============================
    A(Q("dk_marrow_shrouds", "Shrouds for the Unburied", MARROW, 2, 4,
        "Sexton Marrow tends the Shadow Grave's crypt-yard, and he takes pride in never leaving anyone uncovered. The "
        "zombies and skeletons wandering the yard wear scraps of burial shroud - his shrouds, the good linen. He'd like "
        "them back, preferably before the next burial.",
        [fetch("tattered_burial_shroud", 6)], 260, 650,
        "I stitched every one of them myself. The zombies took them off the corpses. Bring them back, and mind the stains.",
        "These are still good. Washed and pressed, they'll do someone another burial. You've a good eye for linen. Take your pick.",
        pack(4, 2, "uncommon", [
            ("Marrow's Mending Gloves", "hands", "of the Eagle", "Needle-callused. They handle cloth better than flesh.", "cloth"),
            ("Gravedigger's Kidney Belt", "waist", "of Stamina", "Wide leather. Seven hundred burials, one back.", "leather"),
            ("Linen-Wrapped Hammer", "main_hand", "of the Bear", "A maul wrapped in clean linen. For quiet work.", "mace_1h"),
        ])))

    # ============================== FOREMAN GRESK - the claim ==============================
    A(Q("dk_gresk_diggers", "Dead Men Don't Dig", GRESK, 3, 5,
        "Gresk's crew was undead before the spiders arrived - which turned out to be convenient for the spiders. The "
        "dead diggers kept working after Gresk gave up supervising them, and now they swing their picks at anyone who "
        "comes near the shaft. He cannot reason with them. He'd like you to try something else.",
        [vk("Dead Digger", 6)], 320, 800,
        "My crew. Every one of them. They don't stop. They don't recognise me. They just dig. Please put them out of it.",
        "I thought I'd feel worse. I don't. Honest work, that, and quick. Take something for it.",
        pack(5, 3, "uncommon", [
            ("Foreman's Hardhat", "head", "of the Bear", "Dented iron. Has saved this man's skull more than once.", "mail"),
            ("Digger's Callused Gloves", "hands", "of Strength", "Thick leather. The knuckles are scraped bare.", "leather"),
            ("Prospector's Pick-Mace", "main_hand", "of the Tiger", "A pick with the point flattened. Now it's a mace.", "mace_1h"),
        ]), "dk_gresk_thread"))
    A(Q("dk_gresk_thread", "Gold on a Thread", GRESK, 4, 6,
        "The spiders weave with more than silk. They've been lacing real gold dust through their webs - taken from the "
        "old veins and spun into lines that glint in the dark. Gresk wants every strand back; the Dark Lady likes gold "
        "and Gresk likes being alive.",
        [fetch("spun_gold_thread", 5)], 360, 950,
        "Look for the spiders that sparkle. They've got gold in their webs, and I want it in my ledger.",
        "That's gold. Honest gold. Spider-spun, but gold. You've saved my neck - what's left of it.",
        pack(6, 4, "uncommon", [
            ("Goldspun Cloak", "back", "of the Monkey", "A shimmer in the weave. It catches torchlight.", "cloth"),
            ("Spiderwire Belt", "waist", "of the Wolf", "Silk and thread-of-gold. Strong enough to hang a man.", "leather"),
            ("Veinseeker's Ring", "ring", "of the Falcon", "It warms when there's gold nearby. It's warm a lot.", None),
        ]), "dk_gresk_goldfang"))
    A(Q("dk_gresk_goldfang", "Goldfang", GRESK, 5, 7,
        "One of the claim's spiders has grown fat on the gold, and bright with it - its fangs have gone yellow-bright "
        "and it hunts the crew's old tunnels. The diggers call it Goldfang. Gresk calls it a problem with a price.",
        [boss("Goldfang"), vk("Claim Spider", 4)], 430, 1200,
        "It's big, it's gold-toothed, and it's mine. Not literally - but the gold in its fangs is the Dark Lady's, and I want it back.",
        "There it is. Pure gold, in a spider's jaw. The world is a funny place. Take your pick of the lot.",
        pack(8, 5, "uncommon", [
            ("Goldfang's Gilded Wand", "main_hand", "of Intellect", "A fang, set in dark wood. Still bright.", "wand"),
            ("Gilt-Webbed Gloves", "hands", "of the Falcon", "Soft silk spun with real gold. Warm on the fingers.", "cloth"),
            ("Prospector's Strongbelt", "waist", "of the Bear", "Heavy, riveted, mine-proof. It keeps you together.", "mail"),
            ("Claim-Warden's Spear", "main_hand", "of the Tiger", "A long spear made for long shafts.", "polearm"),
        ]), "dk_gresk_hatchery"))
    A(Q("dk_gresk_hatchery", "Clearing the Hatchery", GRESK, 6, 8,
        "The Hollow's hatchery is where the claim's spiders come from - a chamber in the north-west of the cave where "
        "egg-clutches hang in the silk, guarded by Hatchery Warden Skrix. The Pale Weaver lurks on the far side, "
        "spinning cocoons around the dead. Gresk wants both gone, and the clutches cleared with them.",
        [boss("Hatchery Warden Skrix", NWH), boss("The Pale Weaver", NWH), ck("Brood Hatchling", 5, NWH)],
        480, 1700,
        "The Hollow's four corners are nurseries. Skrix guards the north-west one. The Weaver's in the south-east brood chamber. "
        "Kill both, and thin the hatchlings while you're at it.",
        "Both of them. And the hatchlings. You are a very efficient little horror. Take your pick.",
        pack(9, 6, "uncommon", [
            ("Hatchery Warden's Cap", "head", "of Agility", "Chitin plates on leather. Still smells of silk and egg.", "leather"),
            ("Weaver's Silk Leggings", "legs", "of the Owl", "Fine, pale and a little too fine to be natural.", "cloth"),
            ("Brood-Warden's Fang", "main_hand", "of the Monkey", "A shard of chitin, honed into a dagger.", "dagger"),
            ("Eggshell Roundshield", "off_hand", "of Stamina", "A shield of shell and silk. Better than it looks.", "shield"),
        ])))

    # ============================== MOURNER ISOLDE - the pond ==============================
    A(Q("dk_isolde_wretches", "Waters Gone Wrong", ISOLDE, 3, 5,
        "The pond west of the graves was a mourners' spot once, a place to sit and talk to the dead. Now the dead "
        "talk back - the drowned wretches that crawl from the silt, dripping and moaning, grabbing at anyone near the "
        "bank. Isolde sits there all day anyway. She asks only that the pond be quiet when she comes.",
        [vk("Drowned Wretch", 6)], 310, 800,
        "They crawl out of the water at dusk, grey as the silt, and they cry. I can't hear myself think. Please.",
        "Quieter. Thank you. It's a poor kind of grief that has to compete with the dead for volume.",
        pack(5, 3, "uncommon", [
            ("Pond-Reed Wraps", "wrist", "of the Whale", "Woven reed, damp forever. They smell of mud and prayers.", "cloth"),
            ("Silt-Streaked Belt", "waist", "of the Bear", "Leather darkened by pond water. It holds a lot.", "leather"),
            ("Mourner's Cane", "main_hand", "of Spirit", "A walking stick for walking slowly, with grief.", "staff"),
        ]), "dk_isolde_keepsakes"))
    A(Q("dk_isolde_keepsakes", "Keepsakes in the Silt", ISOLDE, 4, 6,
        "Isolde lost more than a husband to this pond. The mourners who came here left tokens on the bank - rings, "
        "lockets, ribbon - and the pond-dead have collected them, as if hoarding grief. She would like them returned "
        "to the families, or to someone, or to herself.",
        [fetch("tarnished_keepsake", 5)], 360, 950,
        "The wretches and the shades both carry them. They don't know what they mean - they just know they were loved.",
        "...Oh. This one's mine. This one's... someone's. Thank you. I'll see they're kept. Take your pick of mine.",
        pack(6, 4, "uncommon", [
            ("Keepsake Locket", "neck", "of the Eagle", "Empty of picture. It remembers the weight.", None),
            ("Widow's Black Veil", "head", "of the Owl", "Gauze and ribbon. It's heavy in a way fabric shouldn't be.", "cloth"),
            ("Wading Boots", "feet", "of the Whale", "Leather, waxed against the pond. They squelch.", "leather"),
        ]), "dk_isolde_wren"))
    A(Q("dk_isolde_wren", "Quiet the Weeping", ISOLDE, 5, 7,
        "There's one wail in the pond that's louder than the rest. The Mourning Wren - a shade that stands on the "
        "water at night, weeping in a voice that chills every other thing into following. Isolde has heard that voice "
        "since she arrived. She thinks she knows who it is, and she'd rather it didn't last.",
        [boss("Mourning Wren"), vk("Weeping Shade", 4)], 440, 1200,
        "She stands on the water at night. The shades follow her. End the Wren and the pond will go quiet.",
        "...Gone. Finally. I thought it would feel different. It's only quiet. That's - enough. Please, take whatever helps.",
        pack(8, 5, "uncommon", [
            ("Wren's Mourning Shawl", "shoulder", "of the Owl", "Damp, cold, and softer than any cloth should be.", "cloth"),
            ("Keening Staff", "main_hand", "of the Eagle", "It hums at the pitch of a person crying alone.", "staff"),
            ("Tear-Stained Sandals", "feet", "of the Whale", "Reeds and ribbon. They leave wet prints.", "cloth"),
            ("Drowned Mourner's Ring", "ring", "of Spirit", "Silver gone green. The inscription is a name you can't quite read.", None),
        ])))

    # ============================== GARDENER ORREL - the farmstead ==============================
    A(Q("dk_orrel_scarecrows", "Scarecrows That Walk", ORREL, 4, 6,
        "Orrel tended these fields before the fire, and he still does, in his own way. The scarecrows he built to "
        "keep the crows off have got up and begun walking the furrows, flailing at anything that moves. He assumes it's "
        "his own fault. He'd like you to correct it.",
        [vk("Blighted Scarecrow", 6)], 370, 950,
        "I stuffed them myself. With straw, and some other things I didn't think about. They hit hard. Please be careful.",
        "I'll rebuild them. Properly, this time. Without - whatever it was. Take something for the trouble.",
        pack(6, 4, "uncommon", [
            ("Strawstuffed Jerkin", "chest", "of the Monkey", "Padded leather. It rustles, faintly, even when still.", "leather"),
            ("Orrel's Hedge Shears", "main_hand", "of Agility", "Garden tools with a mean streak.", "dagger"),
            ("Furrow-Walker Boots", "feet", "of the Bear", "Thick boots, clay to the ankle. They still smell of ash.", "mail"),
        ]), "dk_orrel_seeds"))
    A(Q("dk_orrel_seeds", "Seeds Worth Saving", ORREL, 5, 7,
        "The fire took the house and most of the harvest, but not the seed-packets. Orrel buried them in the cellar and "
        "the burned farmhands have been digging them up, as though they remember what the seeds were for. He wants "
        "them back - nothing grows in Tirisfal, but he intends to try.",
        [fetch("unburnt_seed_packet", 5)], 410, 1050,
        "The farmhands keep them in their pockets. Maybe it's habit. Maybe they still hope. Bring me five.",
        "Five. Enough for a row. Maybe two. It's a stubborn kind of hope, I know - but it's mine. Take your pick.",
        pack(7, 5, "uncommon", [
            ("Gardener's Hat", "head", "of the Whale", "Wide-brimmed, stained, and weathered. Somebody loved this hat.", "cloth"),
            ("Seedpacket Satchel Belt", "waist", "of the Eagle", "Full of pockets, all of them empty now.", "cloth"),
            ("Orchard-Keeper's Hoe", "main_hand", "of Strength", "A garden tool turned bludgeon.", "mace_1h"),
        ]), "dk_orrel_thorne"))
    A(Q("dk_orrel_thorne", "Old Gaffer Thorne", ORREL, 6, 8,
        "Gaffer Thorne owned the farm. When the fire came he stayed to save the barn, and when the barn went he "
        "stayed anyway. He still walks the burned rows with a rusted scythe, cutting down whatever he finds, "
        "convinced it's harvest. Orrel owes him a decent burial and will not do it himself.",
        [boss("Gaffer Thorne"), vk("Burned Farmhand", 4)], 540, 1500,
        "He's at the far end of the rows, scythe in hand. Don't talk to him - he won't hear it. Just stop him, for both our sakes.",
        "...He's at rest. The harvest's in. Thank you. I'll bury him myself, in the end. Take whatever you need from his barn.",
        pack(9, 6, "uncommon", [
            ("Thorne's Harvest Scythe", "main_hand", "of Strength", "Rusted, notched and heavy. It cuts yet.", "polearm"),
            ("Scorched Barn-Door Shield", "off_hand", "of Stamina", "Charred wood on an iron rim. It kept the fire out once.", "shield"),
            ("Burnt Farmer's Gauntlets", "hands", "of the Bear", "Scorched leather over scorched knuckles. They still grip hard.", "mail"),
            ("Strawcloak of the Harvest", "back", "of the Monkey", "A coat of old straw. Surprisingly warm.", "cloth"),
        ])))

    # ============================== SCOUT VERRICK - the Scarlet forecourt ==============================
    A(Q("dk_verrick_pickets", "Eyes on the Crusade", VERRICK, 5, 7,
        "The Scarlet Crusade has made a camp outside the old crypt at the valley's north-east edge - pickets, "
        "torchbearers and a great deal of righteous noise. Verrick has watched them for a week from the rocks and "
        "concluded they will not leave on their own. He'd like fewer of them.",
        [vk("Scarlet Picket", 5), vk("Scarlet Torchbearer", 3)], 430, 1100,
        "They burn what they can't convert. They convert what they can't burn. Thin them out before they burn the valley.",
        "Good. Quiet, clean and no survivors to report. You've done this before - maybe in a life you don't remember.",
        pack(6, 5, "uncommon", [
            ("Scout's Mottled Cloak", "back", "of the Monkey", "Dyed grey-green. Fades into the rocks.", "cloth"),
            ("Picket's Dented Helm", "head", "of the Bear", "Crimson paint over dents. It's a better helm than its owner.", "mail"),
            ("Torchbearer's Ember Ring", "ring", "of the Falcon", "Warm to the touch. It never goes out.", None),
        ]), "dk_verrick_orders"))
    A(Q("dk_verrick_orders", "Burning Orders", VERRICK, 5, 7,
        "The Scarlets write everything down - dispatches, sermons, orders for the next day's burning. Verrick wants "
        "those orders. A dispatch in hand tells him what the Crusade plans, which tells him what to plan against. "
        "The pickets and torchbearers carry them stuffed in their belts.",
        [fetch("scarlet_dispatch", 4)], 440, 1150,
        "Their pockets are full of paper. Paper is wonderful. Bring me four dispatches and I'll bring you the war.",
        "Hm. They plan to move on the crypt's reliquary. A patrol, a priest, a lot of banners. This is useful. Take your pick.",
        pack(6, 5, "uncommon", [
            ("Courier's Satchel Strap", "shoulder", "of the Wolf", "A messenger's leather. Pockets inside pockets.", "leather"),
            ("Inkstained Gloves", "hands", "of the Owl", "Cloth stained black. They smell of ledgers.", "cloth"),
            ("Forged-Seal Ring", "ring", "of the Eagle", "A stolen seal. It opens more doors than a key.", None),
        ]), "dk_verrick_halbrook"))
    A(Q("dk_verrick_halbrook", "Sergeant Halbrook", VERRICK, 6, 8,
        "Sergeant Halbrook runs the Crusade's picket line - eight years of service, a halberd he named, and a "
        "certainty that undeath is a sin. Verrick has marked him for the longest time. If the forecourt loses its "
        "sergeant, the pickets lose their spine.",
        [boss("Sergeant Halbrook"), vk("Scarlet Picket", 3)], 520, 1400,
        "He stands by the crypt gate. Big, loud, and disciplined. Break the line and he'll break with it.",
        "Without Halbrook that camp is a rabble with torches. Excellent. Now we can talk about the crypt.",
        pack(9, 6, "uncommon", [
            ("Halbrook's Notched Halberd", "main_hand", "of the Bear", "Eight years of tally marks along the haft.", "polearm"),
            ("Sergeant's Enamel Pauldrons", "shoulder", "of Strength", "Crimson over steel. Someone polished them daily.", "plate"),
            ("Picket-Line Stout Boots", "feet", "of the Bear", "Made for long watches and kicking down doors.", "mail"),
            ("Crusade Tabard-Sash", "waist", "of the Tiger", "Faded red cloth. Still looks righteous at a distance.", "mail"),
        ]), "dk_verrick_crypt"))
    A(Q("dk_verrick_crypt", "Into the Scarlet Crypt", VERRICK, 6, 8,
        "The Scarlet Crypt is the Crusade's foothold in the valley - a chapel, an ossuary, a reliquary and a High "
        "Inquisitor with a fondness for confessions. Verrick wants someone to walk its nave and tell him what's holding "
        "the doors shut. He won't go himself. He's seen what happens to scouts who do.",
        [explore(CRYPT, 47, 32, 7)], 480, 1300,
        "The crypt gate's behind the picket line. Go down the stair, through the nave, to the chapel crossing. See it. Come back and tell me.",
        "A chapel crossing, an inquisitor, vaults on both sides. It's worse than I thought and better than I feared. Take your pick.",
        pack(8, 6, "uncommon", [
            ("Crypt-Scout's Hooded Cloak", "back", "of the Monkey", "Greyed linen over dull leather. Nobody remembers you.", "cloth"),
            ("Penitent's Soft Boots", "feet", "of the Wolf", "Soft-soled, quiet on stone.", "leather"),
            ("Verrick's Spare Dagger", "main_hand", "of Agility", "A thin blade he never used. It's very sharp.", "dagger"),
        ]), "dk_verrick_fairbanks"))
    A(Q("dk_verrick_fairbanks", "The High Inquisitor", VERRICK, 7, 9,
        "High Inquisitor Fairbanks has broken more Forsaken than the valley holds. He sits at the sanctum's far end, "
        "behind a loop of candlelit corridors, and he does not leave. Verrick has no clever plan. He has only "
        "an axiom: nobody who goes down there should expect to come back, and so far the exception is you.",
        [boss("High Inquisitor Fairbanks", CRYPT), ck("Scarlet Initiate", 5, CRYPT)], 770, 2400,
        "The sanctum, past the penitent's walk. He smites, he curses, and he cleanses. Kill the initiates first - they'll heal him otherwise.",
        "Fairbanks. Dead. The Crusade will bleed for it. I won't - but I'll drink to it, in the way the dead drink. Take your reward.",
        pack(11, 7, "rare", [
            ("Fairbanks' Inquisitor Mace", "main_hand", "of the Hierophant", "Flanges engraved with confessions. Some are being added.", "mace_1h"),
            ("Crimson Inquisitor's Mantle", "shoulder", "of the Archmage", "Silk the colour of old wine. It never wrinkles.", "cloth"),
            ("Sanctum Warplate Gauntlets", "hands", "of the Champion", "Worn by a man who believed every strike was a sermon.", "plate"),
            ("Scarlet Penitent's Hauberk", "chest", "of the Physician", "Mail under crimson. The blessing is mostly intact.", "mail"),
        ]), "dk_verrick_vaults"))
    A(Q("dk_verrick_vaults", "The Sealed Vaults", VERRICK, 7, 9,
        "Fairbanks is dead, but the crypt still keeps its secrets. The ossuary to the west holds the dead the Crusade "
        "never finished burying, under Valdric Bonewarden. The reliquary to the east belongs to Brother Wystan, who "
        "keeps whatever the Scarlets thought worth saving. Verrick wants both vaults opened.",
        [boss("Valdric Bonewarden", CRYPT), boss("Brother Wystan", CRYPT)], 720, 2200,
        "West vault: bones and a warden. East vault: relics and a priest. Two doors, two keepers. Both need to go.",
        "Both vaults open. You have done in an afternoon what my scouts failed at for a month. I'll tell the Undercity. Quietly.",
        pack(11, 7, "rare", [
            ("Bonewarden's Ossuary Helm", "head", "of the Soldier", "A helm of fused bone. It hums with other people's prayers.", "plate"),
            ("Reliquary Keeper's Robe", "chest", "of the Restorer", "Layered white wool. The blood only shows in certain light.", "cloth"),
            ("Vaultbreaker's Censer", "main_hand", "of the Prophet", "Heavy, hollow and warm. It still smells of incense.", "mace_1h"),
            ("Scarlet Relic Signet", "ring", "of the Seer", "Gilded and inscribed with an oath that no longer binds.", None),
        ])))
    return Z


# ----------------------------------------------------------------------
NEW_NPCS = [
    dict(npc_id="dk_foreman_gresk", name="Foreman Gresk", gender="male", appearance_variant=5, facing="down",
         greeting="Don't touch the shaft. Don't touch the crew. Don't touch the spiders. Actually - do touch the spiders."),
    dict(npc_id="dk_mourner_isolde", name="Mourner Isolde", gender="female", appearance_variant=2, facing="right",
         greeting="The water's cold. It is always cold. I keep thinking if I sit here long enough, it will stop."),
    dict(npc_id="dk_gardener_orrel", name="Gardener Orrel", gender="male", appearance_variant=9, facing="down",
         greeting="Nothing grows here. I know. I plant anyway. Somebody has to believe in tomorrow."),
    dict(npc_id="dk_scout_verrick", name="Scout Verrick", gender="male", appearance_variant=7, facing="left",
         greeting="Keep your voice down. The Scarlets have good ears and short tempers."),
    dict(npc_id="dk_sexton_marrow", name="Sexton Marrow", gender="male", appearance_variant=3, facing="down",
         greeting="Every soul deserves a proper burial. Even the ones that won't stay in it."),
]

QUEST_DROPS = {
    "weathered_grave_marker": ("Weathered Grave Marker", "A splintered marker with half a name. Somebody was loved, once.",
                               [("Restless Grave-Dweller", 0.45), ("Grave Rat", 0.2)]),
    "tattered_burial_shroud": ("Tattered Burial Shroud", "Good linen, ruined. Sexton Marrow will know whose.",
                               [("Wretched Zombie", 0.5), ("Rattlecage Skeleton", 0.35)]),
    "spun_gold_thread": ("Spun Gold Thread", "Spider-silk laced with real gold dust. Glints in the dark.",
                         [("Claim Spider", 0.45)]),
    "tarnished_keepsake": ("Tarnished Keepsake", "A ring, a locket, a ribbon. Somebody left it at the pond.",
                           [("Drowned Wretch", 0.4), ("Weeping Shade", 0.3)]),
    "unburnt_seed_packet": ("Unburnt Seed Packet", "Paper, singed at the edges. The seeds inside are still good.",
                            [("Burned Farmhand", 0.4), ("Blighted Scarecrow", 0.25)]),
    "scarlet_dispatch": ("Scarlet Dispatch", "Orders for tomorrow's burning, in a neat clerical hand.",
                         [("Scarlet Picket", 0.4), ("Scarlet Torchbearer", 0.4)]),
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

    # drop the six broken originals
    data = json.loads(OLD.read_text(encoding="utf-8"))
    before = len(data["quests"])
    data["quests"] = [q for q in data["quests"] if not q["quest_id"].startswith("dk_")]
    OLD.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # NPCs
    nd = json.loads(NPCS.read_text(encoding="utf-8"))
    have = {n["npc_id"]: n for n in nd["npcs"]}
    for n in NEW_NPCS:
        rec = dict(n, zone="deathknell", x=0, y=0, race="forsaken")
        if n["npc_id"] in have:
            for k in ("name", "greeting", "gender", "appearance_variant", "facing", "race", "zone"):
                have[n["npc_id"]][k] = rec[k]
        else:
            nd["npcs"].append(rec)
    NPCS.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # quest-item drops
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for item_id, (name, desc, srcs) in QUEST_DROPS.items():
        for creature, chance in srcs:
            lst = drops.setdefault(creature, [])
            lst[:] = [d for d in lst if d["item_id"] != item_id]
            lst.append(dict(item_id=item_id, name=name, category="quest", description=desc, chance=chance))
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"deathknell quests: {len(out)} (removed {before - len(data['quests'])} old), "
          f"items {sum(len(q['unique_item_defs']) for q in out)}")


if __name__ == "__main__":
    main()
