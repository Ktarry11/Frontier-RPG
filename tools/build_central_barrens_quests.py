"""
Central Barrens local quest hub (2026-10-21).  Idempotent: rewrites data/quests/central_barrens_hub.json.

    python3 tools/build_central_barrens_quests.py

(The 14 Orgrimmar / Taurajo / Ratchet-given Barrens quests in central_barrens.json are untouched; these are
the quests the zone itself gives, so the Barrens finally has a local hub of its own.)

MAP (300x300; full notes in tools/handbuilt_central_barrens.py)
  Herder Magra (142,82) north of the Crossroads under Sentinel Rocks; Kodo Graveyard (205,120) east of it.
  Plainswatcher Dorn (182,152) east road; Kolkar Outpost (222,160), Kolkar War Camp (238,112).
  Kranal Fiss (85,145) Grol'dom Farm, west road.  Keeper Ahnmar at the Shrine of the Fallen Warrior (52,143).
  Waterkeeper Sanu at Lushwater (88,206), SW oasis; Wailing Caverns mouth (75,223) just south of the bluff.
  Pilgrim-Warden Torga at the Forgotten Pools (96,94), NW.  Scout Zarla (72,70) on the road to Dreadmist Peak
  (cult den at (50,44)).  Ranger Kishi (146,234) between Bramblescar (130,250) and Agama'gor (170,250).
  Caravan-Master Dogan at Raider's Rest (203,217), SE oasis.  Bridgewarden Karga (262,33) at the Durotar landing.
Every giver has ONE chain; rares are paired with trash so the ~6 % roll never stalls a quest.
Rewards are hand-crafted with the real stat formulas (secondary stats, ilvl >= 10).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import item, kill, fetch   # noqa: E402

OUT = ROOT / "data/quests/central_barrens_hub.json"
Z = "central_barrens"


def boss(target):
    return dict(type="kill_boss", target=target, count=1)


def explore(x, y, radius=8):
    return dict(type="explore", target=Z, target_x=x, target_y=y, radius=radius)


def gather(target, count):
    return dict(type="gather", target=target, count=count)


def Q(qid, title, giver, lvl, desc, objs, accept, turnin, rewards, nxt=None, xp=None, gold=None, span=2):
    return dict(
        quest_id=qid, title=title, giver_npc_id=giver, zone=Z, level_min=lvl, level_max=lvl + span,
        description=desc, objectives=objs,
        reward_exp=xp or int(lvl * 58 + 40), reward_gold=gold or int(lvl * 240),
        accept_text=accept, turn_in_text=turnin, rewards=rewards, next_quest_id=nxt)


def quests():
    A = []
    a = A.append

    # ============================== HERDER MAGRA (kodo herd, north) ==============================
    a(Q("cb_strays_on_the_plain", "Strays on the Plain", "barrens_herder_1", 12,
        ("Magra Dustwalker has run kodo north of the Crossroads for twenty years, and it has never been this bad. "
         "Barrens hyenas have learned that a calf separated from the herd is a calf that does not come home. "
         "They shadow the herd at a distance, patient as a debt collector, and pick off whatever lags."),
        [kill("Barrens Hyena", 8)],
        ("Look out over the plain - brown-grey, spotted, grinning. Eight of them, and they will not run. "
         "They have never had a reason to."),
        ("That's quieter. Kodo don't flinch like that when something's after them - they just stop eating. "
         "They're eating again. Come back when you've got your breath, there's a bigger problem in the sky."),
        [item("Herder's Dust-Cloak", "back", "of the Monkey", 15,
              "Grey with a decade of kodo dust. It smells like work and it fits like work.",
              "Cloak (Agi/Sta)", armor="cloth", req=12),
         item("Calf-Guard Crook", "main_hand", "of the Soldier", 15,
              "A long hooked staff, scarred from pulling things out of ditches. Some of those things bit back.",
              "Polearm (Str/Sta)", weapon="polearm", req=12),
         item("Plainsrunner Boots", "feet", "of the Tiger", 15,
              "Hyena-hide soles. They don't squeak, which is the point.",
              "Leather Boots (Str/Agi)", armor="leather", req=12)],
        nxt="cb_thunder_on_the_wing"))
    a(Q("cb_thunder_on_the_wing", "Thunder on the Wing", "barrens_herder_1", 13,
        ("Something has been diving on the herd out of a clear sky: plains thunderhawks, hunting in pairs, leaving the "
         "calves scorched and the air smelling of storm. Magra's kodo don't spook at much, but they spook at that. "
         "She wants the hawks thinned and a few flight-feathers brought back, because a thunderhawk pinion on a "
         "herd-bell keeps the others away."),
        [fetch("thunderhawk_pinion", 6)],
        ("Pinions off the plains thunderhawks - the big ones, you'll know them by the crackle. "
         "Six feathers. Watch your hair; it will stand up."),
        ("Look at that - still sparks. These'll hang on the herd-bells by dusk. "
         "Come to me when you're tired of birds; there's a grey mesa to the east that wants a visit."),
        [item("Pinion-Bound Mantle", "shoulder", "of the Eagle", 16,
              "Charged feathers over hide. Walk fast in it and you can feel the weather change.",
              "Cloth Shoulders (Int/Sta)", armor="cloth", req=13),
         item("Hawkwing Short-Bow", "ranged", "of the Marksman", 16,
              "A short bow with a hawk's wing carved into the grip. It aims for you, if you let it.",
              "Bow (Agi/Sta/Hit)", weapon="bow", req=13),
         item("Storm-Tied Bracers", "wrist", "of the Beast", 16,
              "Mail links on a leather band. Static makes them chime.",
              "Mail Bracers (Agi/Sta)", armor="mail", req=13)],
        nxt="cb_sentinel_stingers"))
    a(Q("cb_sentinel_stingers", "Stingers at the Sentinels", "barrens_herder_1", 14,
        ("The Sentinel Rocks - the sandstone teeth north-west of the Crossroads - are the best shelter on the plains, "
         "and for three weeks no kodo has slept there. Redstone scorpids have claimed the crevices, and something "
         "bigger has claimed the scorpids. Magra says a brood-queen is nesting in the rocks."),
        [kill("Redstone Scorpid", 8), boss("Redrock Matriarch")],
        ("Red-brown, size of a dog, tail like a sickle. Eight of them, and the big mother if she shows her face. "
         "She will. They always do, when you've made a mess of her nursery."),
        ("Quiet in the rocks? Good. My herd will be glad of that shade. You've earned more than thanks."),
        [item("Redstone Carapace Vest", "chest", "of the Defender", 17,
              "Scorpid plate over a boiled-leather backing. It turns a blade like a tabletop turns a spoon.",
              "Mail Chest (Sta/Def)", armor="mail", req=14),
         item("Stinger-Tipped Spear", "main_hand", "of the Hunt", 17,
              "A scorpid stinger lashed to a spear shaft. It makes a sound when it enters. You'll remember it.",
              "Polearm (Agi/Sta)", weapon="polearm", req=14),
         item("Sentinel Stone Ring", "ring", "of the Owl", 17,
              "A chip of rock from the Sentinel pillars. Cool in summer. Warm in a fight.",
              "Ring (Int/Sta)", req=14)],
        nxt="cb_old_sunhide"))
    a(Q("cb_old_sunhide", "Old Sunhide", "barrens_herder_1", 14,
        ("Every herder's story has a villain. Magra's is a bull giraffe the height of a watchtower with a hide "
         "the colour of the dry grass he stands in. Old Sunhide doesn't hunt. He wanders. Wherever he wanders, "
         "kodo calves end up flat. She doesn't hold it against him, exactly. She's tired of burying calves."),
        [kill("Barrens Giraffe", 6), boss("Old Sunhide")],
        ("He walks the plain between here and the Crossroads. You'll see him a long way off, and you'll "
         "want to - nothing his size should sneak. Six of his herd first, to thin the cover. Then him."),
        ("Gone? ... Good. I won't say I'm not sorry. He was a good giraffe, in his way. Take these. "
         "They were my father's, and he'd have wanted them used."),
        [item("Sunhide Wanderer's Tunic", "chest", "of the Monkey", 17,
              "Tall-grass colours, cut for a person who spends a lot of time standing very still.",
              "Leather Chest (Agi/Sta)", armor="leather", req=14),
         item("Herder's Heavy Maul", "main_hand", "of the Gladiator", 17,
              "A thick-headed maul for driving stakes. Does a fair job on other things that stand in lines.",
              "Mace 2H (Str/Sta)", weapon="mace_2h", req=14),
         item("Talisman of the Long Grass", "neck", "of the Falcon", 17,
              "A pressed blade of dry grass in a glass bead. It always points the direction the wind will go.",
              "Necklace (Agi/Int)", req=14)],
        nxt="cb_kodo_graveyard", xp=1010, gold=3900))
    a(Q("cb_kodo_graveyard", "Where the Herd Goes to Die", "barrens_herder_1", 15,
        ("East of the Sentinel Rocks, the plain rises into a shallow bowl that the kodo have always walked into "
         "when it was their time. Magra has made that walk with three herds. Lately it's not quiet. "
         "The dead kodo don't stay dead, and the vultures have gotten bold."),
        [explore(205, 120, 12), kill("Kodo Wraith", 8), boss("Hollowhorn")],
        ("Walk in, look around, come back out - and bring me what the bowl's still holding. "
         "Wraiths first. The big horned one second, if he's still wandering."),
        ("Kodo are not meant to come back. Every one you put down is a favour. Take this, from the old herd."),
        [item("Boneyard Walker's Greaves", "legs", "of the Juggernaut", 18,
              "Kodo ribs over boiled hide. They creak. The creak, you will find, is somehow reassuring.",
              "Plate Legs (Str/Sta)", armor="plate", req=15),
         item("Wraith-Cut Hook-Blade", "main_hand", "of the Champion", 18,
              "A wraith's horn, ground to an edge. It's colder than horn should be.",
              "Axe 2H (Str/Crit)", weapon="axe_2h", req=15),
         item("Graveyard Dust Amulet", "neck", "of the Ironfur", 18,
              "A sealed vial of grey dust. Don't open it. Magra insists. Magra has opened it.",
              "Necklace (Sta/Armor)", req=15)],
        xp=1100, gold=4300, span=3))

    # ============================== PLAINSWATCHER DORN (Kolkar chain) ==============================
    a(Q("cb_smoke_on_horizon", "Smoke on the Horizon", "barrens_scout_2", 13,
        ("Plainswatcher Dorn can see a sandstorm coming from an hour away. He can't see why the smoke over the "
         "Kolkar outpost, due east on the long road, has turned from brown to black. A man on a ridge can only "
         "learn so much. He wants someone to walk down there and look."),
        [explore(222, 160, 10)],
        ("Follow the east road from the Crossroads till it forks off into trampled grass. That's their outpost. "
         "Look. Don't fight. Come back and tell me what you saw."),
        ("Twenty tents, a watchtower, and a war-drum. That's more than they had last season. "
         "The centaur are building - which means they intend to keep it. Next job's louder."),
        [item("Plainswatcher's Windcloak", "back", "of the Monkey", 16,
              "Dyed the exact colour of nothing. You can stand in it for an hour and no one blinks.",
              "Cloak (Agi/Sta)", armor="cloth", req=13),
         item("Spotter's Brass-Sight Bow", "ranged", "of the Marksman", 16,
              "A short bow with a brass sight someone added after the fact. Sights on bows are, apparently, a new idea.",
              "Bow (Agi/Sta/Hit)", weapon="bow", req=13),
         item("Dorn's Watch-Tunic", "chest", "of the Seer", 16,
              "Woven grass-cloth. It hums faintly when something big is coming.",
              "Cloth Chest (Int/Sta/MP5)", armor="cloth", req=13)],
        nxt="cb_taking_the_outpost", xp=870, gold=3150))
    a(Q("cb_taking_the_outpost", "Taking the Outpost", "barrens_scout_2", 14,
        ("The Kolkar outpost is a way-station for their war-parties: tents, a hitching line, and a lot of "
         "centaur with spears. Dorn wants it hurt. Drudges carry the supplies. Taskmasters keep the drudges in line. "
         "Break the line and the outpost folds."),
        [kill("Kolkar Drudge", 8), kill("Kolkar Taskmaster", 4)],
        ("Drudges are the ones with clubs and no ambition. Taskmasters are the ones with whips and plenty. "
         "Eight and four. Come back with your armour a little dented."),
        ("That did something. I could hear their drum change tempo from here. They don't like being surprised. "
         "Good - make them dislike it more."),
        [item("Outpost-Breaker's Cuirass", "chest", "of the Tiger", 17,
              "Mail plates riveted to a kodo-leather backing. Not elegant. Entirely effective.",
              "Mail Chest (Str/Agi)", armor="mail", req=14),
         item("Taskmaster's Lash-Whip", "main_hand", "of the Bandit", 17,
              "A short stock with a braided cord. Hits slower than it looks and harder than it should.",
              "Mace 1H (Agi/Sta)", weapon="mace_1h", req=14),
         item("Drudge-Hide Leggings", "legs", "of the Ironfur", 17,
              "Thick as a doormat. Durable as one, too.", "Leather Legs (Sta/Dodge)", armor="leather", req=14)],
        nxt="cb_windseers_whispers", xp=990, gold=3600))
    a(Q("cb_windseers_whispers", "Windseers' Whispers", "barrens_scout_2", 15,
        ("The Kolkar windseers read the sky for their warlords, and the sky has been telling them something about "
         "the Crossroads. Dorn can't read the sky. He can read a stolen bundle of bone and kodo-hair, if somebody "
         "brings him one that still twitches."),
        [fetch("kolkar_windseer_totem", 5)],
        ("Totems off the windseers and the stormers - they carry them, like a mother carries a purse. "
         "Five. Don't look in the bundle too long. It looks back."),
        ("Hm. That's not a prayer. That's a map. And the map has a war-camp on it, east of here, with a cross "
         "through the Crossroads. I'll want a closer look at that camp."),
        [item("Windseer's Totem-Mantle", "shoulder", "of the Prophet", 18,
              "Feathers stitched over a bone plate. It tilts, a little, towards storms.",
              "Mail Shoulders (Int/Spi/MP5)", armor="mail", req=15),
         item("Stormbound Hexstaff", "main_hand", "of Nature's Wrath", 18,
              "A staff with a hawk's skull on the head. The skull occasionally turns its beak.",
              "Staff (Int/SP)", weapon="staff", req=15),
         item("Cord of Four Winds", "waist", "of the Falcon", 18,
              "A braided belt with four tassels for the four winds. The fifth tassel is for the one that isn't one.",
              "Leather Belt (Agi/Int)", armor="leather", req=15)],
        nxt="cb_the_war_camp", xp=1100, gold=3900))
    a(Q("cb_the_war_camp", "The War Camp", "barrens_scout_2", 16,
        ("The map's cross leads to the Kolkar war camp, deep in the plains east of the Kodo Graveyard. Dorn "
         "has never been close. He wants to know how many tents, how many marauders, and how bad the drum sounds "
         "at close range."),
        [explore(238, 112, 10), kill("Kolkar Marauder", 8)],
        ("Go to the camp. Take a look, take a few of them down before you leave. Marauders are the ones on the "
         "outside. If you're running past them, you're too deep."),
        ("A hundred tents. A hundred! And a banner I haven't seen in years - Gorrak's. "
         "That old war-chief is back, and he's mustering. We cut the head off, or we pay for it."),
        [item("Marauder-Slayer's Hauberk", "chest", "of the Soldier", 19,
              "Chain over boiled kodo-hide. A centaur's lance doesn't go through. Several have been disappointed.",
              "Mail Chest (Str/Sta)", armor="mail", req=16),
         item("Warcamp Scout's Gloves", "hands", "of the Monkey", 19,
              "Soft hide with leather palms. Silent on a ridge.", "Leather Gloves (Agi/Sta)", armor="leather", req=16),
         item("Drum-Beat Pendant", "neck", "of the Champion", 19,
              "A small drum on a cord. Faint, steady, and entirely in your pulse.", "Necklace (Str/Sta)", req=16)],
        nxt="cb_warbringer_gorrak", xp=1210, gold=4200))
    a(Q("cb_warbringer_gorrak", "The Warbringer", "barrens_scout_2", 17,
        ("Warbringer Gorrak has led three Kolkar marches on the Crossroads, and each one left a wall a little "
         "shorter than before. He is old, he is huge, and he does not retreat. Dorn will not ask you to do this "
         "for glory. He will ask you to do it because the next march is already in the drum."),
        [kill("Kolkar Taskmaster", 6), boss("Warbringer Gorrak")],
        ("He rides the war camp's edge when the drum starts. Break the taskmasters first - they keep the herd in "
         "line. Then him. Quick and hard."),
        ("It's quiet. For the first time in three years, I can hear the wind and nothing else. "
         "Take this. The Crossroads owes you a debt it'll never think to repay."),
        [item("Plainswatcher's Spear of Dawn", "main_hand", "of the Soldier", 20,
              "A long spear, cut for the ridge. The first light always finds the point.",
              "Polearm (Str/Agi/Sta)", weapon="polearm", req=17),
         item("Warbringer's Broken Pauldrons", "shoulder", "of the Juggernaut", 20,
              "Kolkar plate, cracked down the middle. Someone patched it with Barrens grass-rope.",
              "Plate Shoulders (Str/Sta)", armor="plate", req=17),
         item("Dorn's Long-Watch Ring", "ring", "of the Hunt", 20,
              "A plain steel band with a notch for every sandstorm survived.",
              "Ring (Agi/Sta)", req=17),
         item("Crossroads Defender's Mantle", "back", "of the Bastion", 20,
              "A heavy cloak, lined for the cold. It will not stop a lance. It will keep you alive until the second.",
              "Cloak (Sta/Armor)", armor="cloth", req=17)],
        xp=1500, gold=5200, span=3))

    # ============================== KRANAL FISS (Grol'dom Farm) ==============================
    a(Q("cb_pests_in_the_furrows", "Pests in the Furrows", "groldom_farmer", 13,
        ("Kranal Fiss has farmed Grol'dom since before Orgrimmar had proper walls. Quilboar press him from two "
         "sides some seasons; this season the problem is smaller and sneakier. Poachers have started working the "
         "farm after dark - lifting sacks, cutting traces, laughing over the wall."),
        [kill("Farm Poacher", 8)],
        ("They hide in the furrows - small men in the colour of dirt. Eight of them, and I'll sleep through the night "
         "for the first time in a month."),
        ("It's been quiet since last night. I did not hear a single laugh. That is better than gold. Next, the sacks."),
        [item("Farmhand's Burlap Cowl", "head", "of the Bear", 16,
              "Burlap and boiled leather. Smells of grain. Stops a thrown knife, by luck, once.",
              "Leather Helm (Sta/Dodge)", armor="leather", req=13),
         item("Furrow-Hoe", "main_hand", "of Striking", 16,
              "A heavy-headed hoe. Works the field. Works other things, in a pinch.",
              "Axe 1H (Str/Agi/Sta)", weapon="axe_1h", req=13),
         item("Seed-Planter's Gloves", "hands", "of the Eagle", 16,
              "Cloth gloves stitched with clover. They smell of soil and spring.",
              "Cloth Gloves (Int/Sta)", armor="cloth", req=13)],
        nxt="cb_stolen_seed"))
    a(Q("cb_stolen_seed", "Next Season's Seed", "groldom_farmer", 14,
        ("The poachers took more than a few coins. They took the seed - next year's whole crop, in sacks, "
         "and the sacks are stamped with Kranal's mark so they can't be sold on. They're hoarding them, or "
         "breaking the stamp. Either way: no seed, no spring."),
        [fetch("groldom_seed_sack", 5)],
        ("Five sacks. The poachers carry them like pack-rats, and they've the habit of losing them in a fight. "
         "Don't tear the burlap. It's got the only copy of next year on it."),
        ("They're all here. All five, and the burlap isn't even torn. You've saved a season, friend."),
        [item("Harvest-Moon Vest", "chest", "of the Seer", 17,
              "Woven grain-cloth. Warm in winter and somehow not in summer.",
              "Cloth Chest (Int/Sta/MP5)", armor="cloth", req=14),
         item("Reaper's Short Sickle", "main_hand", "of the Assassin", 17,
              "A curved blade for cutting things down. Wheat, mostly.",
              "Dagger (Agi/Crit)", weapon="dagger", req=14),
         item("Granary-Keeper's Belt", "waist", "of the Ironfur", 17,
              "Thick leather with a buckle shaped like a plough. It does not bend.",
              "Leather Belt (Sta/Dodge)", armor="leather", req=14)],
        nxt="cb_looter_chief_bazz"))
    a(Q("cb_looter_chief_bazz", "The Looter-Chief", "groldom_farmer", 14,
        ("Every gang has a chief, and the poachers' chief is a brute called Bazz who wields a stolen pitchfork like it "
         "owes him money. He doesn't work the fields. He runs the ones who do. Kranal would like him gone, "
         "and the pitchfork back."),
        [kill("Farm Poacher", 6), boss("Looter-Chief Bazz")],
        ("Big, loud, carries my pitchfork. The tines are bent but I'd know it anywhere. Six of his crew first - "
         "they keep the field between you and him."),
        ("You took the pitchfork back? Hah! ... Still bent. Never mind, keep it. The farm is quiet. That's the prize."),
        [item("Chief's Stolen Cloak", "back", "of the Bandit", 17,
              "Somebody else's cloak, worn so long it fits like it's yours.",
              "Cloak (Agi/Sta)", armor="cloth", req=14),
         item("Kranal's Plough-Iron", "main_hand", "of the Squire", 17,
              "A good plough blade, hafted for the other end of the field.",
              "Axe 2H (Str/Sta)", weapon="axe_2h", req=14),
         item("Poacher's Quick-Fingered Ring", "ring", "of the Monkey", 17,
              "It slips off a thumb in one smooth motion. That is a feature.",
              "Ring (Agi/Int)", req=14)],
        xp=900, gold=3300))
    return A


def quests_oases():
    A = []
    a = A.append

    # ============================== WATERKEEPER SANU (Lushwater) ==============================
    a(Q("cb_choking_the_oasis", "Choking the Oasis", "cb_waterkeeper", 13,
        ("Lushwater has been the first drink on the road to the Wailing Caverns for as long as the Tauren have "
         "had a road. Waterkeeper Sanu Goldenhoof keeps it that way. This season the silithid have pushed up out of "
         "the south dunes in a tide of chitin, fouling the reeds, and he cannot clear them alone."),
        [kill("Silithid Swarmer", 10), kill("Silithid Creeper", 6)],
        ("Swarmers in the grass, creepers in the reeds. They are not here to drink - they are here to breed. "
         "Cut them back before the pool goes brown."),
        ("The water runs clear again. The Earth Mother will notice. The silithid are patient, however. "
         "I will need you again."),
        [item("Reedwalker's Sash", "waist", "of the Eagle", 16,
              "Woven reed-cord with a bone clasp. It dries as fast as you walk.",
              "Cloth Belt (Int/Sta)", armor="cloth", req=13),
         item("Waterkeeper's Walking Staff", "main_hand", "of the Prophet", 16,
              "Cut from an oasis acacia. The wood stays faintly damp, whatever the weather.",
              "Staff (Int/Spi/MP5)", weapon="staff", req=13),
         item("Swarmbreaker Greaves", "legs", "of the Defender", 16,
              "Chitin plates over leather. The insects, noticeably, will not crawl on them.",
              "Mail Legs (Sta/Def)", armor="mail", req=13)],
        nxt="cb_vine_choked_springs"))
    a(Q("cb_vine_choked_springs", "Vine-Choked Springs", "cb_waterkeeper", 14,
        ("The springs at Lushwater are fed from below, and the thing that feeds them has started growing. "
         "Tangle-vines have strangled the east spring until it no longer reaches the surface. Sanu needs the vines "
         "cut, and he needs their hearts - because a tangle-vine heart, planted in clear soil, becomes a reed bed."),
        [kill("Oasis Tangle-Vine", 6), fetch("tangle_vine_heart", 4)],
        ("They hang on the north shore, thick as a leg, quiet as a prayer until you step too close. "
         "Cut them back. Bring me four hearts. And do not let them take your boots."),
        ("The vine hearts will grow where I plant them, and the spring will drink again. "
         "You have done something small and enormous at once."),
        [item("Vine-Heart Mantle", "shoulder", "of the Restorer", 17,
              "Woven vine and living leaf. It grows a new bud every time someone is healed nearby.",
              "Leather Shoulders (Int/Spi/MP5)", armor="leather", req=14),
         item("Tangle-Root Scepter", "main_hand", "of the Hierophant", 17,
              "A root-knotted rod that smells of rain. It is, at all times, slightly warm.",
              "Mace 1H (Int/Spi/MP5)", weapon="mace_1h", req=14),
         item("Springwater Pendant", "neck", "of the Seer", 17,
              "A drop of spring water trapped in a pearl. It never evaporates and never quite stops moving.",
              "Necklace (Int/Spi)", req=14)],
        nxt="cb_queen_skitterwing"))
    a(Q("cb_queen_skitterwing", "The Queen of Lushwater", "cb_waterkeeper", 15,
        ("Every swarm has a mother. Queen Skitterwing rules this one from a nest in the north reeds, a queen "
         "the size of a horse, with wings that hum a note you feel in your teeth. Sanu will not harm anything "
         "needlessly. He has made an exception."),
        [kill("Silithid Creeper", 8), boss("Queen Skitterwing")],
        ("The creepers guard the north reeds. The queen is behind them. Do it cleanly and don't linger - "
         "her song is not a lullaby."),
        ("The reeds are silent. Not the silence of death - the silence of rest. "
         "Thank you, friend of the oasis. Take what the pool has to give."),
        [item("Skitterwing's Chitin Hauberk", "chest", "of the Beast", 18,
              "A queen's carapace fitted to a harness. It is lighter than it looks and tougher than it should be.",
              "Mail Chest (Agi/Sta)", armor="mail", req=15),
         item("Hivesinger's Staff", "main_hand", "of Nature's Wrath", 18,
              "A staff humming with the memory of the hive. It sings low, and keeps singing.",
              "Staff (Int/SP)", weapon="staff", req=15),
         item("Oasis-Guardian's Signet", "ring", "of the Warder", 18,
              "A ring carved from a single reed-knot. It promises cool water and delivers.",
              "Ring (Sta/Armor)", req=15)],
        xp=1100, gold=3700, span=3))

    # ============================== PILGRIM-WARDEN TORGA (Forgotten Pools) ==============================
    a(Q("cb_forgotten_pilgrims", "The Forgotten Pilgrims", "cb_pools_warden", 14,
        ("The Forgotten Pools were once a place of pilgrimage - a chain of sacred springs on the long walk "
         "between Orgrimmar and the south. The pilgrims never stopped coming. They just stopped leaving. "
         "Torga keeps the shrine and watches over the dead, and she wants to know who they were."),
        [gather("pilgrim_prayer_beads", 6)],
        ("They wander the water's edge in robes that have not been dry in decades. They carry prayer beads - "
         "they'll hold the name of the one who owned them. Bring me six. I'll read them back."),
        ("Six names. Six people who walked here because they believed in something. "
         "We will carry the beads to Orgrimmar's shrine. They deserve that."),
        [item("Pilgrim's Faded Mantle", "shoulder", "of the Prophet", 17,
              "Cloth faded white, once a deep blue. It remembers how to be a blessing.",
              "Cloth Shoulders (Int/Spi/MP5)", armor="cloth", req=14),
         item("Prayer-Bead Chain", "neck", "of the Restorer", 17,
              "A string of worn wooden beads. They rattle softly when someone near you is hurt.",
              "Necklace (Spi/Healing)", req=14),
         item("Torga's Walking Staff", "main_hand", "of the Seer", 17,
              "A pilgrim's staff, cut for long walks and quiet thoughts.",
              "Staff (Int/Spi)", weapon="staff", req=14)],
        nxt="cb_murk_in_the_water", span=3))
    a(Q("cb_murk_in_the_water", "Murk in the Water", "cb_pools_warden", 15,
        ("The murlocs came up the old river after the pilgrims stopped coming. They fish the pools, foul the "
         "springs, and have started to build something that looks a lot like a shrine of their own. Torga is "
         "not a violent woman. She is, however, tired of explaining herself to a fish."),
        [kill("Pool Murloc", 8), kill("Murloc Flesheater", 6)],
        ("Pool murlocs are the ones on the shore. The Flesheaters are the ones who've been in the deep too long. "
         "Fourteen between them. Be careful of the Flesheaters; they bite."),
        ("Clear water. Well, clearer. Take this. It was a gift from a pilgrim, and I'm not one for heirlooms."),
        [item("Poolwalker's Waders", "feet", "of the Eagle", 18,
              "Rubberised leather that keeps the water out and the mud off. Only partly.",
              "Leather Boots (Agi/Int)", armor="leather", req=15),
         item("Shrine-Cleaner's Mop-Spear", "main_hand", "of the Soldier", 18,
              "A spear with a mop-head on the other end. Do not ask which one is the weapon.",
              "Polearm (Str/Sta)", weapon="polearm", req=15),
         item("Deep-Pool Pendant", "neck", "of the Whale", 18,
              "A gleaming murloc scale on a cord. It hums when you hold it under water.",
              "Necklace (Sta/Spi)", req=15)],
        nxt="cb_weeping_pilgrim", span=3))
    a(Q("cb_weeping_pilgrim", "Maeve the Weeping", "cb_pools_warden", 16,
        ("One of the pilgrims never stopped walking. Maeve the Weeping walks the water's edge in a wedding veil, "
         "singing a song nobody remembers the words to, and the pool-water follows her like a train. "
         "She's not malicious. She's very, very sad, and sadness has teeth."),
        [kill("Drowned Pilgrim", 6), boss("Maeve the Weeping")],
        ("She walks the south pool at dusk. Do what you must, but be gentle about it. "
         "She does not know she's dead. That's all the sorrow."),
        ("I heard her stop. I will read her prayer at dawn. Take this - she would have wanted somebody to carry it."),
        [item("Weeper's Mourning Veil", "head", "of the Mind's Eye", 19,
              "A black veil, still wet at the hem. It does not dry in any weather.",
              "Cloth Helm (Int/Spi/MP5)", armor="cloth", req=16),
         item("Pilgrim's Reliquary Blade", "main_hand", "of the Squire", 19,
              "A short sword in a reliquary-sheath. It sings, once, when you draw it.",
              "Sword 1H (Str/Agi/Sta)", weapon="sword_1h", req=16),
         item("Tear-Stained Band", "ring", "of the Physician", 19,
              "A silver ring set with a pearl that was never quite a tear.",
              "Ring (Int/Spi/Healing)", req=16)],
        nxt="cb_gaharrz_the_drowned", xp=1200, gold=4100, span=3))
    a(Q("cb_gaharrz_the_drowned", "The Drowned Warlord", "cb_pools_warden", 17,
        ("Gaharrz is not a murloc, exactly. He's what happens when a murloc warlord drowns in a sacred pool and "
         "refuses to be done. He's the reason the shrine goes quiet at dusk, and the reason Torga keeps one "
         "hand on her cleaver at night."),
        [kill("Water Elemental", 4), boss("Gaharrz the Drowned")],
        ("He lives in the middle pool. The elementals guard him - they were pool spirits once. "
         "Kill them, then him. It's the only way the shrine can sleep."),
        ("The pool's still. For the first time since I came here, it is still. "
         "I will light a lamp for you at the shrine. Take this from the dead."),
        [item("Pool-Warden's Plate Girdle", "waist", "of the Defender", 20,
              "A heavy belt forged from a pilgrim's cleaver. It's seen the sorrow, and kept it.",
              "Plate Belt (Sta/Def)", armor="plate", req=17),
         item("Drowned Warlord's Trident", "main_hand", "of the Hunt", 20,
              "A trident still dripping. It's probably better not to know what from.",
              "Polearm (Agi/Sta)", weapon="polearm", req=17),
         item("Shrine-Keeper's Locket", "neck", "of the Archmage", 20,
              "A locket holding a pressed flower and a short prayer. Opening it feels like permission.",
              "Necklace (Int/Spi)", req=17),
         item("Cloak of the Still Water", "back", "of the Restorer", 20,
              "A cloak that never rippled in the wind. Worth the weight, on a restless night.",
              "Cloak (Int/Spi/MP5)", armor="cloth", req=17)],
        xp=1500, gold=5200, span=3))

    # ============================== KEEPER AHNMAR (Shrine of the Fallen Warrior) ==============================
    a(Q("cb_mourning_at_the_shrine", "Mourning at the Shrine", "cb_shrine_keeper", 14,
        ("The Shrine of the Fallen Warrior marks the place where a champion of the plains died holding a pass "
         "against a war-party three times his number. Keeper Ahnmar tends the stone. Lately the stone is not "
         "alone: mourning spirits drift in at dusk and will not leave, and the sound they make is very hard to bear."),
        [kill("Mourning Spirit", 8)],
        ("They gather around the shrine's stone at sunset. They do not mean harm - they simply cannot stop weeping. "
         "Release them. Be kind about it."),
        ("The shrine is quiet. That is the most sacred sound it knows. Thank you for your gentleness."),
        [item("Mourner's Ash-Grey Robes", "chest", "of the Restorer", 17,
              "Spirit-silk dyed the colour of cold ashes. It rustles when no wind is blowing.",
              "Cloth Chest (Int/Spi/MP5)", armor="cloth", req=14),
         item("Keeper's Hand-Bell", "main_hand", "of the Hierophant", 17,
              "A small bronze bell, rung at dusk. It carries farther than a bell should.",
              "Mace 1H (Int/Spi/MP5)", weapon="mace_1h", req=14),
         item("Shrinewalker's Sandals", "feet", "of the Eagle", 17,
              "Soft sandals that make no sound on stone. Out of respect, probably.",
              "Cloth Boots (Int/Sta)", armor="cloth", req=14)],
        nxt="cb_echo_of_the_fallen"))
    a(Q("cb_echo_of_the_fallen", "The Echo of the Fallen Warrior", "cb_shrine_keeper", 15,
        ("The warrior who died here did not go quietly. Something of him lingers at the shrine - an echo, not "
         "a ghost: a memory of the fight, replaying itself for anyone who walks in. Ahnmar believes the echo is "
         "caught, and cannot leave until it is shown the battle is over."),
        [kill("Mourning Spirit", 6), boss("Echo of the Fallen Warrior")],
        ("Face him as an equal. He will not stop for words. When he falls, tell him the pass held. "
         "That is all he needs to hear."),
        ("The pass held. I told him. He... nodded. Take this - it belongs to the warrior, "
         "and he wants it carried by someone who understands."),
        [item("Fallen Champion's Tabard", "chest", "of the Champion", 18,
              "Dust-worn plate. The tabard is untouched by time, as if somebody was waiting for it to be worn again.",
              "Plate Chest (Str/Sta)", armor="plate", req=15),
         item("Echo-Forged Longsword", "main_hand", "of the Soldier", 18,
              "A longsword that rings in your hand like a memory of battle.",
              "Sword 1H (Str/Agi/Sta)", weapon="sword_1h", req=15),
         item("Shrinewarden's Charm", "neck", "of the Bear", 18,
              "A small stone carved with a spear. Cool, always, and heavy as an oath.",
              "Necklace (Sta/Armor)", req=15)],
        xp=1080, gold=3650, span=3))

    return A


def quests_south():
    A = []
    a = A.append

    # ============================== CARAVAN-MASTER DOGAN (Raider's Rest) ==============================
    a(Q("cb_toll_collectors", "Toll Collectors", "cb_caravan_master", 16,
        ("Dogan Ironcart has run the Raider's Rest waystation since the Crossroads was a hitching post, and he "
         "pays his taxes to the right people. Somebody else has been collecting on the south road: bandits who "
         "call themselves toll-men and leave nobody with change."),
        [kill("Bandit Outrider", 8), kill("Bandit Cutthroat", 6)],
        ("Outriders on the road, Cutthroats in the oasis grass. Fourteen between them, and I'll "
         "pay the difference myself. You'll be paid in gold, and in pride."),
        ("The roads run smoother already. You can feel it in the cart-wheels. "
         "Business is a state of mind, friend - and my mind is calmer now."),
        [item("Caravan Guard's Brigandine", "chest", "of the Soldier", 19,
              "Studded leather over mail rings. Standard issue for those who protect caravans. And are paid for it.",
              "Mail Chest (Str/Sta)", armor="mail", req=16),
         item("Toll-Breaker's Shortsword", "main_hand", "of the Tiger", 19,
              "A broad blade for breaking contracts. Both kinds.", "Sword 1H (Str/Agi)", weapon="sword_1h", req=16),
         item("Road-Warden's Greaves", "legs", "of the Bear", 19,
              "Thick leather and iron studs. Made to be sat on for a whole day without complaint.",
              "Leather Legs (Sta/Armor)", armor="leather", req=16)],
        nxt="cb_powder_kegs", span=3))
    a(Q("cb_powder_kegs", "Dogan's Missing Powder", "cb_caravan_master", 17,
        ("A shipment of blasting powder went missing on the south road, and the bandits have found a use for it. "
         "Bombardiers have started lobbing kegs at passing wagons. Dogan wants the kegs back, intact, "
         "before they find a way to light them."),
        [fetch("bandit_powder_keg", 4)],
        ("The bombardiers carry them in satchels on their backs - tiny kegs, long fuses. "
         "Cut the fuses first. Bring four back. Preferably not on fire."),
        ("Four kegs, no fuses lit. You may be the most careful soul in the Barrens. "
         "That is an excellent quality in a merchant. Pity about the pay."),
        [item("Bombardier's Padded Vest", "chest", "of the Bandit", 20,
              "Thick quilting that does not catch fire. Marketed as 'extremely resistant'. Not 'immune'.",
              "Leather Chest (Agi/Sta)", armor="leather", req=17),
         item("Fusemaker's Flintlock", "ranged", "of the Marksman", 20,
              "A flintlock that fires a loud bang first and a bullet second. Both work.",
              "Gun (Agi/Sta/Hit)", weapon="gun", req=17),
         item("Smoke-Bomb Pouch", "waist", "of the Monkey", 20,
              "A belt pouch of smoke-bombs, half-empty, half-reliable.",
              "Leather Belt (Agi/Int)", armor="leather", req=17)],
        nxt="cb_croc_problem", span=3))
    a(Q("cb_croc_problem", "The Crocolisk Problem", "cb_caravan_master", 17,
        ("Raider's Rest has water, and where there's water there are things that want you in it. The watering-hole "
         "crocolisks have taken three of Dogan's oxen this season and one of his best guards. "
         "He'd like them gone, and the smugglers who feed them."),
        [kill("Watering Hole Crocolisk", 6), kill("Raider's Rest Smuggler", 6)],
        ("Crocs in the shallows, smugglers on the shore. Both need removing. The smugglers have been "
         "feeding the crocs - for fun, I think. Fewer of both would be an improvement."),
        ("Quiet shore, and the oxen are safe. You have the thanks of a very tired merchant."),
        [item("Croc-Hide Waders", "feet", "of the Whale", 20,
              "Crocolisk hide, thick as plate. It stops teeth - hopefully the same teeth that made it.",
              "Leather Boots (Sta/Spi)", armor="leather", req=17),
         item("Oxgoad of the Rest", "main_hand", "of the Gladiator", 20,
              "A long goad for prodding oxen. Prods other things, in a pinch.",
              "Polearm (Str/Sta)", weapon="polearm", req=17),
         item("Waterline Amulet", "neck", "of the Falcon", 20,
              "A small bronze amulet on a fishing line. Nobody will tell you what it's for.",
              "Necklace (Agi/Int)", req=17)],
        nxt="cb_silas_quickfinger", span=3))
    a(Q("cb_silas_quickfinger", "Quickfinger", "cb_caravan_master", 18,
        ("The smugglers have a captain, and the captain has a name: Silas Quickfinger. He's been the single "
         "most expensive man on the south road for two years, and he's never once been caught holding "
         "anything. Dogan has finally had enough."),
        [kill("Raider's Rest Smuggler", 8), boss("Silas Quickfinger")],
        ("He runs the oasis-island camp. You'll know him by the lack of anything in his hands. "
         "Check your pockets before and after. Bring me what's left of him."),
        ("You found the ledger? ... That's an enormous help. I'd hoped you wouldn't touch it, "
         "but I'd hoped for a lot of things this year. Take the reward - you've earned every coin."),
        [item("Quickfinger's Stolen Cloak", "back", "of the Assassin", 21,
              "A dark cloak that folds into a pocket. Several pockets, actually.",
              "Cloak (Agi/Crit)", armor="cloth", req=18),
         item("Smuggler's Hidden Blade", "main_hand", "of the Bandit", 21,
              "A dagger concealed in a sleeve-sheath. Draws so fast you won't see it leave.",
              "Dagger (Agi/Sta)", weapon="dagger", req=18),
         item("Dogan's Merchant Seal", "ring", "of the Tactician", 21,
              "A merchant's ring with a signet for the ledger. It has opened more doors than most keys.",
              "Ring (Agi/Int/Crit)", req=18),
         item("Caravan-Master's Cuirass", "chest", "of the Defender", 21,
              "A trader's armour: heavy, plain and made to last through a hundred caravans.",
              "Plate Chest (Sta/Def)", armor="plate", req=18)],
        xp=1620, gold=5700, span=3))

    # ============================== SCOUT ZARLA (Dreadmist approach) ==============================
    a(Q("cb_dreadmist_approach", "The Dreadmist Approach", "cb_dreadmist_scout", 15,
        ("Dreadmist Peak is the grey massif in the north-west corner of the plain, and the cultists inside it "
         "have been very quiet lately. Scout Zarla has been watching the approach for a week and is not "
         "happy with what she has seen. She needs a second pair of eyes at the mouth of the canyon."),
        [explore(55, 52, 8)],
        ("Follow the road past the third baobab, up to where the cliffs close in. "
         "The cult's banners hang at the canyon mouth. Look. Don't linger. Don't touch the banners."),
        ("They've built a ring of red banners and a summoning circle at the mouth. That's more than a cult. "
         "That's a ritual site. Something's coming through, and soon."),
        [item("Scout's Ash-Grey Cloak", "back", "of the Monkey", 18,
              "Ash-grey and weightless, hard to see against the cliffs.",
              "Cloak (Agi/Sta)", armor="cloth", req=15),
         item("Zarla's Spotting Bow", "ranged", "of the Falcon", 18,
              "A short bow with a spotter's lens fixed in the grip. Everything looks closer than it is.",
              "Bow (Agi/Int)", weapon="bow", req=15),
         item("Cliff-Walker's Boots", "feet", "of the Tiger", 18,
              "Hard soles for scree and soft heels for quiet. A scout's best friend.",
              "Leather Boots (Str/Agi)", armor="leather", req=15)],
        nxt="cb_imps_in_the_brush", xp=1010, gold=3450))
    a(Q("cb_imps_in_the_brush", "Imps in the Brush", "cb_dreadmist_scout", 15,
        ("The cultists have been summoning imps - small, sharp, giggly things that spill out of the canyon and "
         "bother everything in the brush. They're a symptom. Zarla wants one cut open to see what the cult "
         "is feeding them."),
        [fetch("smouldering_imp_heart", 6)],
        ("Imps have a heart the size of a plum, and it smoulders. Six of them. "
         "Wear gloves. Don't let it giggle at you."),
        ("Hm. Brimstone and blood. They've been feeding the imps on something that wasn't an animal. "
         "I'll tell the Warchief. Take this."),
        [item("Brimstone-Scorched Mantle", "shoulder", "of the Sorcerer", 18,
              "Scorched at the edges, cold at the centre. Smells of something struck once, hard, and often.",
              "Cloth Shoulders (Int/SP)", armor="cloth", req=15),
         item("Imp-Heart Wand", "ranged", "of Fiery Wrath", 18,
              "A short wand with a flickering cinder at the tip. It giggles, faintly, when used.",
              "Wand (Int/SP)", weapon="wand", req=15),
         item("Cultbreaker's Ring", "ring", "of the Spell Breaker", 18,
              "A plain iron band etched with warding glyphs. They glow when something dark is near.",
              "Ring (Int/Pen)", req=15)],
        nxt="cb_voidcaller_veshra", xp=1010, gold=3450))
    a(Q("cb_voidcaller_veshra", "Veshra the Voidcaller", "cb_dreadmist_scout", 16,
        ("Veshra is the cult's field commander: a voidcaller with a smile like a razor and a list of "
         "things she's summoned. She's stationed at the canyon mouth, supervising the ritual circle. "
         "If she falls, the ritual falters. Zarla would like it to falter."),
        [kill("Dreadmist Cultist", 8), boss("Voidcaller Veshra")],
        ("Cultists around the ritual circle, the Voidcaller at the centre. Take down the cultists first - "
         "they feed her power. Then her."),
        ("The ritual faltered. I felt it from the ridge. Something snapped, and the whole canyon went quiet. "
         "Take this. Well earned."),
        [item("Voidcaller's Hollow Cowl", "head", "of the Invoker", 19,
              "Black cloth, red lining. Looking into the lining is how it got red.",
              "Cloth Helm (Int/SP/Crit)", armor="cloth", req=16),
         item("Rift-Cutter Dagger", "main_hand", "of the Assassin", 19,
              "A ritual dagger meant for opening things that should stay shut.",
              "Dagger (Agi/Crit)", weapon="dagger", req=16),
         item("Ward-Etched Bracers", "wrist", "of the Warder", 19,
              "Bracers etched with ward-glyphs. They warm when something magical is near.",
              "Mail Bracers (Sta/Armor)", armor="mail", req=16)],
        xp=1200, gold=4100, span=3))

    # ============================== RANGER KISHI (quilboar roads) ==============================
    a(Q("cb_quills_and_barbs", "Quills and Barbs", "cb_quilboar_ranger", 15,
        ("The Razormane in Bramblescar have a new weapon: quill-throwers who hurl poison-barbed quills from the "
         "thorn thickets. Ranger Kishi has been stuck with three already and would rather not collect a fourth. "
         "She wants a bundle of the quills for study. Ideally, by someone else."),
        [fetch("razormane_quill_bundle", 6)],
        ("Quillthrowers and veterans carry the bundles. Six, and handle them by the string. "
         "The poison is still wet. It is not a good wet."),
        ("Now that's careful work. I'll send these to the Apothecaries - they can make an antidote. "
         "Take this. And please wash your hands."),
        [item("Quillproof Leather Vest", "chest", "of the Bear", 18,
              "Boar-hide stitched over quilled leather. Hard to stab. Harder to sit in.",
              "Leather Chest (Sta/Dodge)", armor="leather", req=15),
         item("Ranger's Quill-Dart", "ranged", "of the Marksman", 18,
              "A balanced throwing dart. The fletching is a quilboar quill, de-poisoned. Mostly.",
              "Bow (Agi/Hit)", weapon="bow", req=15),
         item("Thorn-Warded Bracers", "wrist", "of the Defender", 18,
              "Mail rings, each bent around a thorn. The thorns have forgiven you.",
              "Mail Bracers (Sta/Def)", armor="mail", req=15)],
        nxt="cb_battleboar_tusks", xp=1010, gold=3450))
    a(Q("cb_battleboar_tusks", "Tusks of the Battleboar", "cb_quilboar_ranger", 16,
        ("Across the road, the Bristleback keep a different kind of weapon: battleboars, trained to charge "
         "anything on two legs and bred to be angrier each generation. Kishi wants tusks - to prove the boars "
         "are being bred, not found - and wants the weavers who breed them silenced."),
        [fetch("battleboar_tusk", 5), kill("Bristleback Briarweaver", 4)],
        ("Briarweavers keep the boars calm. The battleboars carry the tusks. Five tusks, four weavers. "
         "The boars won't be calm without them."),
        ("That's the evidence. The Bristleback are breeding a war-herd, and now the Warchief will know. "
         "Take your payment and my thanks."),
        [item("Battleboar-Hide Jerkin", "chest", "of the Tiger", 19,
              "Reinforced hide, boiled and studded. It smells of boar. It also, oddly, smells of victory.",
              "Leather Chest (Str/Agi)", armor="leather", req=16),
         item("Tusk-Tipped Spear", "main_hand", "of the Soldier", 19,
              "A long spear with a battleboar tusk for the head. Gored the first thing it touched.",
              "Polearm (Str/Sta)", weapon="polearm", req=16),
         item("Briarweaver's Thorn Ring", "ring", "of the Beast", 19,
              "A ring of living thorn-wood. It blossoms, faintly, in the rain.",
              "Ring (Agi/Sta)", req=16)],
        nxt="cb_wardchief_thulg", xp=1100, gold=3800, span=3))
    a(Q("cb_wardchief_thulg", "The Wardchief of Bramblescar", "cb_quilboar_ranger", 16,
        ("Wardchief Thulg commands the Razormane at Bramblescar from a thorn-throne at the camp's heart. "
         "He is clever, brutal, and unburdened by doubt. Kishi believes the war between the quilboar tribes "
         "hangs on his command, and a Razormane without a Wardchief is a Razormane without a war."),
        [kill("Razormane Veteran", 6), boss("Wardchief Thulg")],
        ("He sits at the heart of Bramblescar. The veterans guard the approach. Cut through them, "
         "and finish him before he's up."),
        ("The Razormane are leaderless. That won't last, but it's a start. Take this."),
        [item("Thulg's Thorn-Throne Pauldrons", "shoulder", "of the Bear", 19,
              "Pauldrons carved from a quilboar's war-throne. Painful. Beautiful. Both.",
              "Plate Shoulders (Sta/Armor)", armor="plate", req=16),
         item("Razormane Warcleaver", "main_hand", "of the Gladiator", 19,
              "A chunk of iron with a handle. Quilboar craft isn't subtle.",
              "Axe 2H (Str/Sta)", weapon="axe_2h", req=16),
         item("Bramblescar Thornband", "ring", "of the Defender", 19,
              "A ring bristling with tiny thorns. Not comfortable. Entirely effective.",
              "Ring (Sta/Armor)", req=16)],
        nxt="cb_sowmother_grunka", xp=1200, gold=4100, span=3))
    a(Q("cb_sowmother_grunka", "The Sow-Mother of Agama'gor", "cb_quilboar_ranger", 17,
        ("Across the road, the Bristleback tribe has its own mother: Sow-Mother Grunka, the Brood-Matriarch, "
         "who has sired half the war-herd. Kishi wants the other side of the war dealt with too - "
         "fairness being a rare luxury in a quilboar war."),
        [kill("Bristleback Raider", 6), boss("Sow-Mother Grunka")],
        ("The Bristleback camp at Agama'gor is a horror of mud and tusks. The Sow-Mother sits in the middle. "
         "Her raiders will try to stop you. Don't let them."),
        ("Both chiefs gone. The war will stumble now. It was never going to be quiet - but it will be quieter."),
        [item("Grunka's Brood-Mantle", "back", "of the Restorer", 20,
              "A broad cloak of sow-hide. It's heavy with brood-lore and a very faint maternal grudge.",
              "Cloak (Int/Spi/MP5)", armor="cloth", req=17),
         item("Sow-Mother's Gorebanner", "main_hand", "of the Champion", 20,
              "A war-banner on a spear. The banner is a hide, the spear is a tusk, the hide is Grunka's.",
              "Polearm (Str/Sta)", weapon="polearm", req=17),
         item("Brood-Tender's Girdle", "waist", "of the Juggernaut", 20,
              "A heavy belt of boar-bone and chain. It does not forget.",
              "Mail Belt (Str/Sta)", armor="mail", req=17),
         item("Agama'gor Tusk Ring", "ring", "of the Hunt", 20,
              "A ring carved from a battleboar tusk. It hums when something aggressive is nearby.",
              "Ring (Agi/Sta)", req=17)],
        xp=1500, gold=5200, span=3))

    # ============================== BRIDGEWARDEN KARGA (Durotar landing) ==============================
    a(Q("cb_snapper_season", "Snapper Season", "cb_bridgewarden", 12,
        ("The Southfury bridge connects Durotar to the Barrens, and Bridgewarden Karga keeps the planks sound "
         "and the traffic moving. Riverbank snappers have taken to chewing the pilings. She needs shell plates to "
         "armour the supports - and fewer snappers."),
        [fetch("snapper_shell_plate", 5)],
        ("Snappers on the bank, shells like shields. Take five plates and I'll nail them to the pilings. "
         "Let the next snapper try chewing that."),
        ("Five plates, thick as slabs. The bridge will outlast us all. Take this."),
        [item("Bridgewarden's Shell Buckler", "off_hand", "of Blocking", 15,
              "A snapper-shell shield bound with bridge-rope. It holds against teeth and tide.",
              "Shield (Sta/Block)", weapon="shield", req=12),
         item("Plank-Driver's Mallet", "main_hand", "of Striking", 15,
              "A mallet for driving pilings. Persuasive in negotiations.",
              "Mace 1H (Str/Agi/Sta)", weapon="mace_1h", req=12),
         item("Riverbank Waders", "feet", "of the Bear", 15,
              "Waterproofed hide boots with grip soles. Excellent on wet planks.",
              "Leather Boots (Sta/Agi)", armor="leather", req=12)],
        nxt="cb_bridge_watch", xp=700, gold=2600))
    a(Q("cb_bridge_watch", "Bridge Watch", "cb_bridgewarden", 13,
        ("With the pilings armoured, the next threat is the sky and the shore. Sunscale screechers have taken "
         "to dive-bombing travellers at the Barrens end of the bridge, and the snappers haven't learned their lesson. "
         "Karga wants the bank clear before the next caravan crosses."),
        [kill("Sunscale Screecher", 6), kill("Riverbank Snapper", 6)],
        ("Screechers from above, snappers from below. A bridge-warden's life, friend. Twelve between them, "
         "and I'll pay you in coin and curses."),
        ("Quiet at last! Caravans can cross in peace. Take this - and remember me kindly when you cross."),
        [item("Bridge-Watch Brigandine", "chest", "of the Defender", 16,
              "Boiled leather and mail rings. Standard for the bridge-watch. Fits nobody and everybody.",
              "Mail Chest (Sta/Def)", armor="mail", req=13),
         item("Screecher-Plume Cloak", "back", "of the Eagle", 16,
              "A cloak lined with sunscale feathers. It rustles like applause.",
              "Cloak (Int/Sta)", armor="cloth", req=13),
         item("Warden's Signal Horn", "neck", "of the Falcon", 16,
              "A small bone horn on a cord. A quick blast scatters birds and boars alike.",
              "Necklace (Agi/Int)", req=13)],
        xp=800, gold=2900))
    return A


def main():
    Qs = quests() + quests_oases() + quests_south()
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
    print("central barrens hub quests:", len(out), "items:", sum(len(q["unique_item_defs"]) for q in out))


if __name__ == "__main__":
    main()
