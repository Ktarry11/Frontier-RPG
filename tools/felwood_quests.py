"""
Felwood: South Felwood, Emerald Sanctuary, North Felwood and Jaedenar. 51-56.

Read by tools/build_felwood_quests.py, which holds them to the same rules as Tempest Isle's.

WHAT FELWOOD IS ABOUT (claude/felwood_brief.md). The Emerald Reclamation is taking the forest back:
Sentinels and druids, the Timbermaw, the treants, and a handful of transplants who came and stayed.
The south is already theirs. The north is the Legion's, the Council's and the Deadwood's, with one
Sentinel camp holding on at Talonbranch. So the quests go from mending what's been won to taking
what hasn't:

  IN (2)         The Warsong foreman at the foot of the Felwood road sends you north, and a letter
                 from Tempest Isle comes the other way.
  THE SOUTH (24) The Sanctuary's people, each with their own piece of it: the Sentinels' line, the
                 Timbermaw's cousins, the druids' groves, the volunteers' kitchen and infirmary.
  THE NORTH (19) Talonbranch's five, and the road on into the wastes.
  JAEDENAR (8)   Given in the Sanctuary and at Talonbranch, never inside.
  OUT (4)        The Royal Hive under Tanaris, Khaz Varun on Tempest Isle, Dr. Imani at Ashclaim
                 Landing, and the Timbermaw tunnel (Kyle, 14 Nov: "quest givers can send players to
                 Dungeons ON OTHER CONTINENTS!!!! This can help people find NEW homebrew areas").

Kyle, 14 Nov: "Keep most quest givers in hubs, ensure quests are VARIED and have proper chains in and
out of the zones!" Every giver here stands in the Sanctuary or at Talonbranch except the two who
start a chain in from somewhere else.
"""
from tools.felwood_quest_kit import (  # noqa: F401
    SF, NF, ES, JD, AE, TS, RH, KV, Q, k, boss, explore, deliver, carry, fetch,
    AELYRA, SARANIS, GRUMHALL, THORNBARK, NELANTHE, ELM, NKECHI, TOMASZ, YUKI, ANA,
    ELANYA, ARATHEL, BARROWPAW, MARCUS, THORNCLAW, FOREMAN, IMANI)

#: (item_id, name, description) drops three times in four; a fourth value overrides the rate.
FETCH_DROPS = {
    "Hollowbark Treant": [
        ("fw_q_heartwood_splinter", "Heartwood Splinter", "A pale splinter of living wood. It's warm, and "
                                                          "if you hold it long enough it puts out a root."),
    ],
    "Old-Growth Grizzly": [
        ("fw_q_stolen_honeycomb", "Bear-Stolen Honeycomb", "Half a comb, torn out of a hollow tree. The "
                                                           "bear only got to one side of it."),
    ],
    "Iris Snapjaw": [
        ("fw_q_snapjaw_scrapings", "Snapjaw Shell Scrapings", "A twist of paper full of green scrapings "
                                                              "off a snapjaw's shell. It smells like a pond."),
    ],
    "Blighted Wolf": [
        ("fw_q_fevered_blood", "Fevered Blood Sample", "A stoppered vial of wolf's blood. It's too warm, "
                                                       "and there's a green shimmer in it when it moves."),
    ],
    "Ivybound Treant": [
        ("fw_q_seasoned_ivywood", "Seasoned Ivywood", "A straight limb of old wood wrapped in dry ivy. "
                                                      "It's hard as iron and it doesn't split."),
    ],
    "Silverhorn Stag": [
        ("fw_q_silverhorn_venison", "Silverhorn Venison", "A good cut of venison, lean and dark."),
    ],
    "Moss-Tusk Boar": [
        ("fw_q_mosstusk_bacon", "Moss-Tusk Flank", "A heavy flank of boar, streaked with fat."),
    ],
    "Felguard Sentry": [
        ("fw_q_felguard_axehead", "Felguard Axe-Head", "A black axe-head as wide as your chest. The edge "
                                                       "is still warm."),
    ],
    "Greywood Nightsaber": [
        ("fw_q_greywood_pelt", "Greywood Pelt", "A soft grey pelt with faint darker stripes."),
    ],
    "Timberline Wolf": [
        ("fw_q_timberline_pelt", "Timberline Pelt", "A thick wolf pelt, brown going grey at the tips."),
    ],
    # ---- North Felwood
    "Seepage Ooze": [
        ("fw_q_bloodvenom_sample", "Bloodvenom Sample", "A sealed jar of the falls' water. It's green, it's "
                                                        "faintly warm, and the glass is starting to etch."),
    ],
    "Warpwood Treant": [
        ("fw_q_warpwood_splinter", "Warpwood Heartsplinter", "A splinter of dead ironwood with a thread of "
                                                             "living green still in the middle of it."),
    ],
    "Deadwood Shaman": [
        ("fw_q_deadwood_fetish", "Deadwood Fetish", "A bundle of bone, fur and fel-stained twine. It hums "
                                                    "if you hold it near your ear."),
    ],
    "Jadefire Stag": [
        ("fw_q_jadefire_antler", "Jadefire Antler", "A tine of antler that smoulders green at the tip. It "
                                                    "burns nothing, but it never goes out."),
    ],
    "Felbrand Hellhound": [
        ("fw_q_hellhound_gland", "Hellhound Gland", "A small, hot, unpleasant gland. Marcus wants it "
                                                    "for reasons he's promised to explain."),
    ],
    # ---- inside Jaedenar
    "Shadow Council Summoner": [
        ("fw_q_summoning_codex", "Page of the Summoning Codex", "A vellum page covered in circles and a "
                                                                "script that hurts to look at."),
    ],
    "Jaedenar Felguard": [
        ("fw_q_highborne_keystone", "Highborne Keystone", "A carved keystone from the Hold's arches. The "
                                                          "Council painted over it, and the old work shows "
                                                          "through underneath."),
    ],
    # ---- elsewhere
    "Resin Weaver": [
        ("fw_q_royal_resin", "Royal Hive Resin", "A lump of amber resin from deep in the Royal Hive. "
                                                 "Something small is caught inside it, and it's still green."),
    ],
    "Iron Golem": [
        ("fw_q_dark_iron_hinge", "Dark Iron Hinge", "A hinge as long as your arm, forged in Khaz Varun. "
                                                    "It's never rusted and it never will."),
    ],
}
STARTER_DROPS = {
    # A Sentinel's moonstone, worn by a satyr. It starts the turncloak's story.
    "Jadefire Felsworn": [("fw_q_sentinel_moonstone", "Sentinel's Moonstone",
                           "A Sentinel's moonstone on a broken chain. A name is cut into the back: "
                           "Vor'alith.", 0.20)],
}
STARTER_IDS = {"fw_q_sentinel_moonstone": "fw_the_moonstone"}


