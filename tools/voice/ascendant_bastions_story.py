"""The Ascendant Bastions' story pass (22 Nov 2026), to docs/quest_writing_standard.md, written after Dawnspear Wreck was
built and its people moved in. The deserters stand in the town; the Yard Pens' conscripts are held where they are (Kyle,
22 Nov 2026: "Keep the pens as is"), so they still speak from the pens, and only their dungeon quests moved into town.
Every speech is the giver talking from where they now stand; every accept line is a new beat."""

STORY = {
    'abq_count_the_keels': (
        "Fen counts the hulls from the bow every evening, but a count doesn't tell me how close they are to flying. The slipways are east of the wreck, along the quay, five finger piers with a warship on every berth. I brought the Dawnspear down rather than fire on Tethertown, and I'd like that to have bought more than a season. Walk out along the first pier, the middle one and the last one, and look at what's in the berths. The yard's busy, so keep moving.",
        'Look at the masts. A hull with its masts stepped is a week from flying.'),
    'abq_rivets_and_rot': (
        "Every day the yard works, those keels get closer to flying, and they're nearly there. Every Ascendancy Shipwright on the quay east of here knows the ships better than I do, and every Keel Construct can lay a keel in a week. I commanded one of those ships for nine years, so I know what one costs to finish. I'd rather not see a new one crewed by people I trained. Take them off the work, and the warships wait.",
        'The shipwrights carry their plans on them. Burn the plans if you find any.'),
    'abq_the_unlaunched': (
        "There's a hull on the slipways that was laid down and never finished. The yard's engineers woke its guns up to test them, and they couldn't put it back to sleep. The Unlaunched drifts along the quay east of the wreck now, and it kills shipwrights as happily as it kills us. I've watched it from the bow for a month. Put it down properly.",
        "It swings its guns slowly. Stay on the side it's just fired from."),
    'abq_the_foundry_gate': (
        "The hulls are built on the slipways, but their engines aren't. They come down the causeway out of the citadel's south gate, from the Gravity Foundry under it, north-east of here at the head of the causeway. I watched them load the Dawnspear's engine through that gate when she was new. Go and look at it. Sooner or later somebody's going to have to go through it, and I want you to know where it is.",
        "Don't go in yet. Look, count the guards, and come back."),
    'abq_the_foundry_master': (
        "Every week the Gravity Foundry sends down to the Yard Pens for more hands, and Hamza in the pens cooks for fewer people every week. He gets word to me on the skiff ropes, and this week's word was a name. Foundry-Master Cassor Vane picks the conscripts himself from the gallery at the top of the foundry, with those stones going round his head. Go in through the citadel's south gate, north-east of here, and put him down. Take friends, because the whole foundry works for him.",
        'Hamza will hear it the same day. Word moves fast on the ropes.'),
    'abq_the_warheart': (
        "The day that first warship flies, the free skiffs stop flying, because nothing we've got can outrun a gun deck. Its engine is nearly done, down in the Keelworks under the Gravity Foundry, and they call it the Warheart. The way down is through the foundry, past the Foundry-Master's lift, north-east of here through the citadel's south gate. I'd go myself if I thought I'd come back. Get down there and break it.",
        'If it wakes before you get there, break it anyway. A half-built engine still bleeds.'),
    'abq_the_lance_commander': (
        "I've lost four skiffs this year to lancer wings, and every one of them flew out on Lance-Commander Aris Thane's orders. He holds the Lancer Halls inside the citadel's north gate, in the Ascendant Spire, north-east of the wreck. Tavin says he won't stop while he's still in the saddle, and Tavin should know, because Thane trained him. My pilots had families in Aurelion. Go in and unhorse him.",
        "Go for his steed first. On foot, he's just another officer."),
    'abq_clear_skies': (
        "Every Smoke-Gale Hawk between here and Aurelion has learned that a skiff's full of food. They nest in the chimney smoke over the citadel, north-east of here, and dive at the sails and the rigging when my skiffs come in. Last week one brought a skiff down in the Ashwake, and we pulled the pilot out of the smoke alive. I've been flying the free skiffs for six years, and the hawks are worse than the guns. Clear them off the approach.",
        "They're slow climbing back up after a dive. That's the moment."),
    'abq_the_pourmasters': (
        "Half the burns I treat come across the causeway at night from the Yard Pens, and Siobhan tells me where every one of them came from. The twins run the quench halls in the Gravity Foundry. Pourmaster Ilka pours, her brother Dov quenches, and when they're behind, they make the conscripts carry the crucibles by hand. I've dressed three arms this month with molten crystal down them. You'll find the twins on the foundry's east side, through the citadel's south gate.",
        "You'll have to fight both of them at once. They never leave each other's side."),
    'abq_the_inquisitor': (
        "Everyone the Ascendancy catches ends up in front of High Inquisitor Seren Vash, in the Inquisitorium at the bottom of the Ascendant Spire's first halls. The few who came back to me couldn't sleep for weeks, and one of them still can't. The Spire is through the citadel's north gate, north-east of the wreck. Go in past the lancers or round by the storm gallery. Put an end to the questions.",
        "Don't listen to anything Vash says. That's how the questions start."),
    'abq_burn_salve': (
        "Most of what I treat is burns from the storm guns, and I've run out of salve. Every Smoke Jelly drifting in the Ashwake, south of the wreck, carries a cool gel inside it. It's better than anything Aurelion ever sent me, and I wish I'd found it years ago. The last pot went on a lancer's hands two nights ago. Bring me as much as you can carry.",
        "Scoop the gel out with something that isn't your hand. It numbs for an hour."),
    'abq_the_ash_mother': (
        "The scouts say there's something big out in the Ashwake, deep in the smoke south of here, and the jellies drift out of it in clouds. They call it The Ash-Mother. It's thickened the smoke round the wreck until you can't see the bow from the stern, and half my patients are coughing again. I've stopped being polite about it. I want it dead.",
        'Follow the jellies upwind. They all drift away from her.'),
    'abq_ash_in_the_lungs': (
        "The citadel's chimneys never stop, and every Forge-Ash Wisp that comes out of them drifts down onto the wreck. Half the camp coughs all night, and the coughing keeps the other half awake. I ran the Dawnspear's mess for eleven years, and I can't keep a pot of stew clean with ash falling in it. I can't fix the chimneys. You can thin out the ash, though.",
        "They settle on anything warm. Stand by the mess fire and they'll come down to you."),
    'abq_the_book_of_home': (
        "Hamza in the Yard Pens and I trade recipes on the skiff ropes, and he told me about the book. The pens kept a book of recipes, songs, street names, anything anyone could remember from home, so they wouldn't lose it. The Inquisitors took it for the Burning Archive in the Ascendant Spire, and Archivist-Censor Mallen Roe burns everything that comes in. He's off the Inquisitorium's north door, through the citadel's north gate. If the book's gone, at least stop him burning the next one.",
        "If you find it, bring it to me first. I'll copy every page before it goes back to the pens."),
    'abq_the_right_hand': (
        "Maelis isn't here. She's gone north, and Exarch Lucan Thessaly gives her orders on the Bastions while she's away. He was my student too, before he was hers. You'll find him at the very top of the Ascendant Spire, in the Exarch's Sanctum past the Aegis Engine and his own guard, through the citadel's north gate north-east of here. Take him off the board, and she'll have to come back and see for herself.",
        "He was always the one who finished his work early. Don't give him time."),
    'abq_her_old_teacher': (
        "I taught Ascendant-General Maelis Ardane when she was the brightest student the Patient Lens had in a century. She built two things on the Bastions that I can't forgive. One trains children to ride at the tree, and the other burns the house's oldest records. The arena is on the Proving Grounds, north of the wreck, and the Censor-Archive's yard is further north again. Go and look at both, and come back and tell me what her people were doing.",
        "Tell me exactly what you saw. I've had enough of people softening it for me."),
    'abq_what_they_burn': (
        "There's a clerk at the Censor-Archive, north of here past the Proving Grounds, called Anselm Rook. He was a copyist at the Patient Lens, a good one, and the Ascendancy took him along with the archive. I haven't written to him in six years, because a letter from me could get him killed. Give him this one. He'll know my hand, and he'll know I'm asking him for something dangerous.",
        "Give it to him when nobody's watching. He'll know to burn it after."),
    'abq_burn_nothing_more': (
        "The fires at the Censor-Archive make things. Every Cinder-Script Wisp is a book that burned, still glowing with what was written in it, and every Archive Warden stands there to make sure the fire's fed. The archive is north of the wreck, past the Proving Grounds. I taught from some of the books those wisps used to be. Put out the one, and send the other packing.",
        "If a wisp's words are still readable, read them. Somebody should, once."),
    'abq_copied_before_burned': (
        "I copy what I can before it burns, and I've filled a hundred books in secret. I can copy paper, but I can't copy stone fast enough. The oldest records are plates, and every Censor-Inquisitor here carries them out to be broken in the fire. Bring me the pieces they're carrying, before they get there. I'll put them back together.",
        'Bring every chip, even the small ones. A plate with a hole in it says less.'),
    'abq_three_seals': (
        "Look at the bottom of the plate you pieced together. That's the old house mark, the one our oldest books carry. That's a Kharad rune beside it, I'm sure of it, and the last one is a Veyr talon-print, pressed into the stone while it was soft. Three seals on one record, and the Ascendancy burns every copy it finds. Take it south to Magister Orla Thessan at Dawnspear Wreck.",
        "Wrap it in my coat. If they search you, it's just a clerk's old coat."),
    'abq_high_censor': (
        "High Censor Ilsabet Morn chooses what goes into the fire here, and she reads everything first. She's started asking me why the copying takes so long. Yesterday she stood behind my desk for a whole hour without saying a word. Sooner or later she'll look in my drawer. I'd like her not to.",
        'She works alone in the high reading room. Nobody will come when she calls.'),
    'abq_the_riders': (
        "The recruits on the Proving Grounds are children, most of them, and they're frightened. They train on foot, and every Mounted Sky Lancer there rides down the ones who fall behind, to teach the rest to keep up. I did it myself for two years, and I can still hear them. The Proving Grounds are north of the wreck. I'd like you to stop the riders.",
        "Don't hurt the recruits. They'll scatter when the riders fall."),
    'abq_unhorsed': (
        "A lancer without a steed is a soldier who walks, and nobody's walking to the tree. Every Mounted Sky Lancer on the Proving Grounds, north of here, rides a bronze steed with a crystal core in its chest. I rode one for six years, and I know where the core sits. Without the cores, those steeds are just very expensive statues. Bring me the cores, and the wing stays on the ground.",
        "The core's behind the left shoulder plate. Pry it from the bottom."),
    'abq_the_lance_master': (
        "Lance-Master Varro Dain taught me everything I know about the lance, and he taught me to ride down children. There's a new intake of recruits coming from Aurelion next month, and he'll be waiting for them on the Proving Grounds, north of the wreck. I still salute when I think of him, and I hate that I do. He'll stand in the middle of the arena on the Proving Grounds, because he always does. I don't want him there to meet them.",
        "He'll offer you a fair fight. He's lying, there are always two more behind him."),
    'abq_the_wall_captain': (
        "Wall-Captain Hesper Drace walks the apron round the citadel, north-east of here, and every deserter her guard catches hangs from the walls for a week. Two of the lancers who followed me here were caught on the way. I can see the walls from the yard on a clear day, and I've stopped looking. Their names were Jessa and Corin, and they were good lancers. I'd like the walls to be empty.",
        'She walks the same circuit every hour. Wait by the south corner.'),
    'abq_eyes_on_the_gunline': (
        "The storm guns on the Gunline turn every evening, and from the bow I can't see what they're turning to face. The Gunline is east of here, three platforms off the fort's east side. I've drawn every one of those guns from here, and I still can't tell where they're pointing. Walk the platforms, all three, and look where the barrels point. The crews won't like you being there, so be quick.",
        "Look at the sighting marks on the rails. They scratch the target's bearing there."),
    'abq_silence_the_guns': (
        "The Gunline's crews are ranging their guns on the World Tree, and I can see the muzzle flashes from the bow. A gun's only a gun without a crew. Every Storm Artillerist and every Arcane Bombardier on the platforms east of here knows how to range on a target a long way off. I've seen one shot land short in the cloud, and it boiled for an hour. Take them off the platforms, and the guns can't find anything.",
        'Hit the bombardiers before they charge. Their shots arc, so close the distance fast.'),
    'abq_the_battery_master': (
        "Battery-Master Ormund Krell worked out the ranges to the tree himself, by hand, and it's taken him three years. Nobody else on the Gunline understands his numbers, and he likes it that way. He keeps to the central platform, east of the wreck. I don't want him dead for his own sake. If he goes, they have to start again.",
        "Burn his notebook if you can find it. That's the real target."),
    'abq_the_road_north': (
        "Every few days a column goes north up the Firmament Road off the citadel's northern bastion, and it never comes back the same size. The road leaves the fort north-east of here and keeps going. I've counted the columns from the bow for a year, and the numbers don't add up. Walk to the end of the road and look. I want to know what's out there that's worth so many soldiers.",
        "Carry plenty of water with you. The road's longer than it looks from the bow, and there's nothing on it."),
    'abq_weak_seams': (
        "Every seam I weld, I weld well when they're watching, because they check. Not every seam gets checked, though. I've marked the ones that won't hold in a storm, every one, ship by ship, on a chart I keep in my boot. The captain at Dawnspear Wreck, west along the quay, will know what it's worth. Take it to her.",
        "Don't run on the quay. Running is what makes the overseers look."),
    'abq_the_overseers': (
        "Every Yard Overseer on the quay carries a rod, and they don't hesitate to use it. The conscripts work sixteen hours on the slipways west of the pens, and when someone falls asleep on a weld, the overseers wake them up. I welded ships in Valparaiso for ten years and never once saw a rod. One of them broke a boy's wrist last week for dropping a rivet. Take the overseers off the quay for a while.",
        'They walk in pairs. Take one, and the other comes running to you.'),
    'abq_the_drones_fix_it': (
        "I weld a seam weak, and two days later a Slipway Repair-Drone finds it and fixes it properly. They're patient, they never stop, and they never miss one. They crawl the hulls on the slipways west of the pens day and night. I've watched one undo a week of my work in an afternoon. If they're gone, my seams stay the way I left them.",
        "They're slow on the downhill side of a hull. Catch them there."),
    'abq_lay_no_more_keels': (
        "The yard lays a new keel every month, and every Keel Construct carries the governor that knows the pattern. I've watched them lay the last three from my bench. Without the governors, nobody here can start a new ship, and the five on the slipways west of the pens are all they'll have. Each one I see go out on a hull is another ship I'll have to weld. Bring me the governors.",
        "The governor's the brass box on its back. It comes off with a twist."),
    'abq_medicine_run': (
        "I've got two hundred patients and one tent, and the yard gives us nothing. The surgeon at Dawnspear Wreck, west along the quay, sends what she can when someone can carry it. I nursed in Galway for fifteen years, and I've never had to beg for bandages before. Half of what I need, she doesn't have either, but the other half keeps people alive. Take her this list.",
        "Don't let the hounds on the causeway see you. They'll follow you all the way back."),
    'abq_clean_water': (
        "The water we get runs off the slipways, through the rivets and the oil, and it's making people sick. Every Harvested Storm on the rock to the north-east holds rain inside it, clean rain, the cleanest on the Bastions. I've had four children with fevers this week. I boil what I can, but there isn't enough wood in the pens to boil for two hundred. Bring me what you can wring out of them.",
        'Carry it in something sealed. Storm rain goes sour if it touches the air too long.'),
    'abq_the_hounds': (
        "Every Causeway Construct Hound on the causeway north-west of the pens is set to hunt anyone who hasn't got an Ascendancy mark. Two of my patients tried to reach the wreck last month. The hounds brought back what was left, and the overseers made us look. I sat with the mother of one of them until morning. Clear the causeway.",
        "They hunt by sound. Walk soft and they'll pass you by."),
    'abq_cut_the_rigging': (
        "I rigged every Ascendancy Gunship that flies the Firmament Road, north of the fort. I know where their sails are weakest, because I made them that way when I could. I worked the shipyards in Gdansk before all this, and I never thought I'd rig a ship to fail. Bring them down. I'd like to know my knots did something useful.",
        "Aim for the lower sail on the port side. That's the one I rigged worst."),
    'abq_thunderbirds': (
        "Every storm, a Harvest Thunderbird or two comes down off the Storm Harvest, the rock north-east of here, and goes through the warships' sails like a knife. The yard says I rig them badly and docks our rations for every tear. I can mend a sail, but I can't mend a ration. Last month the pens went three days on half bread because of one torn sail. Thin them out, and the pens eat properly.",
        'They come down with the lightning. Fight them between the flashes.'),
    'abq_old_thunderhead': (
        "There's one thunderbird bigger than the rest, grey round the beak, and the others follow it everywhere. The storm-keeper on the Storm Harvest, north-east of here, calls it Old Thunderhead. When it comes down, the whole flock comes with it. I've seen it go through a mainsail in one pass. Put it down, and the rest will scatter.",
        'It always comes down last. Wait for the flock, then look up.'),
    'abq_two_hundred_plates': (
        "Two hundred people, one pot and whatever the yard throws away. I cooked in a restaurant in Lahore for twenty years, and I've never been prouder of a stew than the ones I make out of nothing here. Every Cinder Ray out in the Ashwake, south-west of the pens, has a fillet on it that's half cooked from the inside already. The children in the pens ask me what I'm cooking every night, and I'd like to say something good. Bring me enough, and I'll feed the pens something they'll remember.",
        "Cut along the spine. The fillet comes away in one piece if you're gentle."),
    'abq_spice_from_the_stores': (
        "The conscripts eat scraps, and the soldiers eat well. Every Bastion Legionary on the apron round the citadel, north-west of the pens, carries a ration tin, and every tin has a twist of good spice in it. I can smell it on them when they walk past the pens. I haven't cooked with real spice since Lahore, and my hands miss it. Bring me the spice, and I'll share the bread with Siobhan's patients.",
        'The tins are on their belts, left side. They never check them.'),
    'abq_the_storm_misbehaves': (
        "These collectors were built to sip at the storms, a little at a time, and that's all they can take. I've kept them for forty years, since long before the Ascendancy came. Now they have them gulping, and every Harvested Storm that breaks loose wanders the rock throwing lightning about. The rock north-east of the fort is scorched black where they've walked. Calm them down the only way that works.",
        "Don't stand under the collectors while you fight. They'll drink you too."),
    'abq_collector_crystals': (
        "The crystals in the collectors are cracking under the strain, and the Ascendancy won't send new ones. Every Lightning Elemental on the rock grows a crystal inside itself, overcharged but sound. I can drain an overcharged crystal, but I can't grow one. Two of the collectors went dark last week, and the Ascendancy blamed me. Bring me those, and I'll set them in the collectors myself.",
        "Let the crystal stop crackling before you pick it up. It'll keep for days."),
    'abq_where_the_lightning_goes': (
        "I write down where every charge goes, because the old house taught me to. Half of it goes down into the citadel, to the foundry. The rest goes into the warships' engines, a little every day, more than a ship needs to fly. Take this ledger to Magister Orla Thessan at Dawnspear Wreck, south-west across the fort. She'll understand what it means.",
        "I've understood it for a month and I didn't want to. Let her be the one."),
}
