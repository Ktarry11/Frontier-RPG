"""Valley of Trials, plain. Camp at (60,25). Sagebrush Flat and the Den are west, the scorpid nest
and the Burning Blade Coven north-east, the sagewood grove just east, the Windrift Dunes east,
Trailwater Spring south, the Cinderjaw Wastes far south-west, and the road to Durotar east.

Second pass, Kyle 14 Nov 2026: "For the love of God bro. Make them talk like people." The first
pass was still composed: teachers summing up the lesson, remarks about what kind of person you
are, careful backstory. These are people at a camp asking for a hand. They say what's going on,
where, and what they want, the way you'd say it to someone you just met, and that's it."""

QUESTS = {
    "vot_first_blood": dict(
        description="Kill Mottled Boars on Sagebrush Flat, west of camp.",
        accept_text=(
            "Easy, take it slow. You took a fall. I'm Nakhtar, and you're not the first one to "
            "wake up here like this, so don't worry about it.\n\n"
            "Can you still swing a weapon? Go and kill a few of the boars out on Sagebrush Flat, "
            "just west of camp, and we'll find out."),
        turn_in_text="Good, you can still fight. Get some food in you before you head back out. "
                     "Thanks.",
    ),
    "vot_scorpid_trouble": dict(
        description="Kill Scorpid Workers at the nest north-east of camp.",
        accept_text=(
            "The scorpids have been wandering a lot further from their nest the last few days. "
            "Could you go and kill some of the workers? The nest's north-east of camp.\n\n"
            "Watch the tail, that's where the sting is."),
        turn_in_text="That'll push them back for a bit. Thanks. Have a look through the camp "
                     "stores and take something you can use.",
    ),
    "vot_den_scout": dict(
        description="Go into the Den, the cave west of camp, have a look around and come back to "
                    "Kuraw.",
        accept_text=(
            "I'm Kuraw. Have you been in a cave yet? The Den's a small one in the ridge west of "
            "camp, and it's a good one to start with.\n\n"
            "Go in and have a look around. Be careful in the small rooms, you can end up with "
            "three of them on you at once. Come back and tell me what's in there."),
        turn_in_text="Alright, that's useful, thanks. Now I know what we're dealing with in "
                     "there.",
    ),
    "vot_nest_guardian": dict(
        description="Kill the Nest Guardian in the deepest room of the Den, west of camp.",
        accept_text=(
            "There's a big one at the back of the Den the recruits call the Nest Guardian, and "
            "it's started wandering the halls. It's the first thing round here that can actually "
            "kill you, so take it seriously.\n\n"
            "It's in the last room, past the nursery. Can you go and deal with it?"),
        turn_in_text="You got it? Nice work. Thanks for that.",
    ),
    "vot_vile_familiars": dict(
        description="Kill Vile Familiars in the Burning Blade Coven, north-east of camp past "
                    "the scorpid nest.",
        accept_text=(
            "We've got demons in the valley now, if you can believe it. I've been on watch here "
            "three years and never saw one until last week.\n\n"
            "They're in the Burning Blade Coven, the cave at the end of the road north-east of "
            "camp, past the scorpids. Can you go in and kill some of the familiars? Don't go any "
            "deeper than that on your own, though."),
        turn_in_text="Thanks. It's gone quiet in there for now, but whoever's in charge of them "
                     "is still around.",
    ),
    "vot_yarrog_baneshadow": dict(
        description="Kill Yarrog Baneshadow at the back of the Burning Blade Coven, north-east of "
                    "camp.",
        accept_text=(
            "We found out who's running that cave. His name's Yarrog Baneshadow, and he's right "
            "at the back of the Coven.\n\n"
            "He keeps calling more demons in the longer you fight him, so go straight for him and "
            "don't drag it out. I'd go myself but I can't leave the road."),
        turn_in_text="He's dead? Great. That's a big help, thank you.",
    ),
    "vot_sagewood_petals": dict(
        description="Bring Marta Sagewood Petals from the sprites in the sagewood grove, just "
                    "east of camp.",
        accept_text=(
            "Half the recruits come back from the nest with scorpid venom in them, and I'm out "
            "of sagewood petals for the remedy.\n\n"
            "The sprites in the grove just east of camp drop them if you spook them. Could you "
            "get me some? Try not to squash them."),
        turn_in_text="These are perfect, thanks. That'll keep a few of them on their feet.",
    ),
    "vot_felstalkers": dict(
        description="Kill Felstalker Whelps in the Burning Blade Coven, north-east of camp.",
        accept_text=(
            "The demons brought hounds with them too. You'll probably run into them in the Coven "
            "before anything else.\n\n"
            "While you're in there, can you kill some of the whelps? No point making two trips."),
        turn_in_text="Thanks. That's a lot less of them to worry about.",
    ),
    "vot_graduation": dict(
        description="Follow the road east out of the valley to Razor Hill and find Weapons "
                    "Trainer Grokk.",
        accept_text=(
            "I think you're done here, honestly. You've handled everything this valley's got.\n\n"
            "Head into Durotar and go to Razor Hill. Just follow the road east out of the valley "
            "and stay on it. When you get there, find Grokk, the weapons trainer, and tell him I "
            "sent you."),
        turn_in_text="Nakhtar sent you? Good, welcome to Razor Hill. Come and find me whenever "
                     "you want some training.",
    ),
    "vot_old_tusk": dict(
        description="Kill Mottled Boars and Old Tusk on Sagebrush Flat, west of camp.",
        accept_text=(
            "There's one boar out on Sagebrush Flat that's way bigger than the rest. The "
            "recruits call him Old Tusk. He keeps charging through the training dummies, and "
            "he's going to hurt somebody soon.\n\n"
            "Can you go and kill him? Take out a few of the other boars first and "
            "he'll come to you. He's the one that doesn't run."),
        turn_in_text="You got Old Tusk? Brilliant, I've been worried about that one for ages. "
                     "Here, take these.",
    ),
    "vot_carrion_circle": dict(
        description="Kill Carrion Vultures and Dustwind Jackals in the Windrift Dunes, east "
                    "of camp.",
        accept_text=(
            "Don't tell Nakhtar I'm handing out jobs, he wants me resting. A scorpid got my leg "
            "and I can't walk on it yet.\n\n"
            "The vultures have started circling over me every afternoon, and the jackals keep "
            "creeping closer at night. It's getting on my nerves. They hang around the Windrift "
            "Dunes, east of camp. Could you go and thin them out?"),
        turn_in_text="Ah, that's so much better. Thanks. I'm not supposed to give out coin, but "
                     "here, have some of my old gear.",
    ),
    "vot_troubled_waters": dict(
        description="Kill Marsh Skimmers and Trailwater Toads at Trailwater Spring, south of "
                    "camp.",
        accept_text=(
            "I can't get clean water out of the spring south of camp any more. It's crawling "
            "with skimmers, and the toads keep stirring up the mud.\n\n"
            "Could you kill some of the skimmers and toads for me? Watch your step at the edge, "
            "the mud's deep."),
        turn_in_text="It's clearing up already. Thanks so much.",
    ),
    "vot_gulpjaw": dict(
        description="Kill Old Gulpjaw and Trailwater Toads at Trailwater Spring, south of "
                    "camp.",
        accept_text=(
            "So it wasn't just the skimmers. There's a huge toad living in the spring now, the "
            "recruits call it Old Gulpjaw, and it's started going for people.\n\n"
            "It sits at the bottom and waits. If you kill a couple of the smaller toads it'll "
            "come up. Fight it on the bank, don't go in the water after it."),
        turn_in_text="It's gone? Oh, thank goodness. Thank you.",
    ),
    "vot_heartwood": dict(
        description="Kill Thornroot Saplings and Bramblethorn the Ancient in the sagewood "
                    "grove, just east of camp.",
        accept_text=(
            "Something's wrong in the sagewood grove. The saplings have started walking around "
            "and attacking people, and there's a big old tree moving with them. Everyone calls "
            "it Bramblethorn.\n\n"
            "Could you kill some of the saplings and then deal with Bramblethorn? The grove's "
            "just east of camp."),
        turn_in_text="It's so much quieter in there now. Thank you, take whatever you like.",
    ),
    "vot_brood_below": dict(
        description="Kill Cave Skitterers, Den Webspinners and Egg Tenders in the Den, "
                    "west of camp.",
        accept_text=(
            "The Den's basically a nest, and there's a lot more of them further in. I want them "
            "thinned out before anyone goes after the big one at the back.\n\n"
            "Can you clear out some of the skitterers and webspinners, and the egg tenders in the "
            "nursery?"),
        turn_in_text="Thanks, that'll make the next bit a lot easier.",
    ),
    "vot_windrift_omens": dict(
        description="Kill Dust Devils and Sandpincer Crawlers in the Windrift Dunes, east of "
                    "camp.",
        accept_text=(
            "Something weird is going on out in the Windrift Dunes. The dust devils keep "
            "following the road, and sandpincers are popping up out of nowhere.\n\n"
            "Can you go out there and kill some of the dust devils and sandpincers? If the sand "
            "starts moving under you, get off it quick."),
        turn_in_text="Thanks. It's much calmer out there now. Come and see me when you're ready, "
                     "there's one more thing.",
    ),
    "vot_cinderjaw": dict(
        description="Kill Ember Wisps, Ashback Basilisks and Smolderhide in the Cinderjaw "
                    "Wastes, far south-west past the lake.",
        accept_text=(
            "Way down in the south-west, past the lake, there's a patch of burnt ground called "
            "the Cinderjaw Wastes. It's been spreading toward the lake for years.\n\n"
            "There are fire wisps and basilisks out there, and a big thing the scouts call "
            "Smolderhide. Can you clear out some of the wisps and basilisks, and then kill Smolderhide? It's "
            "the toughest job I've got, so don't feel bad if you want to wait."),
        turn_in_text="You actually killed Smolderhide? That's amazing. Thank you.",
    ),
    "vot_grosks_trophy": dict(
        description="Kill Dustwind Jackals and Sandfang in the Windrift Dunes, east of camp, "
                    "for Grosk.",
        accept_text=(
            "Hey, you're the one everyone's talking about, right? I need a favour.\n\n"
            "There's this old white jackal out in the Windrift Dunes called Sandfang. Nobody's "
            "ever caught it. I want it as a trophy before I leave the valley, but I can't catch "
            "it on my own.\n\n"
            "Can you kill some of its pack and then get Sandfang? Please don't tell my mum."),
        turn_in_text="No way, you got it! Thanks so much. My mum's going to kill me. Here, take "
                     "this.",
    ),
    "vot_fel_shards": dict(
        description="Bring Fizzcrank Fel-Tainted Shards from the acolytes, initiates and "
                    "ritual guards in the Burning Blade Coven, north-east of camp.",
        accept_text=(
            "Oh, hello! Are you going into the Coven? The crystals in there give off this weird "
            "heat and I'd love to know why.\n\n"
            "The cultists carry little shards of it on their belts. Could you bring me some? "
            "Don't grab them with your bare hands, though."),
        turn_in_text="Oh, these are great, thank you! Hang on, is that one smoking? Never mind, "
                     "take anything you want off the bench.",
    ),
    "vot_silk_for_rhaka": dict(
        description="Bring Rhaka Den Silk Spools from the webspinners and skitterers in the "
                    "Den, west of camp.",
        accept_text=(
            "My son's one of the recruits, and I want to make him a proper cloak before he goes "
            "out again. The silk the webspinners make in the Den is really strong.\n\n"
            "I can't make myself go in there, though. Could you get me some spools? The Den's "
            "the cave in the ridge west of camp."),
        turn_in_text="This is lovely silk, thank you. I made an extra one while I waited, it's "
                     "yours.",
    ),
    "vot_mother_of_nest": dict(
        description="Kill Venomtail Scorpids and Broodmother Sarrix at the scorpid nest, "
                    "north-east of camp.",
        accept_text=(
            "All those scorpids come from one big mother at the nest, Broodmother Sarrix. As "
            "long as she's alive they'll just keep coming.\n\n"
            "She's got venomtails guarding her, so kill a few of those first and then go for "
            "her. It's a long fight, so make sure you're healed up before you start."),
        turn_in_text="Sarrix is dead? That's huge. Thanks.",
    ),
    "vot_ritual_disruption": dict(
        description="Kill Burning Blade Initiates and Coven Ritual Guards in the Burning "
                    "Blade Coven, north-east of camp.",
        accept_text=(
            "Bad news. They're drawing a summoning circle deeper in the Coven, and if they "
            "finish it we're going to have something a lot worse than Baneshadow on our "
            "hands.\n\n"
            "Can you kill some of the initiates and the ritual guards? Get the guards "
            "first if you can, they're the ones doing the summoning."),
        turn_in_text="The circle's broken? Thank you. Now it's just Baneshadow left in there.",
    ),
}