def build():
    q = []

    # =========================================================== IN
    q.append(Q("fw_the_road_north", "The Road North", FOREMAN, 50, 51, "sentinel",
               "Take Foreman Gruzak's letter up the Felwood road to Arch Druid Aelyra Moonbough in the "
               "Emerald Sanctuary.",
               [deliver("fw_gruzak_letter", "the foreman's letter, to Arch Druid Aelyra in the Emerald "
                                            "Sanctuary")],
               "You've got the look of somebody who's done with Ashenvale, and I've got a job for that look. You lot always want to see what's over the next hill.\n\n"
               "The road behind my camp goes north out of the trees and into Felwood. It used to be "
               "somewhere nobody came back from. Now there's a town up there, the Emerald Sanctuary, "
               "and the elves running it have been sending my scouts home with honey and good manners.\n\n"
               "I owe them a reply. Take this letter up the road, past the old watch at Morlos'Aren, and "
               "turn east at the fork. Give it to the Arch Druid. Try not to let her talk you into planting "
               "anything.",
               "Gruzak writes like he swings an axe, and I like him for it.\n\nHe says you're worth "
               "feeding. We'll see about that. Everybody here came for a different reason, and we've stopped "
               "asking which. Have a look round the Sanctuary, and then come and find me when you're ready "
               "to work.",
               zone=AE, turn_in_npc_id=AELYRA,
               grant_items=carry("fw_gruzak_letter", "Gruzak's Letter",
                                 "Folded twice and sealed with axle grease. It's addressed to the elves.")))

    # =========================================================== THE SANCTUARY
    q.append(Q("fw_seeds_for_thornbark", "Seeds for Old Thornbark", ANA, 51, 51, "reclamation",
               "Carry Ana Lucia Ferreira's pouch of seed to Old Thornbark in the Sanctuary's grove.",
               [deliver("fw_seed_pouch", "the seed pouch, to Old Thornbark in the grove")],
               "You're new, so you get the easy one, and you'll learn where everything is on the way.\n\n"
               "I was a courier in Lisbon before I came through, three years ago now. I rode a scooter up hills that would make a goat cry. Here I "
               "walk, and I carry seeds, and honestly it's better.\n\nThis pouch is for Old Thornbark. "
               "He's the treant in the grove at the south end of town, past the shrine. You'll know him "
               "because he's the one who looks like a tree until he says hello.",
               "These are Ana's seeds, and she always brings the right ones.\n\nYou walked past every quarter of "
               "the Sanctuary to get here, so now you've seen us all. Sentinels in the north, Timbermaw in "
               "the east, the volunteers by the gate, and us in the grove. We're a strange town, but we're "
               "all pointed the same way.",
               turn_in_npc_id=THORNBARK,
               grant_items=carry("fw_seed_pouch", "Pouch of Glade Seed",
                                 "Soft leather, full of seed the size of rice. It's warm in your hand.")))

    q.append(Q("fw_roots_in_clean_ground", "Roots in Clean Ground", AELYRA, 51, 52, "reclamation",
               "Defeat Hollowbark Treants in Hollowbark Glade, south-west of the Sanctuary, and bring back "
               "Heartwood Splinters.",
               [k("Hollowbark Treant", 8, SF), fetch("fw_q_heartwood_splinter", 6)],
               "The treants of Hollowbark Glade are the oldest things in the south, and they woke up angry.\n\n"
               "They remember the fel. They don't know it's gone, so they strike at anything that walks "
               "under them, elf or furbolg or you. We can't reason with them yet. We can calm them, and we "
               "can take a little of their heartwood while they're calm. The transplants call that pruning, and they're not wrong.\n\nThe glade's south-west of the "
               "town, over the lower ford. Bring the treants down and gather the splinters they drop. Every "
               "one of those will grow into something that remembers being clean.",
               "These are warm, and that's a good sign. It means the old growth is still alive under all that anger.\n\n"
               "We'll plant them along the Fel Line, where the ground needs reminding. Thank you. The "
               "glade will be quieter for a while, and so will I.",
               nxt="fw_grandfather_hollowbark"))

    q.append(Q("fw_grandfather_hollowbark", "Grandfather Hollowbark", AELYRA, 53, 53, "reclamation",
               "Bring down Grandfather Hollowbark, the oldest treant in Hollowbark Glade.",
               [boss("Grandfather Hollowbark", SF)],
               "There's one treant in that glade the others follow, and he's the reason none of them will "
               "settle.\n\nWe call him Grandfather Hollowbark. He was old when the Highborne were young. "
               "He doesn't see us, he sees the fel that isn't there any more, and he fights it every hour "
               "he's awake.\n\nHe doesn't come out often. Go back to the glade and wait for him. Put him "
               "down gently if you can, and hard if you have to. When he's still, the rest will listen.",
               "He's sleeping, truly sleeping, for the first time in longer than I've been alive.\n\nThe "
               "glade will wake up gentler. You've done something the druids couldn't, and I won't forget "
               "it. Take this with you. It was grown for whoever did what you just did.",
               requires_quests=["fw_roots_in_clean_ground"]))

    q.append(Q("fw_hold_the_fel_line", "Hold the Fel Line", SARANIS, 52, 53, "sentinel",
               "Kill every Blighted Wolf and Felwood Imp you can find along the Fel Line, at the north end of "
               "South Felwood.",
               [k("Blighted Wolf", 10, SF), k("Felwood Imp", 8, SF)],
               "Everything south of the barricade is ours, and everything north of it wants to be.\n\nThe "
               "Fel Line is the band of dying forest at the top of the valley, where North Felwood bleeds "
               "through. The wolves up there have caught the fever, and the imps come down the road in the "
               "dark to set fires. My Sentinels can hold the barricade, but they can't be out in front of "
               "it as well. That's where you lot come in.\n\nGo north up the road, past the healed craters, to where the trees start to "
               "die. Thin out the wolves and the imps. I want my people sleeping more than one night in three.",
               "You smell like burnt fur and imp. That means it went well.\n\nThe watch said last night was "
               "the quietest in a month. They didn't believe it either. Here's something from the "
               "watch-hall. You've earned a place on the rack.",
               zone=ES))

    q.append(Q("fw_sentry_duty", "Sentry Duty", SARANIS, 53, 53, "sentinel",
               "Kill the Border Felhound packs and every Felguard Sentry on the Fel Line.",
               [k("Border Felhound", 6, SF), k("Felguard Sentry", 4, SF)],
               "The wolves and the imps were the Legion's leftovers, but these aren't.\n\nThe demons have set "
               "Felguard Sentries just south of the North Felwood gate, with Border Felhounds running between "
               "them. They aren't attacking. They're watching us, and that's worse. Something up north wants "
               "to know how many of us there are.\n\nGo up to the Fel Line and take the sentries down, hounds "
               "first. Blind them for me.",
               "Whatever was looking south through those sentries just went blind.\n\nIt'll send more "
               "eyes. They always do. But it'll take time, and time is the one thing we've never had enough "
               "of up here.",
               nxt="fw_haskzar"))

    q.append(Q("fw_haskzar", "Hask'zar the Scarred", SARANIS, 53, 53, "sentinel",
               "Kill Hask'zar the Scarred, the doomguard that walks the Fel Line.",
               [boss("Hask'zar the Scarred", SF)],
               "The sentries answered to something, and my scouts have finally seen it.\n\nHask'zar the "
               "Scarred is a doomguard with a burning whip. He took a Sentinel's glaive across the face the "
               "night we drove the Legion north, and he's been walking the Fel Line ever since, waiting for "
               "us to get careless.\n\nI don't intend to get careless. I intend to send you. He doesn't show "
               "himself often, so be patient up there, and don't fight him alone if you can help it.",
               "That's his whip, and Elune help me, it's still warm.\n\nThe Sentinel who scarred him was my sister. I'll hang "
               "this in the watch-hall where she'd have seen it. Thank you. That's a debt that's been "
               "sitting on me for a long time.",
               requires_quests=["fw_sentry_duty"]))

    q.append(Q("fw_arms_for_the_north", "Arms for the North", ELM, 52, 53, "sentinel",
               "Bring Felguard Axe-Heads from the Felguard Sentries on the Fel Line to Barkwarden Elm.",
               [fetch("fw_q_felguard_axehead", 4)],
               "The quartermaster asked me to ask you. She says I look more patient than she is, and she's "
               "right.\n\nEvery Felguard Sentry on the Fel Line carries an axe forged in the Twisting Nether. "
               "Ilyssa says that if she can get the heads into her forge, she can beat the fel out of them and "
               "get good steel back. The Sanctuary has a forge and no iron, and the Legion has plenty.\n\n"
               "I stand on that line every night, so I've watched those axes come down. Take them off the "
               "sentries and bring me the heads. I'll carry them to her, because they're heavy and I'm a tree.",
               "These are heavy even for me. Ilyssa's going to be impossible to live with for a week, because "
               "she loves a challenge.\n\nThe first blade out of that metal goes to whoever walks north next. "
               "She sent this ahead for you in the meantime."))

    q.append(Q("fw_the_morlosaren_watch", "The Watch at Morlos'Aren", ANA, 51, 51, "sentinel",
               "Go to the old watch at Morlos'Aren on the road south of the Sanctuary, then tell Captain "
               "Saranis what's left of it.",
               [explore(80, 178, "the old watch at Morlos'Aren", SF)],
               "The captain asked me to find somebody with good eyes and nothing to do, and you look like "
               "you've got one of those.\n\nMorlos'Aren was a Sentinel watch on the road in from Ashenvale. "
               "They lost half of it to the Legion and took the other half back. Nobody's stood on the tower "
               "since spring, and Captain Saranis wants to know whether it's worth manning again or whether "
               "it's just stones and a view.\n\nIt's south down the main road, past the burned treehouse. "
               "You walked right by it on your way in. Have a proper look this time, and then go and tell "
               "the captain in the Sentinel hall what you saw.",
               "So the tower's still standing. I'll send two of my people down there with a lantern.\n\nThat "
               "watch guarded the road for three hundred years, and it deserves to guard it a while longer. "
               "Thank you for looking.",
               turn_in_npc_id=SARANIS))

    q.append(Q("fw_cousins_in_the_north", "Cousins in the North", GRUMHALL, 53, 53, "timbermaw",
               "Take Elder Grumhall's totem to Scout Barrowpaw at the Talonbranch camp in North Felwood.",
               [deliver("fw_grumhall_totem", "the elder's totem, to Scout Barrowpaw at Talonbranch")],
               "The Timbermaw remember when the Deadwood were our cousins. Some of us remember their names.\n\n"
               "Barrowpaw is one of ours who went north with the Sentinels, to the camp at Talonbranch. He went the same week the first of you lot came up the road. He "
               "watches Felpaw Village, where the Deadwood live now. He hasn't asked for anything, which "
               "means he needs something.\n\nTake him this totem. It's carved with his family's marks. Go "
               "north through the gate at the top of the Fel Line and follow the road until you see Sentinel "
               "tents. He'll be the one sitting apart from the elves, pretending he isn't homesick.",
               "Grumhall sent you up here with this? He always did know what I needed better than I did.\n\nYou came "
               "a long way, so sit down a minute. There's work up here, and none of it's easy. When you're "
               "ready, I'll tell you about my cousins.",
               zone=ES, turn_in_npc_id=BARROWPAW,
               grant_items=carry("fw_grumhall_totem", "Oakpelt Family Totem",
                                 "A short totem of honey-wood carved with paw marks and a name.")))

    q.append(Q("fw_honey_for_the_lodge", "Honey for the Lodge", GRUMHALL, 51, 52, "timbermaw",
               "Take back the honeycomb the Old-Growth Grizzlies have been stealing from the Timbermaw's trees.",
               [fetch("fw_q_stolen_honeycomb", 8)],
               "The grizzlies of the south have found our honey trees, and they've decided they like us.\n\n"
               "They don't like us. They like the honey. Every Old-Growth Grizzly in the forest has been "
               "tearing open our hollow trees, and the lodge is running short. A furbolg without honey in "
               "winter is a sad thing to see, and the ones who came through from your world eat it faster than we do.\n\nThe grizzlies roam all over the open forest round the "
               "Sanctuary. Take back what they've stolen. The bears will live, and so will we.",
               "This will see the lodge through the cold months, and there's enough for the volunteers' "
               "kitchen too.\n\nLuis says our honey's the best he's had. I've decided to believe him. Take "
               "this, with the lodge's thanks."))

    q.append(Q("fw_ursa_mossjaw", "Ursa Mossjaw", GRUMHALL, 53, 53, "timbermaw",
               "Bring down Ursa Mossjaw, the great bear that roams Shatter Scar Vale.",
               [boss("Ursa Mossjaw", SF)],
               "There's one bear the Timbermaw don't hunt. We make offerings to her instead.\n\nUrsa "
               "Mossjaw has lived in Shatter Scar Vale since before the craters healed. The old furbolgs "
               "say she's the forest's own grudge, wearing fur. Lately she's been coming down to the road "
               "and killing anyone who passes.\n\nThe offerings have stopped working. Go to the vale, north "
               "up the road, and end it. Make it clean. She's earned that much.",
               "So she's gone. The elders will sing about it tonight, and some of them will cry.\n\nYou "
               "did the right thing, and it was a hard one. Take this with you. It was carved for her, and she won't "
               "need it now."))

    q.append(Q("fw_hides_for_trading", "Hides for Trading", GRUMHALL, 51, 52, "timbermaw",
               "Bring Greywood Pelts and Timberline Pelts from the nightsabers and wolves of South Felwood.",
               [fetch("fw_q_greywood_pelt", 5), fetch("fw_q_timberline_pelt", 5)],
               "Burlrock trades with everybody, and everybody wants furs for the cold up north.\n\nThe "
               "Greywood Nightsabers and Timberline Wolves of the open forest have the best coats in the "
               "valley. Burlrock can't hunt, because he's too fond of talking, so he's asked me to ask you.\n\n"
               "They're all through the forest round the Sanctuary. Bring the pelts back to me and I'll see "
               "they get to him.",
               "Good pelts, and clean. Burlrock will get twice what he'd get for anything he caught himself.\n\n"
               "He sent this ahead, in case you came back. He's an optimist."))

    q.append(Q("fw_what_the_lake_remembers", "What the Lake Remembers", THORNBARK, 51, 52, "reclamation",
               "Kill the Lakeshore Crocolisks round Iris Lake, east of the main road, and stand at the "
               "purified moonwell on its shore.",
               [k("Lakeshore Crocolisk", 8, SF), explore(96, 158, "the purified moonwell at Iris Lake", SF)],
               "Iris Lake was the first water the druids cleansed. I stood beside it while they did it, "
               "and I watched it turn from green to silver.\n\nNow the Lakeshore Crocolisks have moved in, "
               "and they snap at the druids who go down to draw water. The water's clean, but nobody can "
               "reach it.\n\nThe lake's east of the main road, south of the Sanctuary. Clear the crocolisks "
               "from the shore, and then go and stand by the moonwell. Tell me whether it still feels the way "
               "it did.",
               "It's still silver. I can feel it from here, now that you've been and come back.\n\nThe druids will be "
               "glad. They've been drinking rainwater for a month and complaining about it in two languages."))

    q.append(Q("fw_old_mossback", "Old Mossback", THORNBARK, 52, 52, "reclamation",
               "Defeat Old Mossback, the ancient snapjaw of Iris Lake.",
               [boss("Old Mossback", SF)],
               "Old Mossback and I've known each other for six hundred years, and we've never once got "
               "along.\n\nHe's a snapjaw the size of a cart, and he lives at the bottom of Iris Lake. The "
               "fel made him mean. The cleansing made him meaner, because now he can taste the difference.\n\n"
               "He's taken two druids this month. Go back to the lake and wait for him to surface. Tell him "
               "Thornbark sends his regards.",
               "So he's finished, after six hundred years.\n\nI'm surprised to find I'll miss arguing with him. "
               "Take this with you. It came out of the lake a long time ago, and it's been waiting for someone."))

    q.append(Q("fw_bandages_and_bitterroot", "Bandages and Bitterroot", NKECHI, 51, 52, "reclamation",
               "Collect Snapjaw Shell Scrapings from the Iris Snapjaws in Iris Lake for Dr. Adeyemi's poultice.",
               [fetch("fw_q_snapjaw_scrapings", 7)],
               "I was an emergency doctor in Lagos until I came through, and I never thought I'd be grinding turtle shell for "
               "medicine. Yet here we are.\n\nThe green film on an Iris Snapjaw's shell is full of something "
               "that stops a wound from going bad. The druids showed me, and then they showed me how bad "
               "it smells. It works better than anything I brought with me.\n\nThe snapjaws are in Iris Lake, "
               "east of the road south of town. Scrape their shells for me, and don't let them take your hand "
               "while you do it.",
               "That's a month of poultice, if I'm careful, and I'm always careful.\n\nThank you. People "
               "are going to walk out of my tent who would have been carried out. Take this, and please try "
               "not to need my tent yourself.",
               nxt="fw_the_fel_fever"))

    q.append(Q("fw_the_fel_fever", "The Fel Fever", NKECHI, 52, 53, "reclamation",
               "Draw Fevered Blood Samples from the Blighted Wolves on the Fel Line.",
               [fetch("fw_q_fevered_blood", 6)],
               "Three Sentinels came back from the Fel Line with a fever I can't name, and the wolves up "
               "there have it too.\n\nIt's not an infection I know. It's not anything I know. If I can look "
               "at the blood of the animals that carry it, I might understand how it moves. Then I might be "
               "able to stop it.\n\nThe Blighted Wolves run the Fel Line at the north end of the valley. "
               "Bring me their blood, sealed, and don't let any of it touch you.",
               "There's something alive in this that shouldn't be. It moves away from the light.\n\nI can't "
               "do more with what I've got here. The medic at Talonbranch, Marcus Oyelaran, has been seeing "
               "this up close for months. He'll want these. He'll want you too, I expect.",
               nxt="fw_what_the_fel_does", requires_quests=["fw_bandages_and_bitterroot"]))

    q.append(Q("fw_timber_for_the_barricade", "Timber for the Barricade", TOMASZ, 51, 52, "reclamation",
               "Bring Seasoned Ivywood from the Ivybound Treants in the Ruins of Constellas to Tomasz Wolny.",
               [fetch("fw_q_seasoned_ivywood", 6)],
               "I built houses outside Krakow for twenty years, until the day the world changed. Now I build barricades, and the Sentinels "
               "tell me I'm slow. I tell them it's called doing it properly.\n\nThe stakes on the Fel Line "
               "keep rotting. The fel gets into soft wood and eats it from the inside. What I need is old, "
               "hard wood, and the oldest wood in the valley walks around the Ruins of Constellas wearing "
               "ivy.\n\nThe ruins are west of the road, over the upper ford. The Ivybound Treants there drop "
               "limbs when they're beaten. Bring me the best of it.",
               "Look at that grain. That'll stand for fifty years, and the fel can chew on it all it likes.\n\n"
               "You did good work. This is from my own kit. I made it for myself and it never fit.",
               nxt="fw_stakes_on_the_line"))

    q.append(Q("fw_stakes_on_the_line", "Stakes on the Line", TOMASZ, 52, 52, "reclamation",
               "Carry the new stakes to the Sentinels' barricade across the road on the Fel Line.",
               [explore(71, 28, "the Sentinels' barricade on the Fel Line", SF)],
               "The stakes are cut and tarred, and somebody has to carry them up to the line.\n\nThat "
               "somebody isn't me, because my knees are fifty-three years old. You're younger, and you "
               "already know the way.\n\nThe barricade crosses the main road at the bottom of the Fel Line, "
               "north of the healed craters. Get the stakes up there, and make sure the Sentinels put the "
               "pointed end up this time.",
               "They put the pointed end up? Last time they planted half of them upside down to make a point about "
               "my measurements.\n\nThat line will hold now. You've done more for this town today than most "
               "people do in a month.",
               requires_quests=["fw_timber_for_the_barricade"],
               grant_items=carry("fw_tarred_stakes", "Bundle of Tarred Stakes",
                                 "Heavy, sharp and stinking of pine tar.")))

    q.append(Q("fw_hinges_that_hold", "Hinges That Hold", TOMASZ, 53, 54, "reclamation",
               "Bring Dark Iron Hinges from the Iron Golems of Khaz Varun, the dead Dark Iron city under "
               "Tempest Isle.",
               [fetch("fw_q_dark_iron_hinge", 4)],
               "I want the Sanctuary's gate to outlast all of us, and nothing in this forest will do it.\n\n"
               "There's an old Dark Iron city called Khaz Varun under Tempest Isle, across the sea. A dwarf "
               "trader who's been selling to the transplants since it happened told me their iron never rusts, and that the Iron Golems still walking its halls are "
               "held together with the best hinges ever forged.\n\nIt's a long way, I know. Take the boat "
               "to Tempest Isle and find the gate in the Shallows. Bring me the hinges off those golems and "
               "I'll hang a gate that the Legion itself couldn't shift.",
               "These are beautiful. Not a speck of rust, and look at the joint. That's real craft.\n\nYou "
               "went across the sea for my gate. The least I can do is put your name on it. Take this too.",
               requires_quests=["fw_stakes_on_the_line"]))

    q.append(Q("fw_catalogue_of_the_regrowth", "A Catalogue of the Regrowth", YUKI, 51, 52, "reclamation",
               "Visit Hollowbark Glade, the Ruins of Constellas and Shatter Scar Vale for Yuki Hashimoto's "
               "catalogue.",
               [explore(36, 148, "the heart of Hollowbark Glade", SF),
                explore(36, 104, "the moonwell in the Ruins of Constellas", SF),
                explore(70, 50, "the healed craters of Shatter Scar Vale", SF)],
               "I'm cataloguing everything that grows back. When I came through three years ago I didn't know any of these "
               "plants existed, and now I know more of them than I know people here.\n\nI need eyes in three "
               "places I can't get to myself: Hollowbark Glade in the south-west, the Ruins of Constellas in "
               "the west, and Shatter Scar Vale up the road to the north. Each of them is coming back in its "
               "own way.\n\nGo and stand in each one, look around properly, and come back and tell me what's "
               "growing. You don't have to know the names. I'll ask the right questions.",
               "Moonflowers in the craters already? That's a year ahead of what I expected.\n\nThis is "
               "wonderful. I'll write it all down tonight. Thank you for walking all that way for some "
               "flowers. Most people wouldn't.",
               nxt="fw_something_grows_under_tanaris"))

    q.append(Q("fw_something_grows_under_tanaris", "Something Grows Under Tanaris", YUKI, 54, 55, "reclamation",
               "Bring Royal Hive Resin from the Resin Weavers deep in the Royal Hive, under the Black Strand "
               "in Tanaris.",
               [fetch("fw_q_royal_resin", 5)],
               "A Dark Iron prospector came through and told me something I haven't been able to stop "
               "thinking about.\n\nUnder the Abyssal Sands in Tanaris there's a black strand of jungle, and "
               "under that there's a silithid hive called the Royal Hive. The resin they build it from "
               "traps living things and keeps them alive. If something green can live in there, in the dark, "
               "I need to know how.\n\nIt's the far side of the world. Go down through the Black Strand to "
               "the Royal Hive and bring me resin from the Resin Weavers who make it. It might teach us how "
               "to keep the Sanctuary green through the winter.",
               "There's moss in this one. Living moss, sealed in amber, and it's still green.\n\nYou don't "
               "know what you've given me. This might be the most important thing anybody's brought to this "
               "town. Thank you.",
               requires_quests=["fw_catalogue_of_the_regrowth"]))

    q.append(Q("fw_the_long_way_round", "The Long Way Round", ANA, 53, 54, "reclamation",
               "Take Ana Lucia's letter across the sea to Dr. Imani Mwangi at Ashclaim Landing on Tempest Isle.",
               [deliver("fw_ana_letter", "Ana Lucia's letter, to Dr. Imani Mwangi at Ashclaim Landing")],
               "There's a doctor on Tempest Isle called Imani Mwangi. She came through the same way I did, "
               "and we've been writing to each other for a year.\n\nThe last boat took my letter and lost "
               "it. I think the captain used it to light his pipe. So I'm asking you, because you'll get "
               "there and he won't.\n\nTake a boat to Tempest Isle and go to Ashclaim Landing. She works in "
               "the medic's tent. Tell her the Sanctuary's growing and I'm still walking.",
               "This is from Ana? Oh, thank goodness. I thought the sea had eaten her.\n\nYou've come a long way to "
               "deliver a letter. Sit down, you look like you need it. While you're here, the landing could "
               "use somebody like you.",
               zone=ES, turn_in_npc_id=IMANI,
               grant_items=carry("fw_ana_letter", "Ana Lucia's Letter",
                                 "Three closely written pages, folded into a moonleaf envelope.")))

    q.append(Q("fw_supper_for_sixty", "Supper for Sixty", NELANTHE, 51, 52, "reclamation",
               "Bring Silverhorn Venison and Moss-Tusk Flanks from the stags and boars of South Felwood.",
               [fetch("fw_q_silverhorn_venison", 6), fetch("fw_q_mosstusk_bacon", 5)],
               "There's a bed and a hot meal for everyone here, and that's a promise I'm finding harder to "
               "keep every week.\n\nLuis does wonders in the kitchen, but he can't cook what he hasn't got, and the transplants eat like they're still making up for the day they arrived. "
               "The Silverhorn Stags in the open forest and the Moss-Tusk Boars up in Shatter Scar Vale "
               "are fat this season.\n\nBring back venison and boar for the pot, and I'll see that you never "
               "go to bed hungry in this town.",
               "Venison and boar. Luis is going to cry, and then he's going to cook, and then everyone is "
               "going to be very happy.\n\nYou'll always have a seat by my fire. Take this as well. The last "
               "guest who left it behind isn't coming back."))

    q.append(Q("fw_prowlers_in_the_ruins", "Prowlers in the Ruins", ELM, 52, 52, "reclamation",
               "Kill Ruin Prowlers and Moonlit Wisps in the Ruins of Constellas, west of the road.",
               [k("Ruin Prowler", 10, SF), k("Moonlit Wisp", 8, SF)],
               "The Sentinels stand on the line, and so do I. The difference is that they talk more.\n\n"
               "The Ruins of Constellas are the forest's now, but the forest isn't always kind. The Ruin "
               "Prowlers hunt anyone who goes in, and the Moonlit Wisps are what's left of the Highborne who "
               "died there, and they don't remember being people.\n\nGo west over the upper ford and clear "
               "the ruins. Be gentle with the wisps if you can. They didn't choose this.",
               "The ruins are quiet and the wisps are resting.\n\nThat's good work. I don't say that often, "
               "because I don't say much. Take this with you.",
               nxt="fw_saberfang_the_elder"))

    q.append(Q("fw_saberfang_the_elder", "Saberfang the Elder", ELM, 53, 53, "reclamation",
               "Kill Saberfang the Elder, the old saber-cat that rules the Ruins of Constellas.",
               [boss("Saberfang the Elder", SF)],
               "There's a saber-cat in the ruins older than most of the trees, and he's started hunting "
               "druids.\n\nSaberfang the Elder used to keep the prowlers in line. Now he leads them. Something "
               "in the fel's last breath got into him, and it's still there.\n\nGo back to Constellas and "
               "find him. He's clever, and he'll come at you from behind. Don't let him.",
               "The ruins have a new master now, and it's the forest.\n\nYou fought well. Take this, and walk "
               "softly in there for a while. The prowlers will remember you.",
               requires_quests=["fw_prowlers_in_the_ruins"]))

    # =========================================================== THE NORTH
    q.append(Q("fw_talonbranch_holds", "Talonbranch Holds", ELANYA, 53, 54, "wastes",
               "Kill any Plaguefang Wolf or Fel-Rotted Bear you find in the wastes around the Talonbranch camp.",
               [k("Plaguefang Wolf", 10, NF), k("Fel-Rotted Bear", 8, NF)],
               "This is as far north as the Reclamation holds, and some nights it doesn't feel like holding.\n\n"
               "The Plaguefang Wolves and the Fel-Rotted Bears come at the stakes every night. They're "
               "not hunting us, and they don't care which of us were born here and which came through. They're sick, and they're angry, and we're the only living thing up here "
               "that doesn't smell of fel.\n\nThey roam the whole valley between here and the south gate. "
               "Thin them out. My Sentinels need one night's sleep before I ask them to do anything else.",
               "We slept, all of us, for the first time since we got here.\n\nThank you. That's not a small "
               "thing, and I won't pretend it is. Take this from the camp stores.",
               zone=NF))

    q.append(Q("fw_eyes_on_jaedenar", "Eyes on Jaedenar", ELANYA, 54, 54, "wastes",
               "Stand before the Black Gate of Jaedenar on the west wall of North Felwood, and kill the Shadow "
               "Council's people outside it: every Shadow Council Acolyte and Shadow Council Warlock you find.",
               [explore(24, 108, "the Black Gate of Jaedenar", NF), k("Shadow Council Acolyte", 8, NF),
                k("Shadow Council Warlock", 6, NF)],
               "There's a hold cut into the west wall of the valley. The Highborne built it, and the Shadow "
               "Council took it.\n\nThey call it Jaedenar. Everything wrong with North Felwood comes out of "
               "its gate. I need to know how many of them there are, and I need them to know we're watching.\n\n"
               "Go west along the road from the falls until you reach the Black Gate. Look at it properly, "
               "and then kill the Acolytes and Warlocks camped in front of it.",
               "So they're in there in strength. I thought they might be.\n\nYou've seen the gate. Sooner or "
               "later somebody has to go through it, and I think it's going to be you.",
               zone=NF, nxt="fw_beyond_the_black_gate"))

    q.append(Q("fw_the_moonstone", "The Moonstone", "item:fw_q_sentinel_moonstone", 54, 54, "sentinel",
               "Return the Sentinel's moonstone to Captain Saranis in the Emerald Sanctuary.",
               [deliver("fw_q_sentinel_moonstone", "the moonstone, to Captain Saranis in the Emerald Sanctuary")],
               "A Sentinel's moonstone on a broken chain, taken off a satyr. The name cut into the back is "
               "Vor'alith. Somebody in the Sanctuary will know who that was.",
               "Vor'alith is a name I haven't heard said out loud since Morlos'Aren fell.\n\nHe was one of "
               "mine. He opened the watch's gate to the satyrs that night, and he went with them when they "
               "left. If a satyr was wearing this, then he's out there, and he's one of them now.",
               zone=NF, turn_in_npc_id=SARANIS, nxt="fw_voralith_the_turncloak"))

    q.append(Q("fw_voralith_the_turncloak", "Vor'alith the Turncloak", SARANIS, 55, 55, "sentinel",
               "Find and kill Vor'alith the Turncloak outside the gate of Jaedenar in North Felwood.",
               [boss("Vor'alith the Turncloak", NF)],
               "I've sent word north. The Talonbranch scouts have seen a satyr outside Jaedenar who carries "
               "a Sentinel's glaive.\n\nThat has to be Vor'alith. He sold Morlos'Aren to the Jadefire and took "
               "their gift, and now he guards the Council's door. I'd go myself, but somebody has to hold "
               "this town.\n\nGo to Jaedenar's gate on the west wall of North Felwood and wait for him. Give "
               "him back his moonstone. Then finish it.",
               "So it's finished, and so is he.\n\nI'll put his name back on the Morlos'Aren stone. Not for him, "
               "but for the Sentinels he betrayed, so they have the whole story. Thank you.",
               requires_quests=["fw_the_moonstone"]))

    q.append(Q("fw_poison_in_the_falls", "Poison in the Falls", ARATHEL, 53, 54, "wastes",
               "Kill Seepage Oozes at Bloodvenom Falls, east of the road, and bring back Bloodvenom Samples.",
               [k("Seepage Ooze", 10, NF), fetch("fw_q_bloodvenom_sample", 6)],
               "The ground inside the stakes is clean because I clean it every morning. Nothing outside them "
               "is.\n\nThe river poisoning the whole valley comes off Hyjal's wall at Bloodvenom Falls, east "
               "of the road. The Seepage Oozes breed in the pool at the bottom, and they're spreading "
               "downstream into the south. If I understand the water, I might be able to turn it. One of the transplants says rivers where you're from get poisoned too, and that people turned them back. I'd like to believe her.\n\nGo to "
               "the falls. Kill the oozes and bring me the water, sealed. Don't drink it, obviously.",
               "Look at that. It's eating the glass.\n\nI can work with this, slowly. Every jar of it I "
               "understand is a mile of river I might be able to give back. Thank you.",
               zone=NF, nxt="fw_the_bloodvenom_rot"))

    q.append(Q("fw_the_bloodvenom_rot", "The Bloodvenom Rot", ARATHEL, 54, 54, "wastes",
               "Destroy the Bloodvenom Rot, the vast ooze at the bottom of Bloodvenom Falls.",
               [boss("The Bloodvenom Rot", NF)],
               "The samples you brought me all came from one source. There's something at the bottom of the "
               "falls' pool, feeding the poison and growing on it.\n\nI've been calling it the Bloodvenom Rot, "
               "for want of anything better. It's an ooze the size of a lodge, and it only rises when the "
               "pool is disturbed.\n\nGo back to the falls and disturb it. If it dies, the river might start "
               "running clean, one stretch at a time.",
               "The water below the falls is clearer already. Not clean, but clearer.\n\nThat's the first good "
               "news this valley's had in a long time. Take this with you. You've earned it, and then some.",
               zone=NF, requires_quests=["fw_poison_in_the_falls"]))

    q.append(Q("fw_ironwood_that_remembers", "Ironwood That Remembers", ARATHEL, 54, 55, "wastes",
               "Bring Warpwood Heartsplinters from the Warpwood Treants of Irontree Woods, in the north-west.",
               [fetch("fw_q_warpwood_splinter", 6)],
               "Irontree Woods was the greatest stand of ironwood in Kalimdor. Now it's dead, standing up.\n\n"
               "But not all of it. The Warpwood Treants that walk there still have a thread of green in their "
               "hearts. If I can get those splinters back to the Sanctuary, Old Thornbark thinks he can "
               "grow them.\n\nIrontree Woods is north-west of here, past the crater. Bring me the "
               "heartsplinters. Try to imagine the woods the way they were while you're doing it.",
               "There's green in every one. Faint, but it's there.\n\nThe woods aren't dead. I knew it. "
               "Thank you for bringing them back to me.",
               zone=NF, nxt="fw_ironbark_the_blighted"))

    q.append(Q("fw_ironbark_the_blighted", "Ironbark the Blighted", ARATHEL, 55, 55, "wastes",
               "Bring down Ironbark the Blighted, the great treant of Irontree Woods.",
               [boss("Ironbark the Blighted", NF)],
               "The warpwood answer to something. The oldest of them is still walking, and he's the reason "
               "nothing in those woods will heal.\n\nIronbark the Blighted was the woods' guardian. The fel "
               "turned him against everything he was meant to protect, and he's still guarding it, from us.\n\n"
               "Go back to Irontree Woods and put him to rest. The woods will thank you, even if they can't "
               "say it.",
               "He's still, and the woods feel lighter, even from here.\n\nThat was a hard thing to ask, and "
               "you did it. Thank you.",
               zone=NF, requires_quests=["fw_ironwood_that_remembers"]))

    q.append(Q("fw_felpaw_village", "Felpaw Village", BARROWPAW, 53, 54, "timbermaw",
               "Kill Deadwood Warriors and Deadwood Den Watchers in Felpaw Village, north-east of Talonbranch.",
               [k("Deadwood Warrior", 8, NF), k("Deadwood Den Watcher", 6, NF)],
               "Felpaw was my cousins' village. I still know every path in and out of it, and I'll tell you "
               "which ones they're watching.\n\nThe Deadwood drank the fel water because it was all there "
               "was, and it took them. They're not my cousins any more. They're something wearing their "
               "fur.\n\nFelpaw Village is north-east of the camp, up the eastern track. Fight the warriors "
               "and the den watchers. I can't do it myself. I'd see faces.",
               "You came back. Some of them didn't, I expect.\n\nI won't ask about it. Thank you for doing "
               "what I couldn't. Here, this was my uncle's.",
               zone=NF, nxt="fw_the_totems_of_felpaw"))

    q.append(Q("fw_the_totems_of_felpaw", "The Totems of Felpaw", BARROWPAW, 54, 54, "timbermaw",
               "Take Deadwood Fetishes from the Deadwood Shamans of Felpaw Village.",
               [fetch("fw_q_deadwood_fetish", 6)],
               "The Deadwood shamans carry fetishes that hum with fel. I think that's how the sickness "
               "keeps hold of them.\n\nIf I can take enough of them back to Grumhall, the Timbermaw elders "
               "might be able to understand the hold it has on them. And if they can understand it, maybe "
               "they can break it, one cousin at a time.\n\nGo back to Felpaw and take the fetishes off the "
               "Deadwood Shamans. Don't listen to the humming.",
               "These are worse than I thought. You can hear them even from inside the bag.\n\nThe elders "
               "will want these. It's a start. It's more than we've had.",
               zone=NF, requires_quests=["fw_felpaw_village"], nxt="fw_chieftain_grimpelt"))

    q.append(Q("fw_chieftain_grimpelt", "Chieftain Grimpelt", BARROWPAW, 55, 55, "timbermaw",
               "Kill Chieftain Grimpelt, the Deadwood chief of Felpaw Village.",
               [boss("Chieftain Grimpelt", NF)],
               "Grimpelt was the first of my cousins to drink the fel water, and he made the others follow.\n\n"
               "He's chieftain of Felpaw now, and as long as he's alive none of them will even think about "
               "coming back. He doesn't fight often. When he does, it's with a log the size of a canoe.\n\n"
               "Go back to Felpaw and find him, and end it. I'll tell the elders it was done properly.",
               "He's gone, and Felpaw has no chieftain now.\n\nMaybe one of them will look up and remember who "
               "they used to be, and maybe they won't. Either way, you gave them the chance. The Timbermaw "
               "won't forget it.",
               zone=NF, requires_quests=["fw_the_totems_of_felpaw"]))

    q.append(Q("fw_to_timbermaw_hold", "To Timbermaw Hold", BARROWPAW, 54, 55, "timbermaw",
               "Stand at the Timbermaw Gate at the north end of North Felwood, and speak with Gatewarden "
               "Thornclaw.",
               [explore(94, 10, "the Timbermaw Gate", NF)],
               "Beyond the valley's north end is Timbermaw Hold, my people's home. The tunnel through it "
               "goes all the way to Winterspring.\n\nThe elders closed it when the fel came. Thornclaw guards "
               "the door now, and he's never let anyone through who wasn't Timbermaw. I'd like you to meet "
               "him, because one day he'll open it, and I want him to know your face.\n\nGo north to the end "
               "of the road. The gate's between the two totems.",
               "Barrowpaw sent you? Then you're welcome here, even if I can't let you through.\n\nThe tunnel "
               "is closed. When the elders open it, you'll be the first one I let past. That's a promise "
               "from the Timbermaw, and we keep those.",
               zone=NF, turn_in_npc_id=THORNCLAW))

    q.append(Q("fw_what_the_fel_does", "What the Fel Does", MARCUS, 53, 54, "wastes",
               "Bring Jadefire Antlers from the Jadefire Stags of North Felwood to Marcus Oyelaran.",
               [fetch("fw_q_jadefire_antler", 6)],
               "Nkechi sent you up here with blood samples? She's the best doctor south of here, and the only "
               "one, which helps.\n\nI was a paramedic in Toronto before I came through. Up here it's burns, bites and things I "
               "don't have names for yet. The Jadefire Stags have the fever too, but they don't die of it. "
               "Something in their antlers fights it, and I'd like to know what.\n\nThe stags wander the "
               "open wastes and the woods to the north-west. Bring me their antlers. Gently, if you can.",
               "These are fascinating. They're burning without burning.\n\nI think I can make something out "
               "of these, given time. Not a cure, maybe, but something to slow it down. Thank you.",
               zone=NF, requires_quests=["fw_the_fel_fever"]))

    q.append(Q("fw_sedatives", "Sedatives", MARCUS, 54, 55, "wastes",
               "Bring Hellhound Glands from the Felbrand Hellhounds in Felbrand Crater, west of the road.",
               [fetch("fw_q_hellhound_gland", 5)],
               "This one's going to sound odd, so bear with me.\n\nThe Felbrand Hellhounds in the crater have "
               "a gland that calms them down after they've killed. I've seen it work. If I can get the oil "
               "out of it, I can make a sedative strong enough to hold someone through the worst of the "
               "fever.\n\nThe crater's west of the road, south of the woods. The hounds run with the felguard "
               "there. Bring me the glands and I'll explain the rest once I'm sure it works.",
               "That's perfect, and disgusting, but mostly perfect.\n\nYou've just made the worst night of somebody's life a lot "
               "more bearable. I'll tell them who to thank when they wake up.",
               zone=NF))

    q.append(Q("fw_fire_in_the_crater", "Fire in the Crater", THORNCLAW, 54, 55, "wastes",
               "Kill Felbrand Felguard, Felbrand Hellhounds and Crater Imps in Felbrand Crater.",
               [k("Felbrand Felguard", 8, NF), k("Felbrand Hellhound", 8, NF), k("Crater Imp", 8, NF)],
               "I can't let you through the tunnel, but I can tell you what keeps me awake at this door.\n\n"
               "There's a crater west of the road where an infernal came down when the Legion first arrived. "
               "They never left it. The Felbrand Felguard and their hounds drill there every day, and the "
               "imps watch the road for them.\n\nGo south to the crater and break the drill. If the Legion "
               "is getting ready for something, I'd rather it wasn't ready.",
               "The crater's burning lower tonight. I can see it from here.\n\nThat's a debt the Legion "
               "owes the Timbermaw, and you've collected some of it.",
               zone=NF, nxt="fw_pyrrhax_the_fallen_star"))

    q.append(Q("fw_pyrrhax_the_fallen_star", "Pyrrhax the Fallen Star", THORNCLAW, 55, 55, "wastes",
               "Kill Pyrrhax the Fallen Star, the infernal at the heart of Felbrand Crater.",
               [boss("Pyrrhax the Fallen Star", NF)],
               "The thing that made the crater is still in it.\n\nPyrrhax the Fallen Star fell from the sky "
               "and burned a hole in the forest, and he's been sitting at the bottom of it ever since, "
               "keeping it burning. Everything in the crater is his.\n\nGo back down there and put out the "
               "star. He doesn't come out often, but he'll come out for you.",
               "The crater's dark, for the first time since I was a cub.\n\nTake this with you. The "
               "Timbermaw don't forget the ones who help them.",
               zone=NF, requires_quests=["fw_fire_in_the_crater"]))

    q.append(Q("fw_jadefire_glen", "Jadefire Glen", THORNCLAW, 53, 54, "wastes",
               "Kill Jadefire Rogues and Jadefire Tricksters in Jadefire Glen, in the south-west of North "
               "Felwood.",
               [k("Jadefire Rogue", 8, NF), k("Jadefire Trickster", 8, NF)],
               "The satyrs in the south-west took the Highborne ruins there and built their fel braziers "
               "on top of them.\n\nThey call it Jadefire Glen. The Rogues raid the road, and the Tricksters "
               "play games with the scouts until somebody dies. They're the reason nobody walks to "
               "Talonbranch alone, whether they were born in this forest or came out of nowhere three years ago like you.\n\nThe glen's south-west of the road, near the south gate. Clear it out. "
               "Don't let the Tricksters talk to you.",
               "The road south is clearer. The scouts will thank you, if they ever stop looking over their "
               "shoulders.\n\nYou did good work out there, and this is yours.",
               zone=NF, nxt="fw_prince_aelvorn"))

    q.append(Q("fw_prince_aelvorn", "Prince Aelvorn the Unmade", THORNCLAW, 54, 54, "wastes",
               "Kill Prince Aelvorn the Unmade, the satyr lord of Jadefire Glen.",
               [boss("Prince Aelvorn the Unmade", NF)],
               "The satyrs follow a lord who calls himself a prince.\n\nAelvorn the Unmade was Highborne once. "
               "He drank from the Well, and then from something worse, and he's been unmaking himself a "
               "little more every century. Now he rules a glen of satyrs and calls it a kingdom.\n\nGo back "
               "to Jadefire Glen and end his reign. He'll be at the heart of it, among the braziers.",
               "The prince is dead and the glen has no king.\n\nThe Jadefire won't stop because of it. But "
               "they'll be arguing about who's next for a long time, and that's time we can use.",
               zone=NF, requires_quests=["fw_jadefire_glen"]))

    # =========================================================== JAEDENAR (given in the hubs)
    q.append(Q("fw_beyond_the_black_gate", "Beyond the Black Gate", ELANYA, 53, 54, "jaedenar",
               "Go through the Black Gate of Jaedenar and kill Hold-Warden Gorvash and Inquisitor Xel'thas.",
               [boss("Hold-Warden Gorvash", JD), boss("Inquisitor Xel'thas", JD)],
               "You've seen the gate. Now I need you to go through it.\n\nThe first thing inside is Hold-Warden "
               "Gorvash, who keeps the yard and plants his banner where his guards can see it. Past him, in "
               "the Hall of Whispers, Inquisitor Xel'thas decides who lives. Nobody has walked out past "
               "either of them.\n\nTake a full party. Go in through the Black Gate on the west wall, kill the "
               "Warden and the Inquisitor, and come back and tell me what's beyond them.",
               "Both of them? Then the Hold's open.\n\nYou've done what an army couldn't. Rest, because "
               "there's more of Jaedenar than that, and it goes down.",
               zone=NF, requires_quests=["fw_eyes_on_jaedenar"], nxt="fw_doom_in_the_pit"))

    q.append(Q("fw_the_duskwhisper_sisters", "The Duskwhisper Sisters", SARANIS, 54, 55, "jaedenar",
               "Kill the Duskwhisper Sisters and their demon Zeth'rak in the Black Library of Jaedenar.",
               [boss("The Duskwhisper Sisters", JD), boss("Zeth'rak the Pactbound", JD)],
               "There are two sisters in Jaedenar who were Sentinels once. I trained them.\n\nThe Duskwhisper "
               "Sisters made a pact with an eredar called Zeth'rak the Pactbound, and they keep him in the Black Library, "
               "west of the Hall of Whispers. They drain the life from anyone they catch and give it to "
               "each other. I've lost four scouts to them.\n\nGo into Jaedenar and end them. Kill the sisters "
               "first. The demon is only there because of them.",
               "They're gone, and I'd hoped, once, that they'd come home.\n\nThank you for doing it quickly. Take "
               "this with you. It's the last of what I kept for them."))

    q.append(Q("fw_close_the_portals", "Close the Portals", ARATHEL, 54, 55, "jaedenar",
               "Kill Master Summoner Kaz'reth in Jaedenar's Sanctum, and take Pages of the Summoning Codex "
               "from the Shadow Council Summoners.",
               [boss("Master Summoner Kaz'reth", JD), fetch("fw_q_summoning_codex", 5)],
               "Every demon in North Felwood came through a door the Council opened, and Kaz'reth opens the "
               "doors.\n\nHe's the Master Summoner. He works from the Summoner's Sanctum at the top of the "
               "Hold, and his summoners carry pages of a codex that tells them how. Kill him, and take the "
               "pages, and I'll find out how to close what they've opened.\n\nYou'll find the Sanctum north of "
               "the Hall of Whispers. Don't read the pages.",
               "You didn't read them? Neither will I, until I'm ready.\n\nWith these, I can start "
               "unpicking the circles. It'll take years, but there won't be any new demons while I'm doing it.",
               zone=NF))

    q.append(Q("fw_what_lives_in_the_maw", "What Lives in the Maw", MARCUS, 54, 55, "jaedenar",
               "Kill the Entropic Horror in the Maw, deep in Jaedenar's Summoning Pit.",
               [boss("The Entropic Horror", JD)],
               "My patients describe the same thing when the fever's at its worst. An eye, and tentacles, "
               "and the feeling of coming apart.\n\nThe scouts say it's real. There's something in a side "
               "cave of Jaedenar's pit called the Maw. They call it the Entropic Horror, and it unmakes anything it "
               "looks at. I think it's "
               "what's feeding the fever.\n\nGo down into the pit and find the Maw, and kill The Entropic Horror. Then come back "
               "and tell me whether my patients stop dreaming about it.",
               "Two of them slept through the night. No dreams, they said.\n\nI don't understand it, and I've "
               "stopped needing to. Thank you.",
               zone=NF))

    q.append(Q("fw_the_chained_ancient", "The Chained Ancient", AELYRA, 55, 55, "jaedenar",
               "Free Grimbark the Chained, the corrupted ancient held in the Chained Grove of Jaedenar's pit.",
               [boss("Grimbark the Chained", JD)],
               "The Council has an ancient in chains at the bottom of their pit, and they've been pouring "
               "the fel into him for a hundred years.\n\nHis name was Grimbark. He was a guardian of this "
               "forest before any of us came. They've made him into something that feeds on the fel and "
               "grows from it, and there's no saving what he is now.\n\nGo into Jaedenar's pit and find the "
               "Chained Grove, west of the descent. Free him the only way that's left.",
               "He's free now. I felt it the moment he went.\n\nThe forest has one more guardian resting now, "
               "and one less weapon in the Council's hands. That was a kindness, and a hard one. Thank you."))

    q.append(Q("fw_highborne_stonework", "Highborne Stonework", TOMASZ, 54, 55, "jaedenar",
               "Bring Highborne Keystones from the Jaedenar Felguard in the Shadow Hold.",
               [fetch("fw_q_highborne_keystone", 5)],
               "The elves tell me Jaedenar was built by the Highborne, and that nobody alive knows how they "
               "cut the arches.\n\nI'd like to know how they cut the arches. The Jaedenar Felguard pull the "
               "keystones out to use as weights, from what the scouts tell me, and they carry them round on "
               "their belts.\n\nIf you're going into the Hold anyway, bring me some of those stones. I'll "
               "build the Sanctuary a gatehouse the Highborne would have been jealous of.",
               "Look at that. There's not a gap you could fit a hair into.\n\nThis is going to keep me up at "
               "night for months, in the best way. Thank you."))

    q.append(Q("fw_doom_in_the_pit", "Doom in the Pit", ELANYA, 55, 55, "jaedenar",
               "Go down into Jaedenar's Summoning Pit and kill Doomlord Kazrak.",
               [boss("Doomlord Kazrak", JD)],
               "Under the Hold there's a pit, and in the pit there's a doomlord.\n\nKazrak commands the demons "
               "the Council summons. He wears armour forged in the Nether, and it gets thicker the longer "
               "you give him. Bring weapons that can cut it, and don't let the fight drag.\n\nThe way down is "
               "behind the Summoner's dais. Kill Kazrak and the pit's army has no general.",
               "The doomlord's dead. The scouts say the demons in the wastes don't know what to do with "
               "themselves.\n\nThere's one more thing down there, and you know what I'm going to ask.",
               zone=NF, requires_quests=["fw_beyond_the_black_gate"], nxt="fw_the_unbound"))

    q.append(Q("fw_the_unbound", "The Unbound", ELANYA, 55, 56, "jaedenar",
               "Kill Zar'gothrax the Unbound on the Burning Throne at the bottom of Jaedenar.",
               [boss("Zar'gothrax the Unbound", JD)],
               "Everything the Council has done in Felwood has been for one thing, and it's sitting on a "
               "throne at the bottom of their pit.\n\nZar'gothrax the Unbound. A demon lord they called "
               "through and couldn't send back. The Council serves him now, whether they admit it or not, "
               "and as long as he sits there the fel will keep coming.\n\nGo all the way down, to the Burning "
               "Throne. He won't die easily, and he'll hold on at the end. Hit him again when he does.",
               "It's over, and the throne's empty.\n\nFelwood isn't saved, not yet. But for the first time it can "
               "be. The Reclamation will remember who went down there. So will I.",
               zone=NF, requires_quests=["fw_doom_in_the_pit"]))
    return q
