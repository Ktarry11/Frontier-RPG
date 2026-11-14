"""Valley of Trials, plain. Camp at (60,25). Sagebrush Flat and the Den are west, the scorpid nest
and the Burning Blade Coven north-east, the sagewood grove just east, the Windrift Dunes east,
Trailwater Spring south, the Cinderjaw Wastes far south-west, and the road to Durotar east."""

QUESTS = {
    "vot_first_blood": dict(
        description="Nakhtar wants to see whether you can still fight. Kill 5 Mottled Boars on "
                    "Sagebrush Flat, west of camp.",
        accept_text=(
            "Sit up slowly, you've had a fall. My name's Nakhtar. You're the fourth person this season "
            "to wake up in this valley with no idea how you got here, so I won't ask you where "
            "you came from.\n\n"
            "What I need to know is whether you can still hold a weapon. The boars on Sagebrush "
            "Flat, west of camp, are a good place to find out. Go and kill five of them and come "
            "back to me."),
        turn_in_text=(
            "You're still standing, so you can fight. That's the main thing I needed to know.\n\n"
            "Sit down and eat something before you go out again. There's more work in this valley "
            "when you're ready."),
    ),
    "vot_scorpid_trouble": dict(
        description="Kill 6 Scorpid Workers at the nest north-east of camp.",
        accept_text=(
            "The scorpids have been coming further out from their nest than they should, three "
            "days running now. I don't know why yet and I don't like it.\n\n"
            "The nest is north-east of camp. Go and kill six of the workers so they pull back. "
            "Watch their tails more than their claws. The sting is what does the damage."),
        turn_in_text=(
            "That should keep them closer to home for a while. You did well out there.\n\n"
            "You've done two jobs for this valley now, so take something from the camp stores. "
            "Pick whatever suits the way you fight."),
    ),
    "vot_den_scout": dict(
        description="Go into the Den, the cave west of camp, and look around, then come back to "
                    "Kuraw.",
        accept_text=(
            "I'm Kuraw, and I teach the recruits here. The Den is the small cave in the ridge "
            "west of camp. Nothing in there should kill you if you're careful, which is why I "
            "want you to go in there first.\n\n"
            "Caves fight differently from open ground. The rooms are small, and if you walk into "
            "the wrong one you'll have three of them on you at once instead of one. Go in, look "
            "around properly, and come back and tell me what you saw."),
        turn_in_text=(
            "You came back and told me about the place, not just the fight. Most people only "
            "notice whatever's attacking them.\n\n"
            "Keep doing that and you'll last a lot longer out there."),
    ),
    "vot_nest_guardian": dict(
        description="Kill the Nest Guardian in the deepest room of the Den, west of camp.",
        accept_text=(
            "Something in the back of the Den has started walking the halls instead of staying "
            "in its room. The recruits call it the Nest Guardian.\n\n"
            "It isn't the worst thing in this valley, but it's the first thing you'll meet that "
            "can really kill you if you're careless. I'd rather you learned that here, close to "
            "camp, than somewhere further away.\n\n"
            "It's in the deepest room of the Den, past the nursery. Go and kill it."),
        turn_in_text=(
            "You did it. That was your first proper fight, and there'll be harder ones.\n\n"
            "Remember how that felt, so you know what to expect next time. Thank you."),
    ),
    "vot_vile_familiars": dict(
        description="Kill 4 Vile Familiars in the Burning Blade Coven, north-east of camp past "
                    "the scorpid nest.",
        accept_text=(
            "I've been on watch in this valley for three seasons and I'd never seen a demon here "
            "until last week. Now there's a cave full of them up at the Burning Blade Coven.\n\n"
            "Somebody opened a way for them, and somebody above me needs to work out who. Until "
            "then we need them kept down. The Coven is the cave at the end of the road north-east "
            "of camp, past the scorpid nest. Go in and kill four of the familiars.\n\n"
            "Don't go any deeper than that on your own."),
        turn_in_text=(
            "The cave's gone quiet for now. Whatever's giving them orders is still in there, "
            "though, so it won't stay quiet for long.\n\n"
            "Thank you. I'll let you know when we've found out more."),
    ),
    "vot_yarrog_baneshadow": dict(
        description="Kill Yarrog Baneshadow at the back of the Burning Blade Coven, north-east of "
                    "camp.",
        accept_text=(
            "We got a name out of one of the familiars before it died. The one giving the orders "
            "in that cave is called Yarrog Baneshadow.\n\n"
            "He's at the very back of the Coven, past the hall with the circle. He calls more "
            "demons to him the longer the fight goes on, so go straight for him and finish it "
            "quickly. If you let it drag on you'll be fighting the whole cave at once.\n\n"
            "I'd go myself, but I can't leave the road."),
        turn_in_text=(
            "Baneshadow's dead, then. I watched from the ridge and you didn't hold back once.\n\n"
            "Whatever you did before you woke up here, you know how to fight. Thank you for "
            "doing this."),
    ),
    "vot_sagewood_petals": dict(
        description="Bring Marta 5 Sagewood Petals from the sprites in the sagewood grove, just "
                    "east of camp.",
        accept_text=(
            "You look like you're still not sure the ground's real. That passes, give it a "
            "week.\n\n"
            "My name's Marta. Half the recruits come back from the nest with scorpid venom in them, and "
            "I need sagewood petals for the remedy. The sprites in the grove just east of camp "
            "drop them when you scare them off. Bring me five, as fresh as you can. They wilt "
            "quickly."),
        turn_in_text=(
            "These are still fresh, so you were careful with them. Most recruits crush half of "
            "what they bring me.\n\n"
            "Thank you. This will keep a few of them on their feet."),
    ),
    "vot_felstalkers": dict(
        description="Kill 6 Felstalker Whelps in the Burning Blade Coven, north-east of camp.",
        accept_text=(
            "The demons brought hounds with them. You'll run into them in the Coven before the "
            "familiars, most likely, running in packs.\n\n"
            "While you're in there, kill six of the whelps. There's no sense making two trips "
            "into a cave like that."),
        turn_in_text=(
            "That's six fewer of them in that cave. If the valley keeps sending people in, we "
            "might clear it before something worse moves in behind them. Thanks."),
    ),
    "vot_graduation": dict(
        description="Follow the road east out of the valley to Razor Hill and find Weapons "
                    "Trainer Grokk.",
        accept_text=(
            "There isn't much left this valley can teach you. You've dealt with the boars, the "
            "scorpids and the demons in the Coven, and doing more of the same won't help you "
            "now.\n\n"
            "Razor Hill is the town in the middle of Durotar, and it's time you saw it. Take the "
            "road east out of the valley and stay on it all the way. Durotar is rougher than "
            "here, and it's easy to get into trouble off the road.\n\n"
            "When you get there, find Weapons Trainer Grokk and tell him I sent you."),
        turn_in_text=(
            "Nakhtar sent you? I could tell you came up from the valley. Everyone who comes up "
            "that road looks the same.\n\n"
            "Down there you learned how to stay alive. Up here you'll learn what to do next. "
            "Welcome to Razor Hill."),
    ),
    "vot_old_tusk": dict(
        description="Kill 3 Mottled Boars and Old Tusk on Sagebrush Flat, west of camp.",
        accept_text=(
            "I'm Grulnok, and I've watched this ridge for six seasons. I know every boar out "
            "there by its tracks, and there's one I don't like. It's as big as a cart, with old "
            "yellow tusks, and it walks straight through the training dummies on Sagebrush "
            "Flat.\n\n"
            "The recruits call it Old Tusk and think it's funny. Sooner or later it's going to "
            "kill one of them.\n\n"
            "Kill three of the boars on the flat, west of camp, and when the big one shows up, "
            "kill him too. He's the one that doesn't run away. Keep the dummies between you, he "
            "can't stand them."),
        turn_in_text=(
            "Old Tusk's dead? That boar's been on this ridge for years.\n\n"
            "Thank you. Take these, you've earned them."),
    ),
    "vot_carrion_circle": dict(
        description="Kill 4 Carrion Vultures and 4 Dustwind Jackals out in the Windrift Dunes, "
                    "east of camp.",
        accept_text=(
            "Don't tell Nakhtar I'm handing out work, he wants me lying still. I'm Torgak, and I "
            "can't walk on this leg yet.\n\n"
            "The vultures have noticed. They've started circling the camp in the afternoons, and "
            "the jackals follow them in closer to the fire every night. They think I'm about to "
            "die.\n\n"
            "They sit out in the Windrift Dunes, east of camp, between visits. Kill four vultures "
            "and four jackals. Do the vultures first, the jackals only get brave when the birds "
            "are about."),
        turn_in_text=(
            "The sky's clear. It feels a lot better when you're stuck lying here like me.\n\n"
            "Nakhtar won't let me give out coin, but he never said anything about gear I can't "
            "wear any more. Take it, and thank you."),
    ),
    "vot_troubled_waters": dict(
        description="Kill 5 Marsh Skimmers and 3 Trailwater Toads at Trailwater Spring, south of "
                    "camp.",
        accept_text=(
            "The spring at the lake south of camp has always given clean water, but I can't get "
            "a clean batch of anything out of it now. There are more skimmers on the water than "
            "I've ever seen, and the toads have gone bold.\n\n"
            "I don't need them all dead, just enough that the water settles. Kill five skimmers "
            "and three toads. Watch the mud at the edge, it's deeper than it looks."),
        turn_in_text=(
            "The water's clear again. I can work with that.\n\n"
            "And you hardly got wet. Thank you."),
    ),
    "vot_gulpjaw": dict(
        description="Kill Old Gulpjaw and 2 Trailwater Toads at Trailwater Spring, south of "
                    "camp.",
        accept_text=(
            "The skimmers weren't the real problem. A toad bigger than a boar has moved into "
            "Trailwater Spring, and the recruits are calling it Old Gulpjaw.\n\n"
            "At first it ate whatever floated in. Now it's going for anything that walks in, and "
            "I need that spring.\n\n"
            "It sits at the bottom of the shallows and waits. Kill two of the toads to draw it "
            "out, and then fight it on the bank. Don't go into the water after it."),
        turn_in_text=(
            "It's gone, and the water's already settling. You've done more for this valley "
            "than most recruits do. Thank you."),
    ),
    "vot_heartwood": dict(
        description="Kill 5 Thornroot Saplings and Bramblethorn the Ancient in the sagewood "
                    "grove, just east of camp.",
        accept_text=(
            "The petals worked, and the recruits are staying on their feet. Now I've got another "
            "problem in the same grove.\n\n"
            "The saplings in there have started walking about, and they're quick and nasty. "
            "Something older is moving with them as well. It's an old tree called Bramblethorn, "
            "and it's been in that grove longer than anyone can remember.\n\n"
            "The grove is just east of camp. Kill five of the saplings, then find Bramblethorn "
            "and stop it. Fire works on them, but it also makes the grove angry, so be quick."),
        turn_in_text=(
            "The grove's quiet again. I can hear the birds in it.\n\n"
            "Thank you. Take something, you've earned it."),
    ),
    "vot_brood_below": dict(
        description="Kill 3 Cave Skitterers, 3 Den Webspinners and 2 Egg Tenders in the Den, "
                    "west of camp.",
        accept_text=(
            "You've seen the front of the Den. Now I want you to go deeper. That cave is a "
            "nursery, and the things guarding it get more dangerous the more of them there "
            "are.\n\n"
            "Kill three skitterers and three webspinners in the halls, then two of the egg "
            "tenders in the nursery. Do it in that order, so that whoever goes after the "
            "guardian later isn't fighting it in a room full of its young."),
        turn_in_text=(
            "That's thinned them out. The guardian is the only thing left in there that "
            "matters, and I'll talk to you about it next. Thank you."),
    ),
    "vot_windrift_omens": dict(
        description="Kill 4 Dust Devils and 3 Sandpincer Crawlers in the Windrift Dunes, east of "
                    "camp.",
        accept_text=(
            "Something's wrong out in the Windrift Dunes. The dust devils have been moving along "
            "the road instead of across it, every day for a week, and sandpincers keep coming up "
            "out of ground with no burrows under it.\n\n"
            "I want it quiet out there before whatever's stirring them up takes an interest in "
            "the camp. The dunes are east of camp. Kill four dust devils and three sandpincers. "
            "If the sand starts to move under you, get off it."),
        turn_in_text=(
            "It's quieter already, I can hear the road again.\n\n"
            "There's one more place in this valley that's wrong, and it's the worst of them. "
            "Come and talk to me when you're ready."),
    ),
    "vot_cinderjaw": dict(
        description="Kill 4 Ember Wisps, 2 Ashback Basilisks and Smolderhide in the Cinderjaw "
                    "Wastes, far south-west past the lake.",
        accept_text=(
            "Far to the south-west, past the lake, the ground is burnt black. We call it the "
            "Cinderjaw Wastes, and nobody goes there. For most of my life that was fine.\n\n"
            "But the burnt ground is spreading toward the lake. I've watched the edge of it for "
            "eleven years and I know where it used to be.\n\n"
            "There are ember wisps out there and basilisks that sleep on the hot stone, and "
            "something the scouts call Smolderhide that walks about at night with fire on its "
            "back. Kill four of the wisps and two of the basilisks, and then Smolderhide. This is "
            "the hardest thing I've asked of any recruit, and if you'd rather not go, I won't "
            "think any less of you."),
        turn_in_text=(
            "So Smolderhide's dead. That was the last of the really dangerous things in this "
            "valley.\n\n"
            "Thank you. I don't have anything harder to give you, so you're ready for Durotar."),
    ),
    "vot_grosks_trophy": dict(
        description="Kill 4 Dustwind Jackals and Sandfang in the Windrift Dunes, east of camp, "
                    "for Grosk.",
        accept_text=(
            "You're the one everyone's been talking about. Listen, I'm not leaving this valley "
            "without a proper trophy, and I've picked the one I want.\n\n"
            "There's an old white jackal out in the Windrift Dunes, east of here, with a scar "
            "over its left eye. They call it Sandfang. It's outrun every hunter in the valley, "
            "including two who were actually good.\n\n"
            "I haven't worked out how to catch it, which is where you come in. Kill four of the "
            "jackals in its pack and then kill Sandfang. My mother doesn't like this idea, but "
            "we're doing it anyway."),
        turn_in_text=(
            "You actually did it! My mother's going to be so angry.\n\n"
            "I'll tell everyone it was both of us. Here, take something for your trouble. "
            "Thanks."),
    ),
    "vot_fel_shards": dict(
        description="Bring Fizzcrank 5 Fel-Tainted Shards from the acolytes, initiates and "
                    "ritual guards in the Burning Blade Coven, north-east of camp.",
        accept_text=(
            "You, the one who isn't on fire, you'll do. I'm Fizzcrank, and the crystals in that "
            "Coven give off a kind of heat that shouldn't be possible, and I want to know why.\n\n"
            "I need shards to study. Small ones, the kind the acolytes carry on their belts. "
            "Don't touch the big ones in the walls, I saw what happened to the last person who "
            "tried.\n\n"
            "The Coven is the cave north-east of camp, past the scorpid nest. Bring me five, and "
            "don't hold them with your bare hands."),
        turn_in_text=(
            "Oh, these are lovely. Oh, that one's smoking. It's fine, I've got a bucket.\n\n"
            "Take whatever you want off the bench. Thank you."),
    ),
    "vot_silk_for_rhaka": dict(
        description="Bring Rhaka 6 Den Silk Spools from the webspinners and skitterers in the "
                    "Den, west of camp.",
        accept_text=(
            "My son went up the ridge last week to prove himself, and he came back. I'd like "
            "him to keep coming back, and a good cloak would help.\n\n"
            "I want proper silk, strong enough to stop a scorpid sting, the kind the webspinners "
            "in the Den make. I've got the loom. I just can't make myself go into that cave, "
            "I've stood at the mouth of it twice.\n\n"
            "The Den is the cave in the ridge west of camp. Bring me six spools. Leave the loose "
            "thread, it's too sticky to use."),
        turn_in_text=(
            "This is good silk, that'll stop a sting. He'll have his cloak before he goes up "
            "again.\n\n"
            "I made a spare while I was waiting. Please take it, and thank you."),
    ),
    "vot_mother_of_nest": dict(
        description="Kill 3 Venomtail Scorpids and Broodmother Sarrix at the scorpid nest, "
                    "north-east of camp.",
        accept_text=(
            "The scorpids you've been killing have a mother, and I'd rather you heard it from me "
            "than found out at the nest.\n\n"
            "Broodmother Sarrix has held that nest for longer than we've been in this valley. "
            "As long as she's alive, the workers will keep coming however many you kill.\n\n"
            "The nest is north-east of camp. Kill three of the venomtails that guard her first, "
            "then go for her. It's a long fight, so make sure you're at full health before you "
            "start it."),
        turn_in_text=(
            "Sarrix is dead. The nest will be unsettled for a season and then calm down.\n\n"
            "This valley's needed that done for a long time. Thank you."),
    ),
    "vot_ritual_disruption": dict(
        description="Kill 4 Burning Blade Initiates and 2 Coven Ritual Guards in the Burning "
                    "Blade Coven, north-east of camp.",
        accept_text=(
            "I sent you after the familiars, but they weren't the real problem. Deeper in the "
            "Coven they're drawing a summoning circle, and if they finish it we'll have "
            "something much worse than Baneshadow to deal with.\n\n"
            "The initiates hold the outer halls, and the ritual guards stand in the hall with "
            "the circle. Kill four initiates and two guards. Go for the guards first if you can, "
            "they're the ones finishing the circle."),
        turn_in_text=(
            "The circle's broken. I hadn't noticed the smell until it was gone.\n\n"
            "Thank you. Baneshadow is the only one left in there, so take this and go and "
            "finish it."),
    ),
}

