"""
Tempest Isle quest text, second draft (14 Nov 2026). Read by tools/build_tempest_quests.py, which
lays these over the first draft by quest id.

WHY A SECOND DRAFT. Kyle, the same evening, on writing elsewhere: "This is also all weirdly AI
again. NO ONE talks like this." The first draft had no fragments left, but it still had the other
habits: a joke built out of three things ("flour, salt and a letter of apology"), a closing line
written to land ("He says that every time, and then he signs"), and turn-ins where the giver sums
up what it all meant to them ("You've given me my trade back").

THE RULES FOR THIS DRAFT:
  - say what's wrong, where to go, what to bring back; a reason if a person would give one
  - a turn-in thanks you, says one thing that happens next, and stops
  - no little jokes, no sayings, no line that sums a person up, no moment of feeling explained
  - people from Earth mention it the way you'd mention where you used to work
"""

TEXT = {
    # ================================================================ TEMPEST SHALLOWS
    "tmp_off_the_boat": (
        "Can you take this up to Quartermaster Durn for me? I can't leave the jetty while "
        "there's a boat tied up.\n\nIt's the manifest for the boat you came in on. Durn won't "
        "open the stores until he's checked it against what was landed.\n\nHe's under the big "
        "awning with the barrels, just along the shore to the south-east. Tell him the count's "
        "right.",
        "Thanks. I'll check it myself, but it's good to have it.\n\nIf you're looking for work, "
        "ask around the landing. Most people here have more to do than hands to do it."),
    "tmp_teeth_on_the_trunk_road": (
        "Nobody could land on this island until the sea route opened three years ago. "
        "Now everything we land goes east along the trunk road through the Green Belt, and the "
        "road isn't safe.\n\nThe Greenbelt Raptors hunt it in packs. The Canopy Panthers "
        "wait in the trees above it and drop on whoever's at the back. I've lost porters to "
        "both.\n\nThe Green Belt is the jungle east of the landing. Follow the road in and kill "
        "what you find on it.",
        "The porters made it through this afternoon without seeing a raptor.\n\nThat'll let me "
        "send carts out again. Take this from the jetty stores."),
    "tmp_the_road_to_the_wharf": (
        "I need my tally taken to Harbourmaster Skezz in Cinderwharf, and you've shown you can "
        "look after yourself.\n\nShe runs the berths over there. Four barges left this jetty "
        "since spring and never reached her, and she wants my list of which ones.\n\nTake the "
        "trunk road east through the Green Belt, then the east road north round the mountain "
        "into the Ashen Reach. Keep north along the shore until you reach the town gate. The "
        "country past the mountain is harder than this, so be ready for it.",
        "That's Grekka's tally. Thank you for bringing it all this way.\n\nThe same four barges "
        "are missing from my book. I'd like to find out what happened to them, and I could use "
        "your help."),
    "tmp_crab_for_the_pot": (
        "I've got forty people to feed and the supply boat brought me flour and salt.\n\nThere's "
        "plenty of food out in the shallows. The Bargebreaker Crabs are as big as a handcart "
        "and a claw will feed a table, but they fight.\n\nGo east along the trunk road and take "
        "the strand road down to the water. Bring me the claws and I'll get them cooking.",
        "These are good claws. That's two nights of supper.\n\nSit down and have some once it's "
        "cooked. You can take this as well, somebody left it in the tent."),
    "tmp_carried_up_by_hand": (
        "Somebody's been stealing crates off the ruin road at night, and I know who.\n\nThere are "
        "dwarves camped in the forecourt of Khaz Varun's Gate, south-east of here at the end of "
        "the road. They went into the city and came out wrong, and now they won't leave. The "
        "big ones, the Gate-Squatter Brawlers, come up the road after dark and take whatever my "
        "porters put down.\n\nGet my crates back. You'll have to deal with the Brawlers to do "
        "it.",
        "These all have my tally numbers on them. Some of them haven't even been opened.\n\nI "
        "don't understand what they wanted them for. Thank you for getting them back. Here's "
        "something from the stores."),
    "tmp_mother_canopy": (
        "I've lost three porters this month on the trunk road, and it was the last one in the "
        "line every time.\n\nThe woodcutters say it's a panther twice the size of the others. "
        "They call her Mother Canopy. She hunts the stretch of road under the thickest trees in "
        "the Green Belt, east of the landing.\n\nShe doesn't show herself to just anyone, but "
        "she'll come for someone who goes looking. Please kill her.",
        "That's her hide. I'm glad to see it.\n\nI'll hang it over the stores so the porters can "
        "see she's gone. Choose something from what I've set aside for this."),
    "tmp_what_its_worth": (
        "I'm supposed to put a value on this whole island for the underwriters. Nobody could "
        "reach it before the change, so nobody's done it before.\n\nThere are three places I "
        "haven't been able to stand in. The first is the heart of the Green Belt, east of here "
        "along the trunk road. The second is further east, where the strand road meets the "
        "water. The third is the pass on the Scoured Slope, north-west of the landing up the "
        "west road.\n\nGo to each one, have a good look, and come back and tell me what's "
        "there.",
        "Good timber in the Belt, wrecks at the strand, and ash and scorpions on the slope.\n\n"
        "That's what I needed. I'll write it up and send it to my cousin Nix in Cinderwharf."),
    "tmp_preachers_in_the_forecourt": (
        "I can't survey the forecourt of Khaz Varun's Gate because the squatters keep setting "
        "fire to my equipment.\n\nThe ones doing it are the Gate-Squatter Ashpreachers. They stand "
        "in the rubble shouting at the arch, and they throw fire at strangers. They also carry "
        "slates with writing on them. If it's a claim on the city, the underwriters need to "
        "know.\n\nThe forecourt is south-east of here at the end of the ruin road. Deal with the "
        "Ashpreachers and bring me some of their slates.",
        "They all say the same thing, over and over: \"the forge is lit and we were not "
        "called.\"\n\nIt isn't a claim. I don't know what it means. I'll send these to the "
        "Deedkeeper in Cinderwharf, she reads the old script better than I do."),
    "tmp_bitterbark": (
        "I've run out of painkillers, and the boat won't bring more for a month.\n\nBefore I came "
        "through I had a whole cabinet of them. Here I've got bandages and clean water. The "
        "woodcutters tell me the Ashfur Gorillas in the Green Belt chew a grey bark and put it on "
        "their burns, and the burned ones are climbing again in a day.\n\nThe Green Belt is east "
        "of the landing along the trunk road. The gorillas carry the chewed bark with them. I'd "
        "like to try it.",
        "This is strong. Even a little of it numbs your mouth.\n\nI think I can make a proper "
        "painkiller out of it. Thank you, that's going to help a lot of people here."),
    "tmp_snapper_fat": (
        "Most of what I treat here is burns. Before I came through I'd have ordered "
        "dressings from the hospital stores, but here I've got to make them, and I need a "
        "clean fat that keeps.\n\nButter goes off in a day in this heat and lamp oil makes a wound worse. The "
        "cook says the fat under a Shallows Snapper's shell stays fresh for weeks.\n\nThe "
        "snappers are out in the Tempest Shallows, east along the trunk road and down the "
        "strand road. Watch their beaks.",
        "That's good clean fat.\n\nI'll mix it with the bark and see if it holds. If it works "
        "I'll have proper burn dressings again. Thank you."),
    "tmp_hulls_and_ribs": (
        "I built boats in Booty Bay until the sea route opened three years ago and the "
        "Ashclaim offered me more. I need seasoned timber for barge hulls, and the jungle wood "
        "is too green. It warps "
        "before the pitch has dried, and I can't use it.\n\nThe best timber on the island is in the old wrecks out in "
        "the Tempest Shallows, but the Wreckpicker Murlocs strip the wrecks and carry the planks "
        "off to build with.\n\nGo east along the trunk road and down the strand road to the "
        "water, and take the timber off the murlocs.",
        "This is old oak that's been under salt water for years. It's harder than new wood.\n\n"
        "I can frame a hull with this. There's still something sinking my barges, though, and I "
        "want to talk to you about it."),
    "tmp_the_barge_eater": (
        "I've found out what's been sinking my barges.\n\nOne of my crew watched it from the "
        "beach. A loaded barge was crossing the bay and a huge crab came up under it and put a "
        "claw through the hull. The jetty hands call it The Barge-Eater.\n\nIt lives in the deep "
        "part of the Tempest Shallows, south-east of here past the last of the wrecks. It comes "
        "up for people who go out hunting it. Please kill it before I lose another crew.",
        "My crew saw you bring the claw up the beach.\n\nWe can launch again now. I'm going to "
        "mount the claw on the next hull. Take this, and thank you."),
    "tmp_clear_the_slip": (
        "My barges need a clear channel out of the bay, and the bottom's crawling with things "
        "that slow them down.\n\nThe Shallows Snappers bite at the steering oars and the "
        "Bargebreaker Crabs grab hold of the hulls. A slow barge is an easy target for worse.\n\n"
        "The channel runs out through the Tempest Shallows, east along the trunk road and down "
        "the strand road. Wade out and clear what you find.",
        "The pilot took a barge out on the evening tide and nothing touched the oar.\n\nThank "
        "you. Here's something from the saw pit stores."),
    "tmp_the_unhoused": (
        "The squatters in the forecourt follow one of their own, and I knew him before he went "
        "in.\n\nHis name's Borrik. He was a mason, and the Thane sent him down with the first "
        "party. He came out after six days and wouldn't go further than the forecourt. He says "
        "the city turned him away, and the others call him Borrik the Unhoused.\n\nHe keeps to "
        "the broken ground south and east of here. He'll come out for someone who's hunting "
        "him. I can't leave my post, and I don't think I could do it anyway.",
        "So he's gone.\n\nHe built half the hold in Cinderwharf before he went down there. The "
        "other squatters might go home now that he's not leading them. Take this, and thank "
        "you."),
    "tmp_whelps_in_the_vents": (
        "Khaz Varun gets its air through shafts that come out high on the mountain, and "
        "something's nesting in them.\n\nMy family kept those vents clear for nine generations. "
        "Now the Ashwing Whelps roost in the shaft mouths because the stone's warm, and they've "
        "filled them with ash and bones.\n\nThe vents open onto the Scoured Slope, north of here "
        "up the west road. Clear out the whelps for me.",
        "I felt the air at the arch change about an hour ago. It's blowing out again, the way "
        "it should.\n\nThank you. Take this with my family's thanks."),
    "tmp_nine_generations": (
        "You keep looking at that arch. Ask me about it before you do anything about it.\n\n"
        "When you're done, I've got a favour to ask. I keep a book of everyone who goes through "
        "the gate and everyone who comes back. The Thane hasn't seen it in two months because "
        "nobody will carry it to him.\n\nHe's in Cinderwharf on the north-east shore. Take the "
        "trunk road east, the east road north round the mountain, and follow the shore north "
        "to the town.",
        "This is Bron's book.\n\nForty-one have gone in since spring and twenty-six have come "
        "out. He's marked nine of those as not right. I signed the orders that sent most of "
        "them.\n\nI need someone who'll go down there anyway. If that's you, I've got work for "
        "you."),
    "tmp_prospecting_by_gizzard": (
        "Nobody's prospected this island since the gate opened three years ago, and I want "
        "to find the truesilver without digging up half of it.\n\nBasilisks swallow stones to grind their food, and they pick them up wherever they "
        "walk. If there's truesilver in a basilisk's gizzard, there's a seam somewhere on its "
        "route.\n\nThe Rubble Basilisks are thickest round Khaz Varun's Gate, south-west of "
        "here. Bring me the stones from their gizzards.",
        "Look at the silver in that one.\n\nMost of these have truesilver in them, so there's a "
        "seam near the gate. I'll go looking for it. Take your share of this."),
    "tmp_the_colour_of_the_rock": (
        "Truesilver usually shows in a blue-grey rock, and I can see two patches of that colour "
        "from here.\n\nBoth are up on the Scoured Slope. One's north-west, above the west road, "
        "and the other's north-east, above the east road. The Cinderslope Flame Spirits gather "
        "on that kind of rock and I can't get close.\n\nGo up to both outcrops and take a good "
        "look. You'll have to deal with the Flame Spirits first.",
        "The western one is the real thing and the eastern one is just weathered slag.\n\nThat "
        "saves me a lot of climbing. I'll stake the western outcrop tomorrow. Take this, it came "
        "out of the first seam I found here."),
    "tmp_what_grows_back": (
        "I'm studying a strip of the Scoured Slope where plants are growing back on the bare "
        "ash.\n\nI did the same work in the hills near Quito before the change, after the "
        "eruptions there. Here the first thing to grow back is a small red fern. The Ashscree "
        "Scorpions burrow under it and tear the roots up.\n\nThe slope is north of here, where "
        "the trees stop. If you can thin out the scorpions I'll be able to finish my notes for "
        "the season.",
        "The ferns on the lower plot are still standing. Thank you.\n\nI'll be able to keep "
        "watching that plot through the season now. The Ashclaim will get a copy of my notes."),
    "tmp_pressed_and_labelled": (
        "The Ashclaim pays me to tell them which plants here are worth money, and I've pressed "
        "forty of them between these boards.\n\nAlchemist Pell in Cinderwharf decides what the "
        "Ashclaim buys, so the press needs to reach him flat and dry.\n\nTake the east road "
        "north round the mountain into the Ashen Reach and follow the shore north to the town. "
        "He's by the salvage yard. Please ask him to send the boards back, it's the only press "
        "I've got.",
        "She's labelled every one of these properly. I was expecting a sack of leaves.\n\nI can "
        "sell three of these straight away, and the red fern could be worth a lot. Tell her "
        "she'll have her boards back, and that I'm asking the Ashclaim to raise her pay."),
    "tmp_my_boots": (
        "I went out to the near wreck in my good sea boots and came back without them.\n\nIt's "
        "the wreck you can see sticking up to the south-east. A Bargebreaker Crab got one boot "
        "and another one got the second while I was getting away.\n\nThey were made for me in "
        "Booty Bay and they've got brass toes. The crabs round that wreck will still have them. "
        "Please get them back for me.",
        "Those are mine. They're chewed, but they'll do.\n\nThank you. Here, this came out of "
        "the wreck before the crabs chased me off."),
    "tmp_whats_still_aboard": (
        "There are two big wrecks a long way out that still had cargo when they went down.\n\n"
        "One is south-east of here at the edge of the deep water. The other is further south, "
        "past the sandbar. The cargo was sealed in small casks, and the Wreckpicker Murlocs have "
        "been carrying them off.\n\nGo out to both wrecks and see what's left, and get the casks "
        "back from the murlocs. We'll split whatever's inside.",
        "It's lamp oil, and it's still good after all that time under water.\n\nTrader Gex in "
        "Cinderwharf will pay well for it. Take your half of the money, and I'll keep the "
        "casks."),
    "tmp_pay_chit": (
        "The Brawler had a brass tag on a string round its neck. It's a pay chit from the "
        "Ashclaim stores, the kind every porter at the landing gets, and it's stamped with a "
        "number.\n\nQuartermaster Durn at Ashclaim Landing keeps the pay book. He'll know whose "
        "number it is.",
        "I know this number. It belonged to Hedda, one of my porters.\n\nShe went to look at the "
        "gate on her rest day, because her grandmother was born in the city. I thought she'd "
        "gone home on the boat. I'll correct the book. Thank you for bringing this back."),
    "tmp_the_ships_log": (
        "The murloc was carrying a hardbound book. The pages are swollen with sea water but the "
        "ink can still be read. It's written in English, and the dates are from three years "
        "ago.\n\nThe dwarves and goblins won't be able to read it. Dr. Mwangi at Ashclaim "
        "Landing came through from Earth, so she probably can.",
        "This is the log of the MV Amani, a coastal freighter out of Dar es Salaam. I used to see "
        "her come into Mombasa.\n\nThe last entry is from the day everything changed. The mate "
        "wrote that the coast had disappeared and they were heading for the only land they "
        "could see. That must have been this island."),
    "tmp_who_was_aboard": (
        "The log only lists the crew by rank. I'd like to know their names.\n\nEvery seaman "
        "carries a discharge book with his name and photograph in it. The murlocs took the "
        "log, so they've probably taken those as well.\n\nThe log puts the ship aground at the "
        "far south-east corner of the Tempest Shallows. She'll be the only steel wreck out there. "
        "See if she's there, and bring back any of the books you can find. These people have "
        "been missing for three years.",
        "I can read every name in these.\n\nThis one is Juma Otieno, the second engineer, from "
        "Kisumu. I don't know if any of them got ashore. I'll copy the names out and send them "
        "with every boat that leaves, in case somebody has met them."),
    "tmp_empty_the_gatehouse": (
        "The first thing standing between us and the city is my great-grandfather's "
        "gatewarden.\n\nHis name was Hrun. He was holding the gate of Khaz Varun the night the "
        "city went dark, and he's still holding it. The gate opened by itself three years ago, "
        "on the day the world changed, and nobody I've sent in since has got past him.\n\nThe "
        "gate is on the south shore, a short walk south-east of Ashclaim Landing. Hrun is in the "
        "Gatehouse Hall past the Ember Road. He was a loyal dwarf, so make it quick.",
        "So Hrun can rest now.\n\nI'll have his name added at the shrine tonight. The gatehouse "
        "was only the first part. The worst of it's deeper in."),
    "tmp_the_forge_lord": (
        "The squatters at the gate say the forge is lit, and they're right.\n\nThe Great Forge "
        "of Khaz Varun has been cold since before my father was born, and now it's burning. The "
        "rolls say the last Forge-Lord was a dwarf named Darrok who never left his anvil.\n\nThe "
        "Great Forge is on the east side of the city, past the Counting Hall. Whatever is "
        "working that anvil, I want it stopped before it's finished.",
        "So Forge-Lord Darrok was still there.\n\nThe Underwriter will be glad the forge works. I'm "
        "less glad about what was being made in it. That leaves the hall itself, and the one "
        "who's in it."),
    "tmp_thane_morrun": (
        "My great-grandfather was Morrun Ashhold, and he's still sitting in his chair at the top "
        "of the city.\n\nOne of the first party got as far as the Hall of Ashhold and saw him "
        "through the doors. He hasn't been a living dwarf for a long time. The squatters call "
        "him the Unmade.\n\nI can't take the city back while he's sitting in that chair. The "
        "hall is at the north end of the city, past the Shadow Gallery. I'm asking you to kill "
        "Thane Morrun the Unmade.",
        "It's done, then.\n\nI've waited most of my life to hear that. Morn will light a flame "
        "for him tonight and I'll be there when he does. Take this, with the thanks of the "
        "Ashclaim."),
    "tmp_a_flame_for_each": (
        "I keep one flame on this terrace for everyone still down in the city, because I don't "
        "know their names.\n\nEvery Dark Iron of Khaz Varun carried a name-tablet, a small piece "
        "of iron with their name punched into it. The Ash-Wretches in the lower city were our "
        "people once, and some will still have their tablets.\n\nThe gate is on the south shore, "
        "south-east of Ashclaim Landing. The Ash-Wretches are in the Ash Pits and the Deep Way "
        "in the middle of the city. Bring me the tablets and I'll give each of them a flame.",
        "I'll read every one of these names tonight.\n\nTwo of them are Ashholds and one is an "
        "Emberhold, so I'll tell Bron at the gate. I'll look the rest up in the Deedkeeper's "
        "rolls. Thank you."),
    "tmp_the_iron_mask": (
        "There are dwarves in the city with iron masks riveted over their faces, and they "
        "weren't there before.\n\nSome of them are wearing Ashclaim boots. Something in the Cells "
        "is taking the people who go in, masking them, and sending them out to preach. Those "
        "who've seen it call it The Iron Mask.\n\nThe Cells are on the west side of the city, "
        "below the Deep Way. Please stop it before it takes anyone else.",
        "Thank you. Nobody else will be masked now.\n\nI can't help the ones already wearing "
        "them, but I'll say the rites for them anyway. Take this from the shrine. It should go "
        "to someone who's been down there."),
    "tmp_foundry_inventory": (
        "I've put money into a foundry I've never seen, and my partners want to know what "
        "state it's in.\n\nThe Thane says the works in Khaz Varun are sound. I'd like to hear "
        "that from someone who's actually stood in them.\n\nThe Smelter and the Great Forge are "
        "both on the east side of the city. The gate is on the south shore near Ashclaim "
        "Landing. Look them over for me. The Smelter still has its old master, Smelter-Master "
        "Vaud, and you'll need to get rid of him first.",
        "The crucibles are whole, the flues draw, and the Great Forge is hot.\n\nThat's better "
        "than I'd hoped. I'll tell my partners the works can be used. Here's your payment."),
    "tmp_what_masks_fetch": (
        "I've got a buyer on the mainland who collects Dark Iron work, and he wants the iron "
        "masks.\n\nThe Masked Zealots in Khaz Varun wear them riveted shut, and there's nothing "
        "else like them. I'd rather the Keeper didn't hear where they went.\n\nThe Zealots are "
        "all through the city from the Gatehouse Hall inward. The gate is on the south shore "
        "near Ashclaim Landing. I'll pay well for every mask.",
        "These are real. The rivets are still tight.\n\nThey're heavier than they look. I'll "
        "send them to the buyer and I won't be asking for more. Here's your money."),
    "tmp_grandmothers_mark": (
        "My grandmother was the best armoursmith in Khaz Varun, and I've never seen any of her "
        "work.\n\nShe got out as a girl with nothing but her hammer. One of the Thane's people "
        "says there's a machine in the Workshop called The Crusher, plated with armour taken off "
        "the walls, and that one of the plates carries the Stonecast mark.\n\nThe Workshop is on "
        "the west side of the city, just past the Ember Road. I'd like that breastplate.",
        "That's her mark under the arm.\n\nI can see how she shaped the edge, and it's not how I "
        "was taught. I'm going to spend tonight at the forge working it out. Take this, and thank "
        "you."),
    "tmp_the_rolls_below": (
        "The Thane's claim rests on the rolls I keep, and one of them is missing.\n\nWhen the "
        "city went dark, the Deedkeeper of the day carried out the records of births and debts. "
        "He had to leave the Roll of Oaths, because it was chained to a desk in the Counting "
        "Hall. Without it I can't prove which families swore to the Ashholds.\n\nThe Counting "
        "Hall is in the middle of the city, past the Gatehouse Hall. I'm told Overseer Grall "
        "still walks his rounds with the roll on his belt.",
        "It's all here, every leaf.\n\nEvery family on this wharf swore to the Ashholds, and now "
        "I can show it. I'll take this to the Underwriter tomorrow. Thank you."),
    "tmp_what_they_breathed": (
        "People go into that city sane and come out raving, and I want to know if it's "
        "something in the air.\n\nIf it is, it matters to everyone here, because we're shipping "
        "ore out of the same rock. The Crazed Miners in the lower workings have been breathing "
        "it longest, and their clothes will be full of it.\n\nThe gate is on the south shore "
        "near Ashclaim Landing. The miners are in the Ember Road and the Borer Workings. Bring "
        "me the dust, and cover your mouth while you collect it.",
        "It's mostly forge soot, but there's a fine red grit in it that glows when I breathe on "
        "it. It isn't in the ore we ship.\n\nSo it's coming from something burning down there "
        "now. I'll write to the doctor at the landing tonight."),

    # ================================================================ THE ASHEN REACH
    "tmp_four_barges": (
        "Four of my barges never arrived, and I think the naga have them.\n\nThe current off the "
        "landing runs north along the west shore. Anything that sinks in the bay washes up on "
        "the Scoured Coast, and the Stormscale Naga Raiders have been there since the sea route "
        "opened three years ago. They keep trophies, so they'll have the nameboards.\n\nLeave by "
        "the town gate and cross the Ashen Reach to its far west shore, past the Cinder Flats. "
        "Kill the Raiders and bring back any nameboards you find.",
        "These are all four of them.\n\nSo the naga had them. What I don't know is whether they "
        "found them wrecked or wrecked them. Take these boards to Adjuster Raman at the Merchant "
        "House. Working that out is her job."),
    "tmp_bad_luck_or_bad_seamanship": (
        "The Harbourmaster says naga sank those barges and the Underwriter says her pilots did. "
        "I'm paid to find out which.\n\nI did this work for nine years in Singapore before I came "
        "through. A barge that ran aground is holed underneath. A barge that was boarded is "
        "damaged along the rail.\n\nTwo of the wrecks are lying on the Scoured Coast, on the far west "
        "shore of the Reach, a good walk apart. Look at where each hull is broken. Bring me some of the hooks "
        "the Raiders carry as well, so I can match them to the damage.",
        "Both hulls are sound underneath and both rails are torn up.\n\nThese hooks have pine "
        "splinters in them, and the barges were pine. They were boarded while they were afloat. "
        "Raiders who only scavenge don't carry gear like this, so someone is organising them."),
    "tmp_the_wreck_captain": (
        "The Adjuster's report names someone the coast surveyor has been telling me about for "
        "months.\n\nShe says a naga gives the orders from the old wrecks, and she calls it "
        "Wreck-Captain Vess'ira. The raiders bring everything they take back to it.\n\nIt stays "
        "on the Scoured Coast on the west shore of the Reach. It'll come out for someone who's "
        "hunting it. My crews won't sail until it's dead.",
        "That's its helm. It was wearing one of my berth tags.\n\nI'll post the news on the "
        "wharf tonight and the pilots will sign on again. Thank you. This is from the harbour "
        "office."),
    "tmp_a_harbour_chart": (
        "I've finished my chart of this coast and it needs to get to Harbourmaster Skezz.\n\nThe "
        "last two times I tried to take it myself I lost a boat. She needs it before she sends "
        "another barge round the west side.\n\nCinderwharf is on the north-east shore. Head east "
        "across the Cinder Flats to the town gate. She's on the wharf at the north end of town.",
        "Every reef and wreck is marked on this.\n\nNobody has had a chart of this coast since "
        "the sea route opened three years ago. I'll send the surveyor a bottle to say thank "
        "you. Take something from the harbour office."),
    "tmp_older_than_the_ashclaim": (
        "Someone was sailing to this island long before the goblins found it, and I'd like to "
        "know who.\n\nThe old wrecks on this shore are oak and brass, and the brass is better than "
        "anything my people cast. The Scourcoast Crabs pick the fittings off and carry them "
        "around.\n\nThey're all along the waterline, north and south of here. Bring me some of "
        "the fittings and I'll look for a maker's mark.",
        "There's a mark on this one. It's a hammer over a flame.\n\nThat's the old seal of Khaz "
        "Varun. The dwarves had ships and traded from this coast before their city went dark. "
        "The Thane will want to hear about this."),
    "tmp_pitch_for_two_boats": (
        "My last two boats both leak and I've got no pitch to seal them.\n\nThere's tar on this "
        "island, though. It seeps up warm round the vents, and the Tarfoot Gorillas walk through "
        "it until their feet are caked in it.\n\nThey're in the open ash country east of this "
        "coast, between here and the Works. Bring me the tar off their feet.",
        "That's good tar, and it's still soft.\n\nI'll have both hulls sealed by tomorrow. "
        "Thank you. Take this, it washed up last week."),
    "tmp_weighed_at_the_gate": (
        "If you're going out to the Works, can you take the weigh book with you?\n\nI weigh every "
        "cart of ore that comes through this gate. Assayer Ruddi weighs the same carts when they "
        "leave the Works. If his book and hers don't match, someone's stealing on the road.\n\n"
        "The Works is a long walk west of here, past the Cinder Flats. Follow the cart ruts.",
        "His numbers match mine for every cart this month.\n\nSo nobody's stealing on the road. "
        "The ore we're missing is going missing before it reaches my scales. Come back and see "
        "me once you've had a look round the yard."),
    "tmp_the_ore_road": (
        "I've got sixty people in this yard, and I'd like to keep all of them.\n\nThe ore goes out "
        "by cart across the Cinder Flats to the town gate. The Sulphur Raptors run down the "
        "carts for the mules. The Ashplain Basilisks lie in the ruts looking like rock until a "
        "carter steps on one.\n\nThe Flats are north-east of the yard. Walk the cart road and "
        "kill what's on it.",
        "The afternoon carts got to the gate without stopping.\n\nI've put you on the books for "
        "today. This is Works issue."),
    "tmp_things_that_walk_through_fire": (
        "I can deal with the animals on the Flats. The fire elementals are the problem.\n\nThe "
        "Scoria Fire Elementals come up out of the vents and wander in straight lines, and "
        "anything they walk into burns. Last week one walked through the tool store.\n\nThe "
        "Deedkeeper says there weren't any on this island when the dwarves left. They started "
        "appearing after the day the world changed. They're on the Cinder Flats, north-east of "
        "here. Put out as many as you can.",
        "The lookout says there are fewer glows on the Flats tonight.\n\nThat's the first time "
        "the number's gone down. Take this from the yard stores."),
    "tmp_old_scoria": (
        "There's one elemental out on the Flats that's much bigger than the rest, and it "
        "doesn't wander.\n\nThe carters call it Old Scoria. It stands in the middle of the "
        "Cinder Flats for days, and the small ones come up out of the ground around it. My "
        "scout thinks it's calling them.\n\nIt's north-east of the yard, where the crust is "
        "darkest. It'll come up if someone goes looking for it. If you can kill it, we might get "
        "some peace.",
        "The whole yard felt it go. The ground jumped and then went quiet.\n\nVarga came in an "
        "hour ago and said she hadn't seen a single elemental on her round. Thank you. Choose "
        "whichever of these suits you."),
    "tmp_brass_in_a_month": (
        "The air off these vents eats my gaskets faster than I can cut them. The dwarves say the "
        "vents were gentle before the day the world changed.\n\nI've found something that holds "
        "up. The Steamvent Oozes live in the steam vents and their skin isn't bothered by acid at "
        "all. A strip I cut off a dead one has lasted a month in my worst flue.\n\nThey're on "
        "the Scoured Coast, north-west of the Works, wherever there's steam coming out of the "
        "rocks. Bring me their membranes.",
        "These are just right.\n\nI'll cut new gaskets for the whole pump engine tonight. Thank "
        "you. Have this, I made it and never got round to using it."),
    "tmp_drive_belts": (
        "The winding gear at the mine head runs on leather belts, and the heat down the shaft "
        "ruins them in a week.\n\nThe only hide I've seen that doesn't mind the heat belongs to "
        "the Ashplain Basilisks. They lie on hot rock all day.\n\nThey're out on the Cinder "
        "Flats, north-east of here. Try to bring me whole hides.",
        "That's a good thick hide with no scorch marks.\n\nI'll have it on the drum by the end "
        "of the shift. Thank you. This is from the mine head stores."),
    "tmp_the_number_he_wont_like": (
        "I've worked out why we're short of ore, and the Underwriter won't like it.\n\nNobody's "
        "stealing it, because the seam is running out. Every cart is a little poorer than the "
        "last, and the upper workings will be finished within a year. The rich ore is deeper, "
        "under the Emberdeep.\n\nI can't leave the scales. Please take this to Underwriter Nix "
        "in the Merchant House in Cinderwharf. Head east across the Flats to the town gate.",
        "I've read it twice and she's right. She always is.\n\nSo the venture needs the deep "
        "ore, and the deep ore is under a lake of fire. I'll need to think about what that "
        "means."),
    "tmp_yellow_crust": (
        "The alchemist in town has been buying something off the carters for pennies, and I "
        "want to know what it's worth.\n\nIt's a yellow crust that forms round the fissures. The "
        "Ventborn Flame Spirits come out of those fissures covered in it. If I'm right about the "
        "colour, there's gold in it.\n\nThe fissures are on the Emberdeep Approach, east of the "
        "yard on the way to the big door. Bring the crust back to my scales.",
        "It's rich in gold. I ran it twice to make sure.\n\nPell's been paying a copper a pound "
        "and selling it for silver. From tomorrow I'm weighing this as well, and the dwarves will "
        "be paid for it."),
    "tmp_walking_into_the_face": (
        "I can't fire a charge while something's standing in front of it.\n\nThe Crag Earth "
        "Elementals walk up out of the Emberdeep Approach and into my blast faces. I think the "
        "drilling draws them. Then I've got to pull every charge out by hand before I can try "
        "again.\n\nThe Approach is east of the red shed, on the way to the big door. Break up "
        "the ones you find before they reach my faces.",
        "I fired three faces this afternoon and there was nothing in them but rock.\n\nPulling a "
        "live charge is the most dangerous part of this job. Thank you, and take this."),
    "tmp_a_pulse": (
        "I've told the Foreman this mountain has a pulse, and she wants me to prove it.\n\nBefore "
        "the change I had forty instruments at Sakurajima. Here I've got three tiltmeters I built "
        "from clock parts. If I put them at three vents far apart and they all move at the same "
        "moment, then one thing is moving under the whole island.\n\nPut the first on the "
        "Cinder Flats, north-east of here. Put the second at the steam vent on the Scoured "
        "Coast, to the north-west. Put the third at the big fissure on the Emberdeep Approach, "
        "south-east of the yard. Set each one level on bare rock.",
        "All three needles moved together.\n\nIt happens every nine minutes, at every vent, at "
        "the same moment. A magma chamber doesn't behave like that. I don't know what does, and "
        "I'd like to find out."),
    "tmp_what_the_drakes_carry": (
        "I need a sample from the lake under the mountain, and I can't get close enough to take "
        "one.\n\nThe Calderaborn Drakes roost inside the crater and swallow hot glass from the "
        "edge of the lake. Before I came through I'd have sent a drone over the rim. Here I need "
        "you to cut open a drake.\n\nThey hunt over the Emberdeep Approach, south-east of the "
        "yard. Bring me the glass while it's fresh, because it changes as it cools.",
        "It's still warm, which is what I needed.\n\nThere are threads running through this glass, like grain in "
        "wood. Molten rock doesn't do that. Something is growing in that lake, and I think "
        "it's what's making the pulse."),
    "tmp_the_mountains_heart": (
        "Everything I've measured points to one chamber on the west side of the lake. The "
        "Doorwarden says there's something in it.\n\nHis people call it The Mountain's Heart. It "
        "beats every nine minutes, and the fire elementals come up on the beat.\n\nThe door to "
        "the Emberdeep is east of the yard, at the end of the Approach. The chamber is deep in, "
        "on the western shore of the lake. I'm sorry to be sending you into it.",
        "All three needles stopped at the same moment.\n\nThe vents are still smoking, but it's "
        "an ordinary volcano now, and I know how to watch one of those. When the bay at "
        "Kagoshima vanished three years ago I didn't think I'd be doing this work again. Thank "
        "you."),
    "tmp_where_the_vents_moved": (
        "I've got three marker posts at the edges of the Flats, and I can't get round them this "
        "week.\n\nEach post has a rope pegged out to the nearest vent. If the vent moves, the "
        "rope goes slack or burns through. That tells me where it's safe to send the carts. I "
        "turned my ankle two days ago.\n\nOne post is to the north-west, one is to the north-east, "
        "and the third is south-east toward the town gate. Check the rope at each one.",
        "So the north-west rope has burned through and the other two are fine.\n\nThe western "
        "vent has moved toward the cart road. I'll move the road markers east in the morning. "
        "Thank you. Take this, I won't need it until my ankle heals."),
    "tmp_the_ventlord": (
        "There's something on the Emberdeep Approach that opens new vents wherever it walks.\n\n"
        "I saw it at dawn on the south edge of the Flats. It came up the slope from the big "
        "door, as tall as the winding tower, and the ground split and steamed where it stepped. "
        "The Doorwarden's people call it Karrath the Ventlord.\n\nIt walks the Approach, south "
        "of here. It'll come out to meet someone who's hunting it. If it ever reaches the Works, "
        "we're finished.",
        "I watched the steam stop all along the Approach at once.\n\nThe Foreman told me to give "
        "you this when you came back. Thank you."),
    "tmp_the_door_was_sealed": (
        "If you're going down there, you should hear what I know first.\n\nAsk me about the seal "
        "and the day it broke. After that, I'd like you to take my door book to Keeper Morn in "
        "Cinderwharf. He keeps the old rites, and the seal on this door was one of them.\n\n"
        "The town is north-east of here across the Cinder Flats. Morn is on the Shrine Terrace "
        "in the south-west of the hold.",
        "Kettil has written down every time the door has breathed. There are a lot of "
        "entries.\n\nThe seal was an Ashhold rite. My grandfather knew the words and my father "
        "knew half of them. I don't know them at all, so I can't close that door again. Please "
        "be careful down there."),
    "tmp_whatever_came_off_the_boat": (
        "The stew is usually whatever came off the boat, and this week nothing came off the "
        "boat.\n\nThe carters say the Scourcoast Crabs on the west shore taste smoked already, "
        "because of the vents.\n\nLeave by the town gate and go west across the Reach to the "
        "Scoured Coast. Bring me the meat and I'll get the pot on.",
        "It does smell smoked.\n\nThe dwarves had three bowls each and the goblins asked for the "
        "recipe. Thank you. Your name's on the board, and this is for you."),
    "tmp_no_questions_about_the_powder": (
        "I need a keg taken to Blaster Orrin at the Works, and I'd rather you didn't ask what's "
        "in it.\n\nHe's at the red shed on the south side of the yard and he's expecting it. If "
        "anyone at the gate asks, it's pickled fish.\n\nThe Works is west of town across the "
        "Cinder Flats. Carry it level and keep it away from anything that's burning.",
        "That'll be Gex's powder.\n\nThe official powder comes over on the boat and half of it's "
        "damp when it lands. Gex buys the damp kegs as scrap, dries them out and sells them "
        "back to me. His always fires, so I don't ask questions either."),
    "tmp_the_landing_shelf": (
        "The venture needs the deep ore, and the deep ore is past a door I can't get a survey "
        "party through.\n\nJust inside the Emberdeep there's a shelf of rock where a party "
        "could set up. The Doorwarden says it's held by a pack of hounds made of cinders, led "
        "by one he calls Pack-Alpha Cinderhound.\n\nLeave by the town gate and go south-west "
        "across the Reach. The door is at the end of the Emberdeep Approach, east of the Works. "
        "Kill the alpha and the pack should scatter.",
        "The shelf is clear, so I can put surveyors on it this week.\n\nThank you. Here's what "
        "the Ashclaim owes you."),
    "tmp_geyser_rights": (
        "My surveyors are on the shelf now, and they've sent back a note about steam.\n\nThere's "
        "a field of geysers on the west side of the lake that could drive every engine the Works "
        "needs. There's also something living in it that boiled one of my surveyors. The "
        "Doorwarden calls it Thrass.\n\nThe field is a short way in from the Landing Shelf, to "
        "the west. The door is at the end of the Emberdeep Approach, south-west of town. Please "
        "get rid of Thrass, the Geyser Spirit.",
        "The surveyors say the geysers are still running and nothing is attacking them.\n\nThat's "
        "free power for a foundry. Three years ago all I had was a deed nobody could reach. "
        "Thank you, and here's your pay."),
    "tmp_a_scale_that_stays_hot": (
        "I've heard there's a serpent in the Emberdeep whose scales never cool, and I'd like one "
        "for the forge.\n\nA smith spends half his time waiting for metal to come back up to "
        "heat. A plate that stayed hot on its own would save me hours. The Doorwarden's people "
        "call it The Molten Serpent.\n\nIt's in the middle of the Emberdeep, past the geysers. "
        "The door is south-west of town at the end of the Emberdeep Approach. I only need one "
        "scale.",
        "Put it on the anvil. I can feel the heat from here.\n\nIt hasn't cooled at all. It's "
        "going into the bed of my forge tonight. I made you this while you were telling me how "
        "you got it."),
    "tmp_what_the_vents_cough_up": (
        "There are crawlers in the Emberdeep that live on raw sulphur, and I want what's in "
        "them.\n\nEach Sulphur Crawler stores the sulphur in a gland, purer than anything I can "
        "make. With it I can make an acid that will take the rivets out of those iron masks "
        "without hurting the person wearing one.\n\nThe door is south-west of town at the end "
        "of the Emberdeep Approach. The Crawlers are on the Basalt Shelf, east of the lake. "
        "Bring me the glands whole.",
        "These are perfect.\n\nI tried a drop on one of the masks and the rivets went soft in a "
        "minute. If any of the masked dwarves can be brought out alive, we can get the masks off "
        "now. I'll tell the Keeper, and I won't charge for it."),
    "tmp_the_oracle": (
        "There's a name in my rolls with no date of death, and I think I know why.\n\nYsmel "
        "Ashhold was the city's seer. The roll says she went into the mountain to ask it a "
        "question, the year before Khaz Varun went dark, and never came back. The Doorwarden "
        "tells me something in the Emberdeep calls itself Flame Oracle Ysmel.\n\nShe's in a "
        "ring of standing stones on the east side of the lake. The door is south-west of town at "
        "the end of the Emberdeep Approach. I'd like her to be at rest.",
        "Then I can finally write the date beside her name.\n\nThank you. This was kept with her "
        "roll, and I think she'd want it to be used."),
    "tmp_the_deep_claim": (
        "The last thing on my shelf is a claim marker.\n\nIt's a Dark Iron stake with the Thane's "
        "seal on one side and the Underwriter's on the other. It's meant to be driven into the "
        "floor of the caldera at the bottom of the Emberdeep once someone kills what lives "
        "there. The Doorwarden calls that thing The Caldera.\n\nThe door is south-west of town "
        "at the end of the Emberdeep Approach, and the caldera floor is as deep as the "
        "Emberdeep goes. Nobody has taken the stake yet.",
        "The stake is gone from your pack, so it's where it belongs.\n\nThe whole mountain belongs "
        "to the Ashclaim now, from the gate of Khaz Varun down to the bottom of the fire. You've "
        "earned anything I've got. Take this first."),
    "tmp_kin_under_another_roof": (
        "The old Thane is at rest and the hall is quiet, and there's someone who should be "
        "told.\n\nThere's another Dark Iron hold called Onyxhollow, under the Black Strand far "
        "to the west across the sea. Its Thane is Morgrim. Our families traded before either city "
        "went quiet, and he should hear from us that Khaz Varun has a living Thane again.\n\n"
        "It's a long way. Take the bird from the pad to Saltspur, cross to Kalimdor, and go down "
        "through the Abyssal Sands to the Black Strand. Onyxhollow's gate is at the end of the "
        "slag road.",
        "A letter from Khaz Varun. I'd been told that city was a grave.\n\nMy grandmother used to "
        "talk about the Ashholds. I'll write back to him. Tell the Keeper that Onyxhollow will "
        "light a flame for his dead as well."),
    "tmp_the_tide_chart": (
        "The Raider had a sheet of sharkskin rolled in its belt. It's pricked with small holes, "
        "and when you hold it up to the light the holes show this coast with a line running "
        "between the reefs.\n\nCoast-Surveyor Mizzi is camped on the Scoured Coast and has been "
        "trying to chart these waters. She'd know what the line means.",
        "Hold it up to the lamp for me.\n\nThat's a deep-water channel through the reefs. I've "
        "been looking for it for a year and the naga knew where it was all along. Thank you, "
        "this saves me a great deal of work."),
    "tmp_lantern_nineteen": (
        "There was a lantern stuck in the elemental's side, half melted. It's the kind the "
        "Ashclaim gives its carters, and the brass plate on the bottom is stamped with the number "
        "nineteen.\n\nForeman Brakka at the Ashclaim Works signs those lanterns out. She'll know "
        "whose it was.",
        "Nineteen is Olla Burrfoot. She took a cart out four days ago and the mule came back "
        "without her.\n\nI've had people looking for her on the Flats ever since. I'll write to "
        "her brother. Thank you for bringing it in."),
}
