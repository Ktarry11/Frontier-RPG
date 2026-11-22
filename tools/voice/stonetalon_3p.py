"""Stonetalon and Sun Rock in the giver's own voice (21 Nov 2026): the quests whose offer was narrated about the giver.

Kyle, 21 Nov 2026: no quests handed out in third person, and a story of five or six sentences. Merged into
tools/voice/stonetalon.py's VOICE: each entry here replaces that quest's description (and its accept line where one is
given, kept under 200 characters so the description stays the offer's body).
"""

THIRD = {
    "st_road_west": (
        "I've got a dispatch for Orgrimmar's envoy at Sun Rock Retreat, up in Stonetalon. I don't trust the "
        "Grimtotem with it, I don't trust the harpies with it, and frankly I don't trust you much either. But you're "
        "the one standing in front of me, so you'll do. The road runs west out of the Dry Hills and climbs into the "
        "mountains, and Sun Rock's the hold on the mesa. Put this in Envoy Garnak's hand and nobody else's.",
        "Take the road west out of the Dry Hills and keep climbing. Sun Rock's the hold on the mesa.",
    ),
    "st_talondeep": (
        "I need a pair of eyes in Stonetalon. Orgrimmar's envoy at Sun Rock Retreat writes to me every week, and every "
        "week his letters get shorter. Either he's busy, or something's wrong, and I'd like to know which. The "
        "Talondeep Path runs south out of Ashenvale, through the hill and down onto a mountainside that used to be "
        "forest. Take him this letter and find out what's going on.",
        "South down the Talondeep road, through the tunnel. Sun Rock's the big mesa in the middle of the burn.",
    ),
    "st_hides_for_the_lodge": (
        "I've got more people on Sun Rock than I've got roofs. The refugees who got out when Thunder Bluff fell are "
        "sleeping under the sky, and the wind off the Blowdown has started to bite at night. The old ones are "
        "beginning to cough. Elk hide makes a good tent, and the grey elk graze all over the burn below us. The bull "
        "elk keep to the Standing Grove in the south-west. Bring me their hides and I'll see them stitched before the "
        "cold sets in.",
        "The grey elk graze the Blowdown below us, and the bull elk keep to the Standing Grove. Bring me the hides.",
    ),
    "st_word_to_taurajo": (
        "Elder Longtread at Camp Taurajo speaks for the tauren now, while nobody knows where Cairne is. I've written to "
        "him about the Rim, about the refugees here, and about the dead that won't lie down on the Mulgore side. These "
        "are things I won't trust to a messenger who hasn't seen them. Camp Taurajo's in the southern Barrens, and the "
        "wind riders will take you most of the way. Put this in his hand, and tell me what he says.",
        "Camp Taurajo's in the southern Barrens. Don't let anyone else read it, and don't read it yourself.",
    ),
    "st_taurajo_answer": (
        "I've read Muhana's letter twice, and I've written back. I'd like you to carry it, because I'd rather it went "
        "with someone who's seen Sun Rock with their own eyes. There's something I haven't written down, and I want "
        "you to tell her in person. Taurajo can't send her warriors. We have the Barrens to hold, and I'm sorry for "
        "it.",
        "Take it to Muhana. Tell her I'd come myself if the camp could spare me, and tell her it can't.",
    ),
    "st_ash_that_walks": (
        "The forest on the Blowdown came through with the mountain three years ago, and it didn't burn. It was "
        "knocked flat in a single breath and buried in ash, and its spirits never had time to leave. Now the Ash "
        "Drifters walk the burn, and I believe they're what's left of the trees, trying to remember what they were. "
        "They walk the open burn north and west of here. I'd like them put to rest, gently if you can.",
        "The ash drifters walk the open burn north and west of here. Be gentle if you can, and quick if you can't.",
    ),
    "st_old_greyhide": (
        "There's an elk on the Blowdown that should have died when the mountain blew. Old Greyhide was standing in the "
        "blast and walked out of it, and he hasn't been right since. He leads the grey elk round and round the place "
        "where the forest used to be, and the herd follows him. They won't scatter while he lives, and they need to "
        "scatter to find new grazing. You'll find him in the middle of the Blowdown, grey all over, with the herd "
        "round him.",
        "He's huge and grey, ash in his coat to the skin. Look for him in the middle of the Blowdown.",
    ),
    "st_rot_in_the_heartwood": (
        "The Eldest Sequoia is the greatest tree on Stonetalon, and it's dying from the inside. The Venture Co. bored "
        "into it to tap its sap, and the heartrot beetles followed them in. Their queen is eating the tree's heart, "
        "and I can feel it every time I put my hand on the bark. The Eldest stands on the slopes of Stonetalon West, "
        "and you go in at its foot and climb. Kill the Heartrot Queen before there's nothing left to save.",
        "Go in at the Eldest Sequoia's foot in Stonetalon West. The queen nests in the chewed galleries. Bring friends along.",
    ),
    "st_rest_for_the_eldest": (
        "The heart is clean now, but the Eldest's spirit isn't at peace. I've been listening at the foot of the tree "
        "for three nights, and what I hear from the crown is rage. It's been bored and tapped and climbed on for so "
        "long that it lashes out at anything that moves. The tree will go on standing whatever happens. The spirit "
        "just needs to sleep, so climb to the crown and give it rest.",
        "Climb the trunk and out onto the crown. The Eldest waits at the very top. Bring your best people.",
    ),
    "st_harpies_on_the_crag": (
        "The Windshear harpies have nested on the crag north of the Blowdown for as long as anyone remembers. Since "
        "the mountain blew, they've been coming down on Sun Rock's supply lines and taking whatever they can carry. "
        "I've lost two carts this month, and a driver who didn't let go fast enough. Windshear Crag is the high ground "
        "north-east of here, past the Blowdown. Push the harpies and their talons back up the crag where they "
        "belong.",
        "Windshear Crag's north-east, past the Blowdown. Kill the talons first if you can.",
    ),
    "st_wind_witch_fetishes": (
        "The wind witches are what keep the harpies coming. I've watched them through my glass, and before every raid "
        "they hold up little bundles of feather and bone, and the wind turns their way. I want those fetishes, so "
        "Spiritwalker Tohana can find out what they do and how to stop them. The witches stay near the top of "
        "Windshear Crag, north of here. Don't hold one up into the wind yourself, whatever you do.",
        "The Windshear wind witches stay near the top of Windshear Crag, north of here. Bring me what they carry.",
    ),
    "st_matron_shrieka": (
        "Matron Shrieka is the oldest of the Windshear wind witches. She makes every fetish on the crag, and she sends "
        "every raid down onto our road. Driving her off won't do it, because she'll only come back and start again. I "
        "want her gone for good. She keeps the highest nest on Windshear Crag, and you'll hear her long before you see "
        "her.",
        "She keeps the highest nest on Windshear Crag. Take friends, and plug your ears if you can.",
    ),
    "st_the_grimtotem_line": (
        "The Grimtotem have built a compound south of the Blowdown, and it creeps closer to Sun Rock every month. "
        "They're testing us, sending raider bands and spearhunter packs out to see how far they get before the watch "
        "notices. I want them to learn that the watch always notices. Their compound is to the south, past the "
        "Standing Grove, and their patrols work the ground round it. Hit them there, before they reach the road.",
        "The compound's south, past the Standing Grove. Hit the raiders and spearhunters before they reach the road.",
    ),
    "st_carrion_from_the_rim": (
        "I watch the Mulgore Rim from the south-east tower, every night. The carrion birds that roost on the Rim fly "
        "into Mulgore after dark and come back in the morning. What they carry in their beaks shouldn't be carried "
        "anywhere, and they've started dropping it near the camp. The Rim is in the south-east corner of Stonetalon, "
        "where the light goes strange. Kill them before they bring any more of Mulgore to Sun Rock.",
        "The Mulgore Rim's in the south-east corner, where the light goes strange. Don't stand under the birds.",
    ),
    "st_what_walks_the_rim": (
        "Every night more of them stand on the Rim and look toward Sun Rock. They were tauren once, and some of them "
        "were people I knew. Something in Mulgore killed them and then got them back up again, and now they hunt "
        "along the edge of the dark. I want the risen cut down, and I want the Rim looked at properly, from the "
        "overlook at the far end. Look, then come back and tell me what you saw, and don't stay too long.",
        "The risen walk the Mulgore Rim. The overlook is at the far end, where the ground drops into the dark.",
    ),
    "st_the_risen_hunter": (
        "There's one of the risen who leads the rest, and I knew him. He was a Bloodhoof hunter, the best tracker in "
        "Mulgore, and now he tracks for whatever's down there. I wouldn't send anyone after him until I knew Sun Rock "
        "wasn't standing alone. Camp Taurajo, Splintertree and the Aspen have all answered now, so it's time. He hunts "
        "the Mulgore Rim with the risen behind him, and he'll know you're coming.",
        "He hunts the Mulgore Rim with the risen behind him. Go together, and don't follow him past the Rim.",
    ),
    "st_kingsblood_for_the_sick": (
        "Half the children on Sun Rock have a cough from the ash, and it's getting worse as the nights get colder. I "
        "know an old Mulgore remedy that uses kingsblood, and kingsblood grows on Stonetalon if you know where to look. "
        "I can't leave the camp, because the sick need me here. It grows on the slopes all over Stonetalon, and you'll "
        "need a little herbalism to pick it. Bring me what you find.",
        "Kingsblood grows on the slopes all over Stonetalon. If you can't pick herbs, Nawa will teach you.",
    ),
    "st_aspen_answer": (
        "Hoka wrote three pages to his sister, and then he asked me to add a fourth. It says the Aspen has room for "
        "anyone from Sun Rock who wants to come south. It also says the Aspen's hunters will stand with Sun Rock if the "
        "Rim ever breaks, and I meant every word of that. I'd like it carried back by the same hands that brought the "
        "first letter.",
        "Take it back to Halona at Sun Rock, and tell her the Aspen meant what it wrote.",
    ),
    "st_meat_for_the_rock": (
        "I hunted Mulgore my whole life, and now I hunt for a mesa full of people who lost everything. There aren't "
        "enough hunters, and there are a great many mouths. The bull elk in the Standing Grove are fat, and the grove "
        "is thick enough to sneak up on them. It's in the south-west, among the trees the blast missed. Bring me "
        "venison, as much as you can carry.",
        "The Standing Grove's in the south-west. The bull elk graze between the trees. Come in from downwind.",
    ),
    "st_broadpaw": (
        "Broadpaw is the black bear the Standing Grove belongs to. He's never bothered the hunters before, but the "
        "cougars have pushed him out of his den, and now he takes his temper out on anybody in the trees. I'm sorry "
        "for the bear, truly. But he's hurt two of my hunters, and he has to go. You'll find him deep in the grove, "
        "bigger than any bear you've seen.",
        "He's deep in the Standing Grove, and he'll charge. Don't be standing where you were when he does.",
    ),
    "st_grimtotem_intent": (
        "Orgrimmar wants to know whether the Grimtotem mean to take Sun Rock or only to frighten it, and I can't tell "
        "them from up here. Their compound is south of the Blowdown. Get close enough to see what they're building "
        "inside the walls. If their brutes come at you, make an example of them, so they know they've been seen. Then "
        "come back and tell me everything.",
        "The compound's south of the Blowdown. Get close enough to see inside, and make an example of the brutes.",
    ),
    "st_word_to_splintertree": (
        "I've written to Overseer Gorada at Splintertree Post about the ladders, the fire and Hargol. I won't trust it "
        "to a wind rider, because the harpies have been knocking them out of the sky. It has to go on foot, up the "
        "Talondeep Path to Ashenvale. Splintertree's the Horde post on the other side of the tunnel, and Gorada will be "
        "on the wall, because she always is.",
        "North up the Talondeep Path and through the tunnel. Gorada will be on Splintertree's wall.",
    ),
    "st_splintertree_answer": (
        "I've written back to Garnak. Splintertree can't spare warriors, not with the demons loose in Ashenvale, but I "
        "can spare arrows and a promise, and I've sent both. I want the answer carried back the way his report came, "
        "on foot. Tell him the arrows follow on the next cart. Tell him I meant the promise, and he'll know what I "
        "mean.",
        "Back down the Talondeep to Sun Rock. Tell Garnak the arrows follow on the next cart.",
    ),
    "st_blasting_caps": (
        "The Venture Co. blasters are clearing the Blowdown with powder, and they're not careful about it. One of their "
        "charges shook the whole mesa last week and took a corner off the inn. I want their blasting caps, and I want "
        "their yard foremen dealt with, because without both of them nothing goes bang. They work the Venture Salvage "
        "Yard, north-west of here. Carry the caps very carefully, and I'm being serious.",
        "The blasters and their foremen work the Venture Salvage Yard, north-west of here. Carry the caps carefully.",
    ),
    "st_yard_boss_krizzle": (
        "Yard Boss Krizzle runs that salvage yard, and I've found out he used to be Cartel. He walked out with a "
        "warehouse key and a crate of our caps the day the Venture Co. offered him more money. Nobody steals from the "
        "Cartel and gets to keep the profit. He's in the middle of the Venture Salvage Yard, north-west of here, "
        "shouting at people. Deal with him, and make sure he knows it came from me.",
        "He's in the middle of the Venture Salvage Yard, north-west of here. Tell him Pixie says hello.",
    ),
    "st_samples_from_the_rim": (
        "I know the tauren don't want me on Sun Rock, and I don't blame them. But whatever is getting the dead up in "
        "Mulgore isn't the Scourge, and it isn't anything the Forsaken have ever seen. I want to know what's doing it before "
        "it reaches anywhere else. I need tissue samples from the risen tauren and the risen stalkers on the Rim, in "
        "the south-east. The jars seal themselves, mostly, but I wouldn't count on it.",
        "The risen walk the Mulgore Rim in the south-east. Take the samples from the ones you put down.",
    ),
    "st_what_raised_them": (
        "I want to see what the risen see. There's a cairn at the edge of the Mulgore Rim, south of here, right where the dark begins, and I "
        "believe the thing that raises them reaches up out of Mulgore there. I'd like you to stand at that cairn and "
        "tell me what you feel. Thin out the risen guarding it first, or you won't be standing long. Stay as long as "
        "you can bear it, and then come back and tell me everything.",
        "The cairn's on the Mulgore Rim, where the daylight gives up. Stand there as long as you can bear it.",
    ),
    "st_ground_zero": (
        "I studied volcanoes in Washington State before the Integration, and I'm almost sure the mountain above Sun "
        "Rock is something like Mount St. Helens. The Blowdown looks exactly like what happened there in 1980, right "
        "down to the way the trees are lying. I need to see the middle of the blast and the edge of the salvage yard, "
        "but I'm not much use with a weapon. Go and stand where the blast was strongest, out in the middle of the "
        "Blowdown, and then look over the yard. Tell me which way the trees are lying.",
        "Stand in the middle of the Blowdown, then look over the salvage yard. Tell me which way the trees lie.",
    ),
    "st_cores_of_ash": (
        "The ash drifters on the Blowdown are made of the same ash the mountain threw, and they pack it down tight in "
        "their middles like a core sample. If I can read their layers, I can tell how long the mountain rested "
        "between eruptions. That tells me how long we've got before the next one. They walk all over the Blowdown, so "
        "break them open and bring me what's in the middle. It'll be warm, which is good, because it means it's "
        "fresh.",
        "The ash drifters walk all over the Blowdown. Break them open and bring me what's in the middle.",
    ),
    "st_vents_on_the_peak": (
        "The peak of Stonetalon is in the West, past the redwoods, and I'm convinced the vents up there are opening. "
        "Every Vent Steamling on that peak is really a vent walking around, a crack in the mountain letting off "
        "pressure. I want them put out, and I want someone to look into the crater from the rim. Take the road through "
        "Stonetalon West and up to the top. Tell me if the crater lake is steaming.",
        "Take the road through Stonetalon West to the peak. Put out the steamlings and look into the crater.",
    ),
    "st_into_the_ashvent": (
        "The Ashvent is a lava tube on the flank of the peak, and the heat at the bottom of it shouldn't be there. "
        "Something called Magmacore sits on the last of the molten rock and keeps it from cooling. As long as it does, "
        "the whole mountain stays warm, and the next eruption gets closer. I can't go down there myself, but you can. "
        "The tube opens on the peak's north flank, and Magmacore sits at the very bottom.",
        "The Ashvent opens on the north flank of the peak. Follow the tube down to Magmacore. Bring heat-proof friends.",
    ),
    "st_iron_under_the_burn": (
        "There's good iron on Stonetalon now that the trees aren't sitting on top of it. Sun Rock needs spearheads, "
        "hinges and nails, and I can't make any of them without ore. The refugees are building homes with rope and "
        "hope, and that won't last a winter. Iron turns up all over the Blowdown and the slopes in the West. Bring me "
        "what you can dig, and I'll teach you mining if you don't know it.",
        "Iron turns up all over the Blowdown and the slopes in the West. I'll teach you mining if you need it.",
    ),
    "st_fallen_not_felled": (
        "I won't touch a living giant, and nobody on Sun Rock will. But the Blowdown is full of trees that came "
        "through already down, and redbark from a fallen tree is every bit as good as redbark from a standing one. I "
        "need logs for the new lodge. Cut them where they lie, all over Stonetalon. You'll need woodcutting, and I'll "
        "teach you if you haven't got it.",
        "There's redbark down all over Stonetalon. Cut it where it lies.",
    ),
    "st_planks_for_the_lodge": (
        "I've got the logs, and now I need planks. I'd like you to mill them yourself at my bench, because once you've "
        "cut the boards for a lodge, you'll never look at one the same way again. It's slow work, and it teaches you "
        "patience. Straight, even planks are all I ask. Mind your thumbs.",
        "Mill them at my bench or any woodworker's bench. Straight, even planks, and mind your thumbs.",
    ),
    "st_fireweed_and_amber": (
        "I've heard that the Eldest Sequoia's sap runs as living amber inside the trunk, and that it heals burns "
        "better than anything that grows outside. The Venture Co. has been tapping it to sell, and the living sap that "
        "pools in the galleries carries the amber. I want some before they sell all of it. The children here burn "
        "themselves on the cooking fires every week. Go in at the tree's foot, and take friends, because it's "
        "dangerous in there.",
        "Go into the Eldest Sequoia from the door at its foot. The living sap moves through the lower galleries.",
    ),
    "st_beetles_in_the_bark": (
        "I walk the fog under the redwoods that came through with the mountain, and the bark beetles have never been "
        "this bad. They bore into the giants and lay their eggs, and a tree that big dies so slowly that nobody "
        "notices until it's too late. I want them cut back before they reach the oldest trees. They're thickest in "
        "Greatwood Vale, below the camp. Stand still and you'll hear them chewing.",
        "The bark beetles are thickest in Greatwood Vale, below the camp.",
    ),
    "st_the_ancients_wake": (
        "Some of the giants were awake when they came through. I call them the Redwood Ancients, and since the "
        "Venture Co. started cutting, they've been waking in a rage and walking the vale, flattening anything they "
        "find. I've tried to calm them, and they won't listen to me any more. I need them put back to sleep the only "
        "way that works now. They walk in Greatwood Vale and on the Sequoia Slopes.",
        "The ancients walk Greatwood Vale and the Sequoia Slopes. Don't stand still in front of one.",
    ),
    "st_gnawheart": (
        "The bark beetles have a mother, and I've found where she's been laying. She's inside a giant in Greatwood Vale "
        "that's hollow now from root to crown. I call her Gnawheart, because that's what she does. The beetles won't "
        "stop coming while she lives. She's bigger than a kodo, so bring friends.",
        "Gnawheart lives in a hollow giant deep in Greatwood Vale. Don't let her get behind you.",
    ),
    "st_a_climbers_look": (
        "I climbed redwoods for a living back in Humboldt County, in California. The tallest tree on Earth was a "
        "redwood called Hyperion, and the great sequoia on the slopes here would make Hyperion look like a sapling. "
        "I'm not climbing anything that big until I know how it's standing. Go and look at the base for cracks, and "
        "then cross the slopes and look at which way it would fall. It's on the Sequoia Slopes, north of the vale.",
        "The great sequoia's on the Sequoia Slopes, north of the vale. Check the base, then the fall line.",
    ),
    "st_sap_on_the_slopes": (
        "The sap oozes are what happens when a sequoia bleeds. The Venture Co. taps the giants, the sap runs out, and "
        "then it gets up and walks away. It sticks to everything, and it sticks to my climbing rope worst of all. I "
        "can't climb with a rope full of sap. Clear them off the Sequoia Slopes so I can get up there.",
        "The sap oozes crawl all over the Sequoia Slopes. Watch your feet.",
    ),
    "st_skyreach": (
        "I got halfway up a sequoia before a sky serpent the size of a canoe came round the trunk at me. The ridge "
        "eagles used to nest up on the peak, and the biggest of the serpents, Skyreach, has been driving them off and "
        "taking their nests. I'd like to climb without being eaten. I'd also like the eagles to have their peak back. "
        "Skyreach hunts round Stonetalon Peak, and it'll come to you.",
        "Skyreach hunts round Stonetalon Peak. Clear a few feral eagles on the way, and it'll come to you.",
    ),
    "st_the_cutline": (
        "I ran a Venture Co. saw crew for years, and I quit the day they started cutting the living giants. Now I work "
        "for the Cartel, undoing what I used to do. The Venture Cutline is eating into the redwoods from the east, and "
        "I know every crew on it by name. The fellers cut, and the riggers haul. I want both of them stopped.",
        "The Venture Cutline's east of the camp, where the trees stop and the stumps start.",
    ),
    "st_shredder_gears": (
        "The Venture Co.'s shredder walkers do the work of ten crews each. I helped build the first ones, and I know "
        "they can't run without their drive gears, so pull the gears and the shredders are scrap. Before the "
        "Integration there were no trees this big to cut, and nobody would ever have built a machine this stupid to "
        "cut them. The shredders work the Venture Cutline. Bring me their gears, and don't climb into one while it's "
        "running.",
        "The shredders work the Venture Cutline. Bring me their drive gears.",
    ),
    "st_saw_boss_brakka": (
        "Saw-Boss Brakka runs the Venture Cutline. She was my foreman, and she's the one who decided the living giants "
        "were fair game. She won't stop while she's alive, I know her too well for that. I want her stopped, and every "
        "one of her foremen with her. She carries a saw on a pole that'll take your arm off, so go together.",
        "Brakka's at the head of the Venture Cutline with her foremen. Go in together.",
    ),
    "st_the_ash_mother": (
        "The ash wraiths come from somewhere, and I've found where. There's a hollow off the skylight in the Ashvent, "
        "where ash falls in through the roof and something gathers it into the shape of a woman. The ash mother makes "
        "the wraiths, and she's making more every week. I want her ash, all of it, preferably. The Ashvent opens on "
        "the peak's north flank, and she's in the hollow off the skylight.",
        "Go down the Ashvent to the skylight and find the hollow off it. Take friends who can stand the heat.",
    ),
    "st_for_the_society": (
        "I need a second opinion, and the only Forsaken apothecary I trust on this side of the world is Dellwyn Voss, "
        "at Hammerfall in the Arathi Highlands. Voss has written four reports about something in the mere water there "
        "that won't die properly. I think it might be the same thing as the Rim. I've packed the samples in ice, and I "
        "need them carried across the sea. Don't open the box, and I do mean that.",
        "Hammerfall's in the Arathi Highlands, in the Eastern Kingdoms. Don't open the box.",
    ),
    "st_voss_replies": (
        "I've had Merrow's samples for a day and a night. What lives in the Arathi mere isn't the same thing as what's "
        "on his Rim, but it was made the same way, by something that doesn't need plague to hold the dead together. "
        "I've written it all down for him. My hand is small, so he'll need his spectacles. Take it back to Sun Rock for "
        "me.",
        "Take this back to Merrow at Sun Rock. Tell him he was right, and that I hate that he's right.",
    ),
    "st_cartel_paperwork": (
        "Somebody signed those blasting caps out of a Cartel warehouse, and I want to know who. The Cartel's warehouse "
        "ledgers for this side of the world are kept by Factor Weezel in Booty Bay, because Booty Bay never throws "
        "anything away. I've written down every stamp number off the caps. Booty Bay is at the bottom of Stranglethorn, "
        "in the Eastern Kingdoms. Weezel will tell you he's busy, so wait for him anyway.",
        "Booty Bay's at the bottom of Stranglethorn. Weezel keeps the ledgers. Wait for him, however busy he says he is.",
    ),
    "st_weezels_findings": (
        "I found the signature in the ledgers. The caps were signed out by a Krizzle, a Cartel man in Ratchet, on the "
        "very day he resigned. He took a key, a crate and the Cartel's good name with him, and the Cartel would like at "
        "least one of the three back. I've written it all up for Pixie, with the seal that means she can do whatever "
        "she likes about it.",
        "Take these to Pixie Brightcog. The seal means she has the Cartel's leave.",
    ),
    "st_ash_for_brill": (
        "I've got ash from the wraiths and ash from the thing that made them, and I want both of them in the hands of "
        "the apothecaries at Brill. They'll know what to do with it. It's better if you don't know. I've sealed it in "
        "lead, because I'm not a monster. Brill's in Tirisfal Glades, near the Undercity, and Assistant Grael will take "
        "it from you.",
        "Brill's in Tirisfal Glades, by the Undercity. Give it to Assistant Grael. Don't drop it, and don't shake it.",
    ),
    "st_grael_writes_back": (
        "I've written back to Rennick. The ash is exactly what Brill wanted, and we'd like more. There's also a warning "
        "on the second page. The Royal Apothecary Society has heard about his work, and they'd like a word with him. I "
        "didn't say which word.",
        "Take this back to Rennick. He'll be pleased, until he reads the second page.",
    ),
    "st_cougar_stew": (
        "I feed everybody on Sun Rock, and the elk are running thin this season. Cougar makes a good stew if you cook "
        "it long enough, and the ridge cougars have been eating very well on the Blowdown. I'd rather they fed us than "
        "we fed them. They hunt all over the Blowdown and in the Standing Grove. Bring me their flanks, and I'll do the "
        "cooking.",
        "The ridge cougars hunt the Blowdown and the Standing Grove. Bring me the flanks.",
    ),
    "st_hides_for_the_cold": (
        "Winter on a mesa is cold, and a bear hide is the warmest thing a tauren can sleep under. The refugees came "
        "here with nothing, and some of them are sleeping on bare stone. Black bear from the Standing Grove or "
        "greatwood bear from the redwoods in the West, it doesn't matter which. Bring me the hides, and I'll tan them "
        "for the refugees' beds.",
        "Black bears in the Standing Grove, greatwood bears in the West. Bring me the hides.",
    ),
}