GREETINGS = {
    "valley_of_trials": {
        "vot_greeter": (
            "Hey, you're awake. I'm Nakhtar. This is the Valley of Trials, where the Horde trains "
            "new recruits. I've got some jobs for you when you're ready."),
        "vot_guard_1": (
            "If you're looking for something to fight, there's plenty. Boars to the west, "
            "scorpids to the north-east, and a cave full of demons past the scorpids."),
        "vot_elder": (
            "I'm Kuraw, I help train the recruits. If you want to learn how caves work, come "
            "and talk to me."),
        "vot_recruit_watcher": (
            "Watch yourself on Sagebrush Flat. Most of the boars are fine, but there's one "
            "massive one out there that keeps knocking over the training dummies."),
        "vot_goblin_tinkerer": (
            "Hi! I'm Fizzcrank, I'm doing a bit of research. Please don't touch the bench, I "
            "think part of it's on fire."),
        "vot_orc_mother": (
            "My son's one of the recruits here. If you're going into the Den, come and see me "
            "first, I could use a hand."),
        "vot_wounded_grunt": (
            "A scorpid got my leg. Nakhtar says I'll walk again soon, but for now I'm stuck "
            "sitting here."),
        "vot_young_orc": (
            "I've killed more boars than anyone my age here. I want something better than a "
            "boar before I leave, though."),
        "ct_vot": "Come and see me when you've gained a level and I'll teach you something "
                  "new. It costs a bit of coin.",
        "pt_vot_forge": (
            "I can teach you mining. The forge is just north of here if you want to smelt "
            "anything. For smithing you'll need to go to Razor Hill."),
        "pt_vot_herbs": (
            "I can teach you herbalism. If you want to learn to brew things, Kagra teaches "
            "alchemy in Razor Hill."),
        "pt_vot_wood": (
            "I can teach you woodcutting. The sawmill's just north-west of here, past Marta's "
            "fire. Hulda teaches woodworking in Razor Hill if you want to build things."),
    },
}

VENDOR_GREETINGS = {
    "kalimdor_and_lordaeron": {
        "valley_vendor": (
            "Hi, love. I've got potions, food and drink, and a few bits for your trade. Stock up "
            "before you head east to Durotar, there's nothing to buy until Razor Hill."),
    },
}
