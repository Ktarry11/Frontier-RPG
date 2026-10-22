"""
Southern Barrens local quest hub (2026-10-21).  Idempotent: rewrites data/quests/southern_barrens_hub.json.

    python3 tools/build_southern_barrens_quests.py

(The 16 Orgrimmar / Taurajo / Ratchet-given quests in southern_barrens.json are untouched.)

MAP (260x240; full notes in tools/handbuilt_southern_barrens.py)
  Rift-Warden Brakka (137,116) + Provisioner Hemma - the Rift Waystation on the north rim of the Rift canyon.
  Bonehunter Rurk (128,172) at the Field of Giants gate.   Thornwatch Ranger Oggra (62,141) Razorfen approach.
  Dig-Scout Tarrik (63,57) on the Bael Modan quarry rim.    Spy Zhuul (121,41) by the Bael'dun Keep east gate.
  Huntress Alamir (195,49) in the NE hunter's blind (Hoodoo Spires; Raptor Grounds to the south).
  Excavator Fizzwick (209,222) on the Sinkhole Crater rim (Broodspiral stair at (225,220)).
Every giver has ONE chain; rares are paired with trash so the ~6 % roll never stalls a quest.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import item, kill, fetch   # noqa: E402
RZ = "razorfen_kraul"
BS = "the_broodspiral"                                      # dungeon-scoped objectives only count inside it

OUT = ROOT / "data/quests/southern_barrens_hub.json"
Z = "southern_barrens"

_STAT = {"strength": "Str", "agility": "Agi", "intellect": "Int", "stamina": "Sta", "spirit": "Spi"}
_SLOTNAME = {"head": "Helm", "shoulder": "Shoulders", "chest": "Chest", "wrist": "Bracers", "hands": "Gloves",
             "waist": "Belt", "legs": "Legs", "feet": "Boots", "back": "Cloak", "neck": "Necklace", "ring": "Ring",
             "ranged": "Ranged", "off_hand": "Off-hand", "main_hand": "Weapon"}


def boss(target, zone=None):
    o = dict(type="kill_boss", target=target, count=1)
    if zone:
        o["zone"] = zone
    return o


def explore(x, y, radius=8):
    return dict(type="explore", target=Z, target_x=x, target_y=y, radius=radius)


def R(lvl, name, slot, suffix, flavor, kind=None):
    """Reward.  kind: 'cloth'|'leather'|'mail'|'plate' armour, or a weapon type like 'dagger'; None for jewellery/back."""
    weapons = {"sword_1h", "sword_2h", "axe_1h", "axe_2h", "mace_1h", "mace_2h", "dagger", "fist_weapon", "staff",
               "wand", "thrown", "totem", "shield", "bow", "gun", "crossbow", "polearm"}
    armor = kind if kind in ("cloth", "leather", "mail", "plate") else None
    weapon = kind if kind in weapons else None
    if slot == "back" and armor is None:
        armor = "cloth"
    d = item(name, slot, suffix, lvl + 3, flavor, "", armor=armor, weapon=weapon, req=lvl)
    stats = "/".join(_STAT[s] for s in d.get("primary_stats", {}) if s in _STAT)
    if weapon:
        word = {"mace_2h": "Mace 2H", "mace_1h": "Mace 1H", "axe_1h": "Axe 1H", "axe_2h": "Axe 2H",
                "sword_1h": "Sword 1H", "sword_2h": "Sword 2H", "fist_weapon": "Fist Weapon"}.get(weapon, weapon.title())
    elif slot in ("back", "neck", "ring"):
        word = _SLOTNAME[slot]
    else:
        word = f"{armor.title()} {_SLOTNAME[slot]}"
    d["label"] = f"{word} ({stats})" if stats else word
    return d


def Q(qid, title, giver, lvl, desc, objs, accept, turnin, rewards, nxt=None, xp=None, gold=None, span=2):
    return dict(
        quest_id=qid, title=title, giver_npc_id=giver, zone=Z, level_min=lvl, level_max=lvl + span,
        description=desc, objectives=objs,
        reward_exp=xp or int(lvl * 58 + 40), reward_gold=gold or int(lvl * 240),
        accept_text=accept, turn_in_text=turnin, rewards=rewards, next_quest_id=nxt)


def quests():
    A = []
    a = A.append

    # ============================== RIFT-WARDEN BRAKKA (Rift Waystation) ==============================
    G = "sb_rift_warden"
    a(Q("sb_hawks_over_the_rift", "Hawks Over the Rift", G, 18,
        ("The Rift is a day's walk of broken canyon between Camp Taurajo and everything south of it, and Brakka "
         "Stonehoof keeps the ramp that crosses it. Cliffhawks have started to nest in the walls. They don't mind "
         "the caravans. They mind the people on the ramp, who they see, quite reasonably, as dinner."),
        [kill("Rift Cliffhawk", 8)],
        ("Brown wings, white throats, a lot of attitude. Thin them out along the canyon walls. "
         "Don't fall in. The Rift is not forgiving about that."),
        ("Quieter already. I can hear the wagons again. Take this. It's the least the Waystation owes you."),
        [R(18, "Waywarden's Cliff-Cloak", "back", "of the Eagle", "Dun-coloured and weather-beaten. It disappears on a canyon wall, which is the point."),
         R(18, "Ramp-Guard Spear", "main_hand", "of the Soldier", "Long enough to reach over a rail. Short enough to still stab someone.", "polearm"),
         R(18, "Rimstone Tread-Boots", "feet", "of the Bear", "Ribbed soles. They grip rock like it owes them money.", "mail")],
        nxt="sb_geodes_for_the_warden"))
    a(Q("sb_geodes_for_the_warden", "Geodes for the Warden", G, 18,
        ("The gravel skitterers of the Rift floor carry geodes in their shells like pockets. Brakka's wardens have "
         "learned that the crystals inside hum when a rockfall is about to happen. A string of them along the ramp "
         "would be worth a warden's life. They are, unhappily, worth a skitterer's too."),
        [dict(type="fetch", target="rift_geode", count=6)],
        ("Glittering things inside the shell, you can't miss them. Six geodes. "
         "And if the skitterer objects, don't take it personally."),
        ("They hum! Listen to that. That's one fewer funeral this season. Take this."),
        [R(18, "Geode-Studded Bracers", "wrist", "of the Beast", "Leather bound with rock-crystal. They hum a little. They've never told anyone why.", "leather"),
         R(18, "Warden's Rockfall Charm", "neck", "of the Bear", "A string of tiny geodes. It tinkles before a slide. The tinkle is the warning."),
         R(18, "Canyon-Slate Shield", "off_hand", "of Blocking", "A flat slab of slate, hand-fitted. Heavy, honest, impossible to leave behind.", "shield")],
        nxt="sb_teeth_in_the_canyon"))
    a(Q("sb_teeth_in_the_canyon", "Teeth in the Canyon", G, 19,
        ("The sabertooths came down out of the high rock three weeks ago. A caravan of kodo-haulers lost two animals "
         "and a driver on the ramp, and the survivors swear something bigger than a sabertooth watches from the "
         "ledges. Dustmaw. Brakka has heard the name before. She'd hoped it was a story."),
        [kill("Rift Sabertooth", 6), boss("Dustmaw the Rift-Lurker")],
        ("Six cats first - they're the sure thing. Dustmaw, if he shows himself, is the reason. "
         "He's half the canyon's size and twice as stubborn."),
        ("Dustmaw. Dead. I'll hang a fang over the gate. You've earned a bigger share than that."),
        [R(19, "Sabertooth-Hide Jerkin", "chest", "of the Tiger", "Spotted pelt over riveted leather. It still smells like the cat.", "leather"),
         R(19, "Dustmaw-Tooth Dirk", "main_hand", "of the Assassin", "A fang as long as your hand, set in a wrapped grip. It still looks hungry.", "dagger"),
         R(19, "Canyon-Warden's Signet", "ring", "of the Soldier", "A plain band hammered from an old ramp-spike. It has held a lot of weight.")],
        nxt="sb_across_the_rift", xp=1260, gold=4800))
    a(Q("sb_across_the_rift", "Across the Rift", G, 19,
        ("Two ramps cross the Rift besides the Waystation's, and Brakka hasn't had a warden near either since the "
         "cliffhawks started. She wants eyes on both. Walk the west ramp, walk the east one, and tell her what you "
         "see. The Rift is wider than it looks, and it is always quieter than it should be."),
        [explore(100, 126, 9), explore(176, 142, 9)],
        ("West ramp first, then east. Look for hawks, cats and anything that shouldn't be there. "
         "Bones are normal. Fresh bones are not."),
        ("Both ramps passable. Good. The Waystation can breathe. Take this - and remember me kindly when you cross."),
        [R(19, "Rimrunner's Leggings", "legs", "of the Monkey", "Hide leggings with reinforced knees. For people who spend their lives climbing in and out of holes.", "leather"),
         R(19, "Waystation Warhorn", "neck", "of the Falcon", "A small horn on a cord. One blast gets the whole ramp's attention."),
         R(19, "Crossing-Keeper's Truncheon", "main_hand", "of Striking", "Short, heavy and well-balanced. Persuasive in a traffic dispute.", "mace_1h")],
        xp=1320, gold=5000))

    # ============================== BONEHUNTER RURK (Field of Giants) ==============================
    G = "sb_bonehunter"
    a(Q("sb_hyenas_in_the_bones", "Hyenas in the Bones", G, 18,
        ("Rurk collects bones. Giant bones, the kind that stick out of the Field of Giants like the ribs of a ship. "
         "Hyenas have made that harder. They've learned that a man with his arms full of bones is a man who "
         "cannot swing a spear, and they come in packs to prove it."),
        [kill("Giantbone Hyena", 8)],
        ("Spotted, patient, cheerful. Drive them off the bones. I'll make more of a living if I'm not being chased."),
        ("Mmm. Hear that? Nothing. You'd be surprised how nice that sounds. Take this."),
        [R(18, "Bonepicker's Padded Vest", "chest", "of the Monkey", "Lots of pockets. Each one smells of something dead.", "leather"),
         R(18, "Hyena-Tooth Hatchet", "main_hand", "of the Squire", "A small axe with a hyena tooth set in the pommel. It's a lucky tooth. Mostly.", "axe_1h"),
         R(18, "Marrow-Hardened Gauntlets", "hands", "of the Gorilla", "Bone plates over mail. They've seen a lot of marrow.", "mail")],
        nxt="sb_giants_knucklebones"))
    a(Q("sb_giants_knucklebones", "Giants' Knucklebones", G, 19,
        ("The old plain has more than bones. It has something that wears them. Dust-grey wraiths drift between the "
         "ribs, shouldering knuckles the size of anvils. Rurk wants those knuckles. Why? He won't say, and he "
         "pays well enough that you don't ask."),
        [dict(type="fetch", target="giant_knucklebone", count=6)],
        ("Bone-Dust Wraiths. They keep the knucklebones close, like a miser keeps coins. "
         "Take six. Don't let them take yours."),
        ("Six knucklebones. Look at the polish on that! Beautiful. Take this - I'll be busy carving."),
        [R(19, "Knucklebone-Linked Belt", "waist", "of the Bear", "Linked giant knuckle-plates. The belt weighs more than it should and holds up better than it looks.", "plate"),
         R(19, "Carver's Bone Wand", "ranged", "of Shadow Wrath", "A bone sliver carved with unfriendly little faces. They whisper when you aren't looking.", "wand"),
         R(19, "Giant's Memory Pendant", "neck", "of the Whale", "A tiny polished knuckle on a cord. It feels like being very, very small.")],
        nxt="sb_the_matriarchs_last_walk"))
    a(Q("sb_the_matriarchs_last_walk", "The Matriarch's Last Walk", G, 20,
        ("A herd-mother kodo has been walking the Field of Giants in circles for a season, goring anything that wanders "
         "close. The herders call her Old Mother Longhorn. She isn't mad. She lost a calf, and she's been looking "
         "for it ever since. Rurk won't do it himself. He thinks it'd be bad luck. He pays well, though."),
        [kill("Aged Kodo", 6), boss("Old Mother Longhorn")],
        ("Six of her herd, the old and sorry ones. Then her. Be quick about it. She's been grieving long enough."),
        ("It's done, then. Quietly, I hope. Take this. And say a word for her at the gate, if you've got one."),
        [R(20, "Herd-Mother's Horn Helm", "head", "of the Defender", "A horned helm shaped from a matriarch's horn. It's heavy, and it's warm, and it remembers.", "plate"),
         R(20, "Longhorn Calf-Cradle Cloak", "back", "of the Restorer", "Soft hide, long fur. It looks like it's meant to hold something small.", "cloth"),
         R(20, "Gorebreaker's Mace", "main_hand", "of the Champion", "A hard, curved horn bound to a haft. Not made to be gentle.", "mace_2h")],
        nxt="sb_thrumbone", xp=1400, gold=5200))
    a(Q("sb_thrumbone", "Thrumbone", G, 21,
        ("There is something in the Field of Giants that is older than the bones. The wraiths gather around it. "
         "It walks in a slow circle through the ribs, and the ground hums when it does. Rurk calls it Thrumbone. "
         "He's never seen it. He doesn't want to. He wants it gone."),
        [kill("Bone-Dust Wraith", 8), boss("Thrumbone the Ancient")],
        ("Wraiths first. Then, if you feel the ground start to sing, you've found him. "
         "I'd run, but that's why you're being paid."),
        ("The ground's gone quiet. First time in years. I... thank you. Take these. They belong to the plain now, and so do you."),
        [R(21, "Wraith-Hunter's Marrow-Staff", "main_hand", "of the Prophet", "A hollow giant femur, polished by a lot of wind. It sings if you hold it up to the sun.", "staff"),
         R(21, "Rattlebone Wraps", "wrist", "of the Necromancer", "Strings of small bones on cloth. They click in time with your heart.", "cloth"),
         R(21, "Giantbone Breastplate", "chest", "of the Juggernaut", "Sections of giant rib over iron. Bigger than it needs to be, tougher than it looks.", "plate")],
        xp=1520, gold=5600))

    # ============================== THORNWATCH RANGER OGGRA (Razorfen approach) ==============================
    G = "sb_thornwatch"
    a(Q("sb_skinners_trophy_cords", "Skinner's Trophy Cords", G, 19,
        ("Oggra keeps the thornwatch on the Razorfen approach and has done for four winters. Razormane skinners "
         "wander south of the Ridge now, braiding trophy cords out of whatever they kill. Oggra wants the cords. "
         "Not for the trophies - for the names knotted into them."),
        [dict(type="fetch", target="skinner_trophy_cord", count=6)],
        ("Look for the small bell on the cord. That's how they know each other. "
         "Six cords. Bring them back and I'll read what they say."),
        ("Names. Faces. A lot of dead rangers. I'll write to their families. Take this."),
        [R(19, "Thornwatch Ranger's Vest", "chest", "of the Hunt", "Boiled leather, sewn with thorn-wood buttons. Sharp edges, comfortable fit.", "leather"),
         R(19, "Ranger's Skinning Knife", "main_hand", "of the Bandit", "Narrow, curved, and extremely sharp. The grip is wrapped in a stranger's good intentions.", "dagger"),
         R(19, "Trophy-Cord Choker", "neck", "of the Tiger", "A braided cord with a single small bell. It isn't there to warn you. It's there to remind you.")],
        nxt="sb_the_boarhound_pack"))
    a(Q("sb_the_boarhound_pack", "The Boarhound Pack", G, 20,
        ("The Razormane keep boarhounds - low, bristled, built for charging through thorn. They've started to hunt "
         "in packs along the ridge, driven by a quilboar handler who is a lot better at it than Oggra would like. "
         "Hounds and handlers both."),
        [kill("Blackthorn Boarhound", 6), kill("Razormane Stalker", 6)],
        ("Hounds to the west of the ridge, stalkers in the thorns behind them. Twelve in all. "
         "And if you find the handler, I'd like to hear about it."),
        ("Better. The ridge sounds different. I think I can hear the birds again. Take this."),
        [R(20, "Boarhound-Hide Bracers", "wrist", "of the Wolf", "Tough bristled hide, hard to cut and harder to wear to a formal occasion.", "leather"),
         R(20, "Thornwatch Spear-Thrower", "ranged", "of the Marksman", "A short bow of bent thornwood. It's light and fast. It hates being dropped.", "bow"),
         R(20, "Stalker-Cut Pauldrons", "shoulder", "of the Falcon", "Mail over leather with thorn-points riveted in. They make for a respectful hug.", "mail")],
        nxt="sb_skinwalker_garn"))
    a(Q("sb_skinwalker_garn", "Skinwalker Garn", G, 21,
        ("There's a story in the Ridge: a Razormane named Garn, who skins animals and wears what he takes. "
         "Oggra thought it was folklore until a ranger came back with half his coat missing. Garn works with seers, "
         "so Oggra wants the seers dealt with first."),
        [kill("Razormane Seer", 6), boss("Skinwalker Garn")],
        ("Seers first, they're his eyes. Then Garn. Watch his hands - he can wear a face the way you'd wear a hat."),
        ("Garn's dead. The Ridge feels lighter. Take this - keep it close, and don't let anyone peel your coat."),
        [R(21, "Garn-Slayer's Patchwork Leggings", "legs", "of the Hunt", "Hide in three colours. They look good, if you can ignore the stitching.", "leather"),
         R(21, "Garn's Flensing Hook", "main_hand", "of the Assassin", "A curved blade for lifting pelts. It could also lift other things.", "dagger"),
         R(21, "Many-Hide Cloak", "back", "of the Monkey", "A cloak sewn from several different animals. Uncomfortably well-made.", "leather")],
        nxt="sb_the_bramble_court", xp=1480, gold=5400))
    a(Q("sb_the_bramble_court", "The Bramble Court", G, 22,
        ("South of Oggra's post the thorns grow thick and the quilboar thicker. A Bristleback matriarch, Durga, "
         "has taken the Razorfen approach for her court. She's grown her bramble-guard around her like a hedge. "
         "Oggra wants the hedge cut and the queen put in the ground."),
        [kill("Razorfen Bramble-Guard", 8), kill("Thornhide Boar", 6), boss("Bramblequeen Durga")],
        ("Guards, then boars, then the queen. The thorns bite. The quilboar bite harder. Stay on the dry ground."),
        ("The Bramble Court is over. The approach is open. You've done more for the Barrens than a battalion. Take these."),
        [R(22, "Bramblequeen's Thorned Staff", "main_hand", "of Nature's Wrath", "A staff of grown thorn. It's alive. It's a little offended.", "staff"),
         R(22, "Bramble-Court Hood", "head", "of the Invoker", "A hood of woven vine. It sprouts small flowers when you cast something kind.", "cloth"),
         R(22, "Thornhide Warplate", "chest", "of the Bastion", "Plate studded with sharpened thorns. They didn't have to do that, but they did.", "plate")],
        xp=1620, gold=6000))

    # ============================== DIG-SCOUT TARRIK (Bael Modan) ==============================
    G = "sb_modan_scout"
    a(Q("sb_the_pit_at_bael_modan", "The Pit at Bael Modan", G, 19,
        ("The dwarves at Bael Modan have been digging for years, and the pit keeps getting wider. Tarrik watches "
         "from the rim and has counted heads. Every month there are more miners and the hole is deeper. "
         "He'd like fewer miners. He'd like to find out why they're digging so fast."),
        [kill("Dwarf Miner", 8)],
        ("Eight miners. They're not soldiers, but they swing a pick like they mean it. "
         "Thin them out and keep an eye on the pit. There's something at the bottom."),
        ("Eight down. And the pit's still going. They didn't even stop to look. That's what worries me. Take this."),
        [R(19, "Scout's Rimwalker Boots", "feet", "of the Eagle", "Thick-soled, quiet and easy to run in. A scout's best friend.", "leather"),
         R(19, "Quarry-Edge Short-Sword", "main_hand", "of the Soldier", "A short blade with a notch in it from hitting rock. Not a very good rock-breaker.", "sword_1h"),
         R(19, "Dig-Watcher's Spyglass", "neck", "of the Hunt", "A tiny brass spyglass on a cord. You can see a surprising amount through it.")],
        nxt="sb_golem_cores"))
    a(Q("sb_golem_cores", "Golem Cores", G, 20,
        ("The dwarves have built golems to haul rock. Stone ones, grey and square, thumping up and down the "
         "terraces. They obey orders and never tire. Tarrik wants to know how. He'd settle for a piece of one."),
        [dict(type="fetch", target="golem_core_shard", count=5)],
        ("Crack a golem. There's a core in the chest, glowing. Bring me five shards. "
         "Don't try to think about what they're running on."),
        ("Five. Interesting. They're running on... nothing. Or something that thinks it's nothing. I'll send word north. Take this."),
        [R(20, "Core-Shard Spellblade", "main_hand", "of the Sorcerer", "A short blade set with a glowing shard. It hums when you cast.", "sword_1h"),
         R(20, "Golemstone Gauntlets", "hands", "of the Bulwark", "Stone-faced plate. They don't scrape. They crush.", "plate"),
         R(20, "Quarry-Dust Mantle", "shoulder", "of the Archmage", "Grey cloth, stiff with dust. It shakes off magic better than it shakes off dirt.", "cloth")],
        nxt="sb_the_overseers"))
    a(Q("sb_the_overseers", "The Overseers", G, 21,
        ("Behind every dwarven digger is a man with a whip. The overseers keep the miners moving, and the "
         "engineers keep the overseers supplied. Tarrik thinks if he can break the middle of the chain, "
         "the rest will fall apart. He also thinks you're the person to do it."),
        [kill("Modan Overseer", 6), kill("Dwarf Engineer", 6)],
        ("Overseers wear red sashes. Engineers carry wrenches the size of your arm. "
         "Take both out and the pit's labour grinds to a halt."),
        ("The pit's gone quiet. Whole terraces idle. Nice work. There's one more thing to chase. Take this first."),
        [R(21, "Overseer's Brassbound Vest", "chest", "of the Tiger", "Leather with brass studs. Good for crowd control and intimidation.", "leather"),
         R(21, "Engineer's Heavy Wrench", "main_hand", "of the Gladiator", "A wrench you can break a skull with. It was designed for pipes.", "mace_2h"),
         R(21, "Rivet-Studded Belt", "waist", "of the Falcon", "Mail links on a studded strap. It holds everything you own, and all of it rattles.", "mail")],
        nxt="sb_grubbs_ledger"))
    a(Q("sb_grubbs_ledger", "Grubb's Ledger", G, 21,
        ("Foreman Grubb Deepdelver has run the pit since before the Keep was built. He keeps a ledger: ore, "
         "workers, accidents. Tarrik wants every page. A man who counts that carefully is a man who knows what "
         "he's counting for."),
        [dict(type="fetch", target="dig_ledger_page", count=4), boss("Foreman Grubb Deepdelver")],
        ("Pages from the overseers' satchels, and Grubb himself if he comes up for air. "
         "He's stubborn. He's also paid by the cubic yard."),
        ("Look at these numbers. They've been digging for something specific. I don't know what, but they know where. "
         "Take your reward. I'll write this up."),
        [R(21, "Quarry-Boss's Iron Cap", "head", "of the Bulwark", "A stout iron cap with a lantern-hook. Dented from every ceiling in the quarry.", "plate"),
         R(21, "Ledger-Keeper's Wraps", "wrist", "of the Mind's Eye", "Cloth wraps stitched with a tally pattern. Counting suits you.", "cloth"),
         R(21, "Quarry-Breaker's Pick", "main_hand", "of the Champion", "A heavy pick with a short haft. It was used for digging, but it works for other things too.", "axe_1h")],
        xp=1500, gold=5500))

    # ============================== SPY ZHUUL (Bael'dun Keep) ==============================
    G = "sb_keep_spy"
    a(Q("sb_eyes_on_the_gate", "Eyes on the Gate", G, 21,
        ("Zhuul lies in the grass east of Bael'dun Keep with a spyglass and a bad attitude. The dwarves "
         "have turned the keep into a proper fortress - riflemen on the walls, patrols in the yard. "
         "He needs someone to scout the gate and thin out the riflemen before they spot him."),
        [explore(113, 36, 10), kill("Bael'dun Rifleman", 6)],
        ("Walk up to the gate. Look. Come back. If a rifleman objects, shoot him first. "
         "I'd go myself, but I'd leave a trail. Trolls are tall, mon."),
        ("Good. Good. Gate's guarded, but not as well as they think. Take this."),
        [R(21, "Spy's Silent Vest", "chest", "of the Monkey", "Soft hide, dyed in the colours of dusk. It disappears in grass and in rumours.", "leather"),
         R(21, "Rifleman-Bane Crossbow", "ranged", "of the Marksman", "Light, quiet and fast to reload. It was built for one thing.", "crossbow"),
         R(21, "Gate-Watcher's Signet", "ring", "of the Falcon", "A narrow band with a little peephole. You can almost see through it.")],
        nxt="sb_mastiffs_at_the_gate"))
    a(Q("sb_mastiffs_at_the_gate", "Mastiffs at the Gate", G, 22,
        ("The dwarves keep mastiffs at the Keep. Big, loud, mean and loyal. They've started to range out past "
         "the walls, and one of them found Zhuul's last lean-to. He'd like the dogs gone, and he'd like the "
         "dispatches they've been guarding. A hound isn't a good postman."),
        [kill("Keep Mastiff", 6), dict(type="fetch", target="keep_dispatch", count=4)],
        ("Mastiffs, and the sergeants that walk them. Sergeants carry dispatches. "
         "Bring me four. I don't read dwarvish, but I know a man who does."),
        ("Four dispatches. Orders for the east gate. The dwarves are digging in. Take this."),
        [R(22, "Mastiff-Tamer's Leggings", "legs", "of the Beast", "Heavy mail with leather straps. Whatever you walk, it walks where you tell it.", "mail"),
         R(22, "Dispatch-Runner's Cloak", "back", "of the Monkey", "Light, fast and quiet. It doesn't flap. It doesn't dare.", "leather"),
         R(22, "Keep-Hound Fang Dagger", "main_hand", "of the Bandit", "A fang set in a bone hilt. A trophy, and a warning.", "dagger")],
        nxt="sb_cut_the_fuse"))
    a(Q("sb_cut_the_fuse", "Cut the Fuse", G, 22,
        ("Bael'dun's explosives experts run a charge-line to the east gate. If it's fired, it'll bring the cliff "
         "down on the Waystation road. Zhuul wants the experts gone and the charges in his hands before that "
         "happens. He knows what he'll do with them."),
        [kill("Dwarf Explosives Expert", 8), dict(type="fetch", target="powder_charge", count=5)],
        ("Experts, with the little red hats. Take their charges, and don't drop them. "
         "I know that sounds obvious. It's not, if you've met a dwarf."),
        ("Five charges, all intact. I'm impressed. Don't tell anyone I said so. Take this."),
        [R(22, "Fuse-Cutter's Gloves", "hands", "of the Duelist", "Thin leather, thick insulation. Made for people who do delicate work near explosives.", "leather"),
         R(22, "Sapper's Powder-Horn", "neck", "of the Sorcerer", "A brass horn on a chain. It never explodes. It threatens to."),
         R(22, "Blast-Blackened Mail Hood", "head", "of the Wolf", "Scorched mail with a leather liner. It remembers every explosion, and forgives none.", "mail")],
        nxt="sb_ironvein"))
    a(Q("sb_ironvein", "Sergeant Ironvein", G, 23,
        ("Sergeant Ironvein runs the Keep's east wall. He drills the riflemen, walks the mastiffs and "
         "hammers every plan flat. Zhuul says if Ironvein falls, the east gate falls. Zhuul has been wrong "
         "before, but he's very sure about this one."),
        [kill("Bael'dun Sergeant", 6), boss("Sergeant Ironvein")],
        ("Sergeants on the walls. Ironvein among them, if you listen for the hammer. "
         "Dwarves fight better in lines. Break the line."),
        ("Ironvein down. The east gate's lost its anchor. This is going to hurt them. Take this - you've earned it."),
        [R(23, "Ironvein's Gatekeeper Plate", "chest", "of the Defender", "Thick dwarven plate with a vein of bright ore. It rings when struck, and holds.", "plate"),
         R(23, "Sergeant's Marching Axe", "main_hand", "of the Soldier", "A short axe built for crowded places. Fast, honest, and meaner than it looks.", "axe_1h"),
         R(23, "Keep-Marcher's Ring", "ring", "of the Bear", "A band of dark iron. It looks heavy and feels reassuring.")],
        xp=1700, gold=6200))

    # ============================== HUNTRESS ALAMIR (Hoodoo Spires / Raptor Grounds) ==============================
    G = "sb_hoodoo_huntress"
    a(Q("sb_windspire_harpies", "Windspire Harpies", G, 20,
        ("The spires in the north-east are full of wind and voices. Harpies nest in the hollows, shrieking down "
         "at anyone who passes below. Alamir has hunted them for a season. Her arrows are running low and "
         "her patience's already gone."),
        [kill("Windspire Harpy", 8)],
        ("Feathers, claws, a lot of noise. Eight of them, from the hollows on the east side. "
         "Don't stand under the spires. They drop things."),
        ("Quiet at last. You could almost hear yourself think. Take this."),
        [R(20, "Harpy-Feather Mantle", "shoulder", "of the Eagle", "Soft down and long flight feathers. It rustles when you aren't moving.", "leather"),
         R(20, "Spire-Hunter's Shortbow", "ranged", "of the Marksman", "A light bow cut for shooting at things overhead. It forgives mistakes.", "bow"),
         R(20, "Windcut Greaves", "legs", "of the Falcon", "Mail leggings with wind-cut slits. They breathe in the heat and still turn a blade.", "mail")],
        nxt="sb_voices_in_the_spires"))
    a(Q("sb_voices_in_the_spires", "Voices in the Spires", G, 21,
        ("The wind sings through the hoodoo spires, and the harpy windcallers sing with it. Where they sing, the "
         "dust gets up and turns on you. Alamir wants the windcallers silenced and the crystals they carry brought "
         "to her. Crystals sing, too. They'd better do it for her than for the harpies."),
        [dict(type="fetch", target="spire_wind_crystal", count=5), kill("Hoodoo Dust Devil", 6)],
        ("Windcallers carry crystals, the size of your thumb. Dust devils follow the singing. "
         "Take the crystals, break the devils."),
        ("They're singing in my pocket. It's... not unpleasant. Take this, and stop humming."),
        [R(21, "Windcaller's Crystal Wand", "ranged", "of Nature's Wrath", "A sliver of windspire crystal in a bone handle. It hums a tune you almost know.", "wand"),
         R(21, "Dust-Devil Wraps", "wrist", "of the Elder", "Fine cloth that eddies faintly in a still room. Unsettling and weirdly comforting.", "cloth"),
         R(21, "Huntress's Spire-Cloak", "back", "of the Hunt", "Light, quiet and sand-coloured. A cloak for people who prefer not to be seen.", "leather")],
        nxt="sb_skyshriek"))
    a(Q("sb_skyshriek", "Skyshriek", G, 22,
        ("At the heart of the spires is a hollow where the wind never stops, and a harpy matron who has "
         "named herself for it. She commands the windcallers and sets the dust devils loose. "
         "Alamir wants her gone before the next storm."),
        [explore(212, 46, 8), boss("Skyshriek Matron")],
        ("The hollow is at the arch, near the east edge. Look for the biggest nest. "
         "She'll scream. Ignore it."),
        ("The wind's dropped. Listen. That's the quietest the spires have been in years. Take this."),
        [R(22, "Matron's Storm-Feather Wand", "ranged", "of the Archmage", "A long feather tipped with a spark. It crackles when you point it.", "wand"),
         R(22, "Spire-Weave Robes", "chest", "of the Seer", "Light cloth that doesn't catch on thorns or ideas.", "cloth"),
         R(22, "Skyshriek-Talon Spear", "main_hand", "of the Hunt", "A long spear tipped with a harpy talon. It screams on release.", "polearm")],
        nxt="sb_the_raptor_cull", xp=1580, gold=5800))
    a(Q("sb_the_raptor_cull", "The Raptor Cull", G, 21,
        ("South of the spires lies the Raptor Grounds, a long valley between two ridges where the Sunscale "
         "raptors nest. Alamir is a hunter, and a hunter respects a cull. The grounds are overfull this season. "
         "Too many stalkers, too many lashtails, and not enough prey to go around."),
        [kill("Sunscale Stalker", 8), kill("Sunscale Lashtail", 6)],
        ("Stalkers on the ridges, lashtails in the valley. Fourteen in all. "
         "Leave the eggs. I won't have it said I broke the balance."),
        ("Fourteen. Good. The valley can breathe. Take this."),
        [R(21, "Raptor-Scale Jerkin", "chest", "of the Hunt", "Overlapping scales over soft hide. It sheds sand and the occasional dagger.", "leather"),
         R(21, "Cullmaster's Longbow", "ranged", "of the Marksman", "A strong longbow strung with raptor sinew. It remembers its prey.", "bow"),
         R(21, "Lashtail-Barbed Gloves", "hands", "of the Tiger", "Gauntlets barbed with lashtail spines. Use caution when applauding.", "mail")],
        nxt="sb_razorbeak"))
    a(Q("sb_razorbeak", "Razorbeak the Nestbreaker", G, 23,
        ("A raptor alpha called Razorbeak has been raiding other nests - not for food, for eggs. "
         "She breaks them, one by one, and the grounds are going quiet for it. Alamir hates waste. "
         "She hates it more when it's deliberate."),
        [kill("Nest-Mother Raptor", 4), boss("Razorbeak the Nestbreaker")],
        ("Nest-mothers, four of them, protecting what's left. Then the alpha. "
         "She's fast. Don't stand still."),
        ("Razorbeak's gone. The nests will recover. Take this, with my thanks."),
        [R(23, "Nestwarden's Raptorbone Bow", "ranged", "of the Marksman", "Strung with sinew from the alpha herself. It twangs like something remembering how to hunt.", "bow"),
         R(23, "Nestbreaker's Scale Vest", "chest", "of the Tiger", "Overlapping raptor scales over soft hide. It sheds sand and rumours.", "leather"),
         R(23, "Cloak of the Spared Egg", "back", "of the Eagle", "Feathered and speckled. Smells faintly of gratitude.", "cloth")],
        xp=1680, gold=6100))

    # ============================== EXCAVATOR FIZZWICK (Sinkhole Crater) ==============================
    G = "sb_crater_digger"
    a(Q("sb_something_below", "Something Below", G, 22,
        ("Fizzwick Boltcog found the crater last spring and has been digging ever since. He found a stair at the "
         "bottom, a lot of glittering rock and, three days ago, what he describes as 'a series of unfortunate "
         "bites.' Sinkhole burrowers came up through the floor. They're still coming."),
        [kill("Sinkhole Burrower", 8)],
        ("Little brown things, lots of legs, extremely rude. Thin them out and I'll get back to my digging. "
         "No, you can't see what I've found."),
        ("Eight! Marvellous. I've sorted three crates already. Don't look at them. Take this."),
        [R(22, "Excavator's Padded Coat", "chest", "of the Bear", "Thick hide with extra pockets. It smells of dirt and ambition.", "leather"),
         R(22, "Boltcog's Dig-Hammer", "main_hand", "of the Squire", "A stout hammer with a pointed end. Good for rocks, locks and people who ask the wrong questions.", "mace_1h"),
         R(22, "Burrower-Chitin Bracers", "wrist", "of the Defender", "Plates of hardened shell, strapped over mail. They hurt anything that hurts them.", "mail")],
        nxt="sb_tunnel_guards"))
    a(Q("sb_tunnel_guards", "Tunnel-Guards", G, 23,
        ("Below the burrowers are the tunnel-guards: bigger, harder, and a great deal better organised. "
         "They're keeping Fizzwick away from the stair, and he doesn't enjoy being kept away from anything. "
         "He'd like the guards dead, and a few of their chitin plates for his shop."),
        [kill("Brood Tunnel-Guard", 6), dict(type="fetch", target="tunnel_guard_chitin", count=5)],
        ("Six guards, five plates. They ring when you tap them, don't tap them. "
         "Whatever answers, you don't want to meet."),
        ("Five plates! They'll fetch a fortune in Ratchet. Don't tell my partner. Take this."),
        [R(23, "Tunnel-Guard Chitin Cuirass", "chest", "of the Juggernaut", "Layered chitin over plate. It rings when you hit it, and it hits back.", "plate"),
         R(23, "Brood-Slayer's Blade", "main_hand", "of the Champion", "A long blade ground from a tunnel-guard's claw. The edge is chitin-fine.", "sword_2h"),
         R(23, "Shell-Plate Mantle", "shoulder", "of the Elder", "Light chitin over cloth. Insects tend to leave you alone while you wear it.", "cloth")],
        nxt="sb_vexa", xp=1660, gold=6000))
    a(Q("sb_vexa", "Vexa the Tunnel-Queen", G, 24,
        ("At the bottom of the crater, past the guards, sits the queen. Her name is Vexa, and she has made the "
         "Sinkhole her own. The Broodspiral below is her nursery. Fizzwick wants to get to the stair, and, "
         "to be fair, he'd like the nursery safe. He just can't do either until she's gone."),
        [explore(225, 212, 8), boss("Vexa the Tunnel-Queen")],
        ("Go down into the crater. Find the nest at the centre. "
         "She's big, she's angry and she will not stop. Neither should you."),
        ("The queen is dead. The stair's open. I'm going to need a bigger shovel. Take this, with my deepest thanks and a cheque I'll never cash."),
        [R(24, "Queen-Slayer's Brood-Mace", "main_hand", "of the Spell Breaker", "A scepter of fused chitin with a pulsing sac at the tip. Do not squeeze it.", "mace_1h"),
         R(24, "Tunnel-Slayer's Chitin Cowl", "head", "of the Beast", "Hard shell plates, stitched with sinew. The cavities hold amber, and the amber holds something.", "mail"),
         R(24, "Hive-Amber Signet", "ring", "of the Restorer", "A bead of resin, warm to the touch. Something small inside kicks whenever you heal.")],
        xp=1800, gold=6600))
    # ============== FIZZWICK, PART TWO: THE STAIR (Broodspiral dungeon chain, independent of the crater chain) ==============
    # Fizzwick's crater chain above ends with the stair open; this chain sends you down it.  Kills only count inside the dungeon.
    a(Q("sb_down_the_stair", "Down the Stairs", G, 20,
        ("The stair at the bottom of the crater doesn't go down so much as around. Fizzwick has measured it twice "
         "and gotten two different answers, which he finds deeply insulting. Drones and skulkers patrol the outer ring. "
         "Thin them out so he can chalk the walls."),
        [kill("Hive Drone", 8, zone=BS), kill("Hive Skulker", 6, zone=BS)],
        ("Take the stair at the crater's edge and keep to the right-hand wall. It's a spiral. "
         "Stay with it and it'll bring you to the middle, whether you like it or not."),
        ("Eight drones, six skulkers. You came back with all your fingers. I'm adding that to my map. Take this."),
        [R(20, "Chalkmarker's Hive-Coat", "chest", "of the Bear", "Quilted hide, chalk-stained at the cuffs. Every pocket has a drawing of a tunnel in it.", "leather"),
         R(20, "Outer-Ring Spike", "main_hand", "of the Soldier", "A drone's barb on a hammer-handle. Gets the point across.", "dagger"),
         R(20, "Stair-Walker's Amber Loop", "ring", "of the Eagle", "A little bead of resin on a wire. Warm, in a cold place.")],
        nxt="sb_amber_for_the_taking", xp=1380, gold=4800))
    a(Q("sb_amber_for_the_taking", "Amber for the Taking", G, 21,
        ("The hive builds in amber, and amber, Fizzwick explains at length, is worth more by the ounce than any of "
         "the things he's dug up so far. Weavers and spitters carry the best shards in their glands. "
         "He'd like six. Don't ask what he does with them."),
        [fetch("hive_amber_shard", 6)],
        ("Hive Weavers spin it, Resin Spitters spit it. Either will do. "
         "Don't drop them. They go off, in a sense."),
        ("Six! Perfect clarity, and the one in the middle appears to be waving. Take this, I need to sit down."),
        [R(21, "Amber-Glass Cowl", "head", "of the Sorcerer", "A cap of cloth with a lens of hive-amber. Everything you look at takes on a golden cast, and a faint resentment.", "cloth"),
         R(21, "Spitter-Hide Gauntlets", "hands", "of the Tiger", "Resin-hardened hide. Sticky only if you want them to be.", "leather"),
         R(21, "Fizzwick's Pocket Bulwark", "off_hand", "of the Defender", "A tiny round shield of pressed amber. Very sturdy for something so small.", "shield")],
        nxt="sb_the_tenders", xp=1440, gold=5100))
    a(Q("sb_the_tenders", "The Tenders", G, 22,
        ("Past the outer ring the tunnel widens into a brood chamber, and the things that tend it are called "
         "Brood Tenders. They are quite gentle. Fizzwick has been told this by someone who isn't coming back. "
         "The Broodkeeper sits at the head of the chamber. Kill the tenders; then kill it."),
        [kill("Brood Tender", 6, zone=BS), boss("The Broodkeeper", zone=BS)],
        ("Six tenders, then the Broodkeeper. It sits behind a pair of resin pillars. "
         "Stay out of the green. The green is not for you."),
        ("The Broodkeeper's dead and the second ring's open. I'm very proud of you and also deeply afraid. Take this."),
        [R(22, "Keeper's Resin-Leggings", "legs", "of the Restorer", "Cloth stiffened with brood-resin. It cracks when you kneel, which is a good reason to stay standing.", "cloth"),
         R(22, "Tender-Plate Gauntlets", "hands", "of the Juggernaut", "Chitin over steel. Every plate remembers a different hive.", "plate"),
         R(22, "Brood-Chamber Thumper", "main_hand", "of the Squire", "A carapace-headed mace. Hits like a tunnel collapsing.", "mace_1h")],
        nxt="sb_screen_the_queen", xp=1500, gold=5400))
    a(Q("sb_screen_the_queen", "Screen the Queen", G, 23,
        ("The last ring before the Queen's Hollow is the Larval Screen: crushers, larvae, and a great pale guard "
         "who watches the throne from the dark. If Fizzwick's maps are right, the Queen sits on the other side. "
         "He'd rather you cleared the screen than found out how right his maps are."),
        [boss("Larval Broodguard", zone=BS), kill("Carapace Crusher", 6, zone=BS)],
        ("Crushers first, then the Broodguard. It doesn't move much, and it hits like a falling roof. "
         "The Queen's behind it. Not today, though. Today you clear the screen."),
        ("The screen is down and you're alive. I'll chalk the throne room in on my next trip. Take this, with my gratitude and my apologies in advance."),
        [R(23, "Screenwarden's Crushing Axe", "main_hand", "of the Champion", "A two-handed axe with a carapace-plate head. The Broodguard wore the blade first.", "axe_2h"),
         R(23, "Larval-Silk Mantle", "shoulder", "of the Sorcerer", "Pale silk, spun by something that should have been a moth. Cool to the touch.", "cloth"),
         R(23, "Hollow-Edge Spaulders", "shoulder", "of the Elder", "Mail laced with hive-amber. A faint glow when anything ugly gets close.", "mail")],
        xp=1620, gold=5800))
    # ============== OGGRA, PART TWO: THE KRAUL (Razorfen Kraul dungeon chain; kills only count inside it) ==============
    # Oggra's thornwatch chain above clears the approach; the Kraul itself is the hill under it (entrance (55,175), south of her post).
    G = "sb_thornwatch"
    a(Q("sb_into_the_kraul", "Into the Kraul", G, 25,
        ("Every thorn on this ridge grows out of the same root, Oggra says, and the root is the Kraul: the quilboar "
         "hill-warren south of her post, with a mouth of bramble and a throat of boars. She has watched it for four "
         "winters and it has never looked as busy as this. She wants the gate guard thinned before anything else."),
        [kill("Razorfen Spearhide", 8, zone=RZ), kill("Razorfen Beast Trainer", 6, zone=RZ)],
        ("The gate is south of my post, under the thorns. Spearhides at the door, beast trainers just inside. "
         "Be quick, and keep your back to the wall. The wall is mostly thorn."),
        ("Eight spears, six whips, and all your fingers. You'll do. Take this. We're going deeper."),
        [R(25, "Thornwatch Scout's Vest", "chest", "of the Falcon", "Quilted hide with thorn-guards sewn into the shoulders. It smells of the hill and of Oggra's tobacco.", "leather"),
         R(25, "Bramble-Cutter", "main_hand", "of the Squire", "A short hooked blade for cutting thorn, and, if need be, quilboar.", "axe_1h"),
         R(25, "Gatekeeper's Bone Ring", "ring", "of the Eagle", "A ring of carved bone. The Spearhide who owned it was no longer using it.")],
        nxt="sb_seed_and_thorn", xp=1560, gold=5500))
    a(Q("sb_seed_and_thorn", "Seed and Thorn", G, 26,
        ("The thorns on the ridge are not wild. The geomancers inside the Kraul seed them, one barbed pod at a time, "
         "and every pod is a little more hill the quilboar own. Oggra wants six seed-pods for her notes, and the "
         "geomancers who make them put in the ground."),
        [kill("Razorfen Geomancer", 6, zone=RZ), fetch("kraul_seed_pod", 6)],
        ("Geomancers carry the pods, and they are almost always on the ground, working. "
         "Don't drop them. They go off, in a sense."),
        ("Six seed-pods. The thorn's spreading faster than I'd feared, and now I can prove it. Take this."),
        [R(26, "Geomancer's Thorn-Robe", "chest", "of the Sorcerer", "A robe stitched with living briar. Each thorn points away from the wearer, which is considerate.", "cloth"),
         R(26, "Seedcaller's Wand", "ranged", "of Nature's Wrath", "A wand of dried seed-pod, still faintly warm. It clicks like an awakening plant.", "wand"),
         R(26, "Root-Bound Gauntlets", "hands", "of the Bear", "Leather bound with root. They hold fast to whatever they grip.", "leather")],
        nxt="sb_the_vine_bridge", xp=1620, gold=5800))
    a(Q("sb_the_vine_bridge", "The Vine Bridge", G, 28,
        ("West of the first fork a rope-and-vine bridge crosses a drop to a platform, and on the platform lives "
         "Roogug, who has been ordering the hill's warriors about since before Oggra was a ranger. "
         "He's off the main road, which makes him safe to leave alone. Oggra would rather he were not left alone."),
        [kill("Razorfen Defender", 6, zone=RZ), boss("Roogug", zone=RZ)],
        ("The bridge is narrow. Don't fight on it. Wait for them on the platform, and Roogug will come to you. "
         "He's all muscle and no plan, so use that."),
        ("Roogug's down. The bridge is quiet, for the first time in my life. Take this, with my thanks."),
        [R(28, "Bridge-Warden's Vine-Hauberk", "chest", "of the Tiger", "Mail woven through with vine-rope. It creaks when you move and it dares you to climb something.", "mail"),
         R(28, "Roogug's Cudgel", "main_hand", "of the Champion", "A knotted club with iron studs. It makes a distinct, regrettable sound.", "mace_1h"),
         R(28, "Platform-Walker's Boots", "feet", "of the Falcon", "Soft leather boots, treaded for narrow places and falling.", "leather")],
        nxt="sb_two_speakers", xp=1740, gold=6300))
    a(Q("sb_two_speakers", "Two Speakers", G, 30,
        ("North of the fork the Kraul splits around the Thorn Court and two chieftains sit at either end of it. "
         "Aggem Thorncurse, west, who calls the boar-spirits; Death Speaker Jargba, east, who speaks for the dead "
         "and takes what they say very seriously. Both of them keep the hill's heartbeat. Stop either and it stumbles."),
        [boss("Aggem Thorncurse", zone=RZ), boss("Death Speaker Jargba", zone=RZ)],
        ("Both of them, in whichever order you like. Aggem's guards are beast-trainers with boars. "
         "Jargba's are Death's Head, with hexes. Don't fight both at once, and don't let either one finish a sentence."),
        ("Both of them! I'd call the hill's spirit broken, but I know better. Take this, and my respect."),
        [R(30, "Speaker's Hexbound Robes", "chest", "of the Archmage", "Cloth sewn with thorn and prayer-beads. It hums quietly with other people's voices.", "cloth"),
         R(30, "Boarspirit Greathelm", "head", "of the Defender", "A plate helm with a stylised boar-snout. The tusks are real, which is sad.", "plate"),
         R(30, "Thorncurse Hunter's Bow", "ranged", "of the Marksman", "A bow of ironwood thorn. It pulls hard and seldom misses.", "bow")],
        nxt="sb_the_pens_below", xp=1860, gold=6700, span=3))
    a(Q("sb_the_pens_below", "The Pens Below", G, 32,
        ("At the centre of the Kraul is the Boar Pens: a corral ring, stalls on every side, and in the middle, "
         "Overlord Ramtusk, who has been fattening his boars for a war for a decade. Oggra wants the pens broken "
         "before they open them."),
        [kill("Thornback Sow", 6, zone=RZ), boss("Overlord Ramtusk", zone=RZ)],
        ("Sows in the stalls, the Overlord in the ring. The ring has three gaps. Hold the south one and "
         "they'll come to you. Keep the sows off your back."),
        ("The Overlord's down and the pens are empty. I'll sleep tonight. Take this, you've earned it."),
        [R(32, "Boarlord's Tusk-Plate", "chest", "of the Bastion", "Plate grown over a pen-keeper's rib-guard. The tusk-spikes are decoration, mostly.", "plate"),
         R(32, "Pen-Breaker's Maul", "main_hand", "of the Gladiator", "A two-handed maul with a boar's skull for a head. It hits like a collapsing corral.", "mace_2h"),
         R(32, "Overlord's Warcloak", "back", "of the Eagle", "A heavy cloak of boar-hide. It rustles and whispers menacing little oaths.", "cloth")],
        nxt="sb_the_beast_pit", xp=1960, gold=7000))
    a(Q("sb_the_beast_pit", "The Beast Pit", G, 32,
        ("From the pens a narrow neck runs north-west, sealed by a ward and held by Ward-Keepers: the Beast Pit, "
         "where something called Agathelos has been fed on stolen kodo for years. The ward-stones keep it in. "
         "Take four and the ward falls, and then, Oggra says, you'll want to be ready."),
        [kill("Razorfen Ward-Keeper", 5, zone=RZ), fetch("ward_seal_stone", 4), boss("Agathelos the Raging", zone=RZ)],
        ("Ward-Keepers hold the neck. Break the stones, then go in. "
         "Agathelos is a beast, not a boar. Don't mistake one for the other. It isn't kind."),
        ("Agathelos is dead and the pit's open to the sun. I hope that rattles Charlga. Take this."),
        [R(32, "Pit-Warden's Stoneward Shield", "off_hand", "of Blocking", "A shield of warded stone. It still hums with the binding that held the beast.", "shield"),
         R(32, "Beastcaller's Fang-Dagger", "main_hand", "of the Assassin", "A dagger carved from a beast-pit fang. It likes your hand.", "dagger"),
         R(32, "Ward-Stone Pendant", "neck", "of the Whale", "A seal-stone pendant, still faintly warm. It dulls the blows you take.")],
        nxt="sb_razorflank", xp=1980, gold=7100))
    a(Q("sb_razorflank", "Razorflank", G, 34,
        ("At the top of the Kraul, on a platform of bones, sits Charlga Razorflank in a hut of thorn and tusk, "
         "and she has heard the pens fall, and the speakers die. Oggra says the hill's heart is hers. "
         "Take it, and the thorns will wither by spring."),
        [kill("Razorfen Totemic", 6, zone=RZ), boss("Charlga Razorflank", zone=RZ)],
        ("Totemics around her, and she mends them as fast as you cut them. Go for her first if you can. "
         "The thorns won't forgive you, but they'll stop."),
        ("Charlga's dead. The Kraul will take a generation to recover, if it does, and the ridge will breathe. "
         "Take this, with all the thanks a ranger has."),
        [R(34, "Razorflank's Thornweave Mantle", "shoulder", "of the Physician", "Cloth woven from living briar. It pulses faintly when something nearby needs healing.", "cloth"),
         R(34, "Chieftain's Thorn-Guard Greaves", "legs", "of the Juggernaut", "Plate legguards edged with thorn. Enemies bleed before they have the sense to run.", "plate"),
         R(34, "Agamaggan's Boarhide Belt", "waist", "of the Tiger", "A belt of ancient boar-hide, scarred and thick. It makes you feel hunted, and quick.", "leather"),
         R(34, "Quilboar Queen's Longbow", "ranged", "of the Marksman", "A great bow of quilboar-bone and sinew. It sings when strung.", "bow")],
        xp=2200, gold=8200, span=3))
    a(Q("sb_blind_hunter", "The Blind Hunter", G, 29,
        ("There's a hunter in the western galleries of the Kraul who has been blind for years and still never misses. "
         "Oggra has lost two scouts to him. She wants him stopped, and the handlers that guide him dead."),
        [kill("Razorfen Handler", 8, zone=RZ), boss("Blind Hunter", zone=RZ)],
        ("West gallery, past Aggem's pen. He listens for you. Don't stand still. "
         "Don't breathe loudly, either, if it comes to that."),
        ("The hunter's down, and I'll write to the families. Take this, and my thanks."),
        [R(29, "Listener's Quiver-Coat", "chest", "of the Marksman", "Soft leather, cut for quiet movement. It hushes the sound of your breath, and your boots.", "leather"),
         R(29, "Hunter's Blind Dagger", "main_hand", "of the Assassin", "A dagger with a handle wrapped in cord to find the grip by feel.", "dagger"),
         R(29, "Handlers' Bone Amulet", "neck", "of the Eagle", "A bone amulet, strung on sinew. It tingles when something nearby is lying.")],
        xp=1760, gold=6400))
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
    OUT.write_text(json.dumps({"quests": out}, indent=2, ensure_ascii=False) + "\n")
    print("southern barrens hub quests:", len(out), "items:", sum(len(q["unique_item_defs"]) for q in out))


if __name__ == "__main__":
    main()