GREETINGS = {
    "valley_of_trials": {
        "vot_greeter": (
            "My name's Nakhtar. This is the Valley of Trials, where the Horde trains its recruits, and "
            "lately it's where people like you wake up as well. I'll tell you when you're ready "
            "for Durotar. Until then, I've got work for you."),
        "vot_guard_1": (
            "I keep the camp road. The boars are west of here and the scorpids are north-east, "
            "and past the scorpids there's a cave full of demons that I've not got the soldiers "
            "to clear. If you want something to fight, I can tell you where."),
        "vot_elder": (
            "I've been teaching recruits in this valley longer than Nakhtar's been talking to "
            "them. He'll tell you about the Horde. I'll send you into the Den and out to the "
            "dunes, and you'll learn more that way."),
        "vot_recruit_watcher": (
            "I've been watching the tracks on this ridge for six seasons. The boars stay on "
            "Sagebrush Flat, west of camp, except for one big one that keeps walking through "
            "the training dummies."),
        "vot_goblin_tinkerer": (
            "I'm Fizzcrank, and I'm doing research here until the camp asks me to leave. Please "
            "don't touch the bench, it isn't finished and part of it might be on fire."),
        "vot_orc_mother": (
            "My son's one of the recruits. He went up the ridge last week and came back, and I'd "
            "like it to stay that way. I'm a weaver. If you're going into the Den, come and talk "
            "to me first."),
        "vot_wounded_grunt": (
            "A scorpid opened up my leg at the nest before I killed it. Nakhtar says I'll walk "
            "again. Until then I'm stuck sitting here, and the vultures have started taking an "
            "interest."),
        "vot_young_orc": (
            "I've killed more boars on this ridge than anyone my age, and I'm not leaving the "
            "valley until I've got something better than a boar to show for it."),
        "ct_vot": (
            "I train every kind of fighter, blade, bow or spell. Come and see me when you've "
            "gained a level and bring some coin, the lessons aren't free."),
        "pt_vot_forge": (
            "I teach mining, where to dig and how to tell ore from plain rock. The camp forge is "
            "just north of me by the Farseer's tent, for smelting what you bring back. If you "
            "want to learn smithing, that's taught in Razor Hill."),
        "pt_vot_herbs": (
            "I teach herbalism, which plants to pick and which to leave alone. If you want to "
            "brew them into anything, that's alchemy, and Apothecary Kagra teaches it in Razor "
            "Hill."),
        "pt_vot_wood": (
            "I teach woodcutting. The camp sawmill is north-west of here, past Marta's fire, for "
            "turning logs into planks. If you want to build things with them, Woodwright Hulda "
            "teaches that in Razor Hill."),
    },
}

VENDOR_GREETINGS = {
    "kalimdor_and_lordaeron": {
        "valley_vendor": (
            "I keep the supply stall for the valley. I've got potions, food and drink, and a few "
            "things for whatever trade you take up. Stock up before you take the road east to "
            "Durotar, there's nothing to buy until Razor Hill."),
    },
}
