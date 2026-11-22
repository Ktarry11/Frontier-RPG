"""Azshara, Talrendis Landing and Timbermaw Hold in the giver's own voice (21 Nov 2026).

Kyle, 21 Nov 2026: "Azshara is doing that weird third person shit again with quests", then "make some kind of note that
doesnt have quests handed out in third person...and likely something else that has a story and aims for at least 5-6
sentences of coherant structure".

Every description is now the giver talking: who they are or what they've seen, what's wrong, why it matters to them,
and what to do and where, in five or six sentences. The accept line stays a short parting direction (under 200
characters, so the offer window keeps the description as the body). Story beats, names and directions are the ones
the zone already had; nothing new is revealed. The item starter (az_the_sea_side_dig) narrates to "you" on purpose and
is left alone.
"""

VOICE = {
    # ------------------------------------------------------------------ the road north, and the Landing
    "az_the_north_gate": (
        "Elder Torgun sealed this report himself, and it goes to Overseer Durgash Stonejaw at Talrendis Landing. "
        "Durgash runs Orgrimmar's half of the dig there, and the elves run the other half. The new gate out of the "
        "canyon north of the Valley of Honor opens straight onto Azshara, so it's not a long walk. The Warchief wants "
        "to know what the elves are pulling out of the ground, and he wants to know before they do. Keep the seal "
        "where nobody can see it until it's in Durgash's hands.",
        "Out the north gate and up through the forest. The Landing's on the point to the west.",
        None,
    ),
    "az_boar_for_the_mess": (
        "The mess hall's short of meat, and I've got a camp full of orcs who've been eating elf food for a week. The "
        "Conclave sends up bread so thin you can read through it, and our cook won't touch it. Dana runs the mess "
        "now, and she's from somewhere called the North Sea and can cook anything you put in front of her. The russet "
        "boars root all over the forest round the Landing, and they're fat this time of year. Bring me their haunches "
        "and I'll have a camp that can work a full shift again.",
        "The boars are thick in the trees all round the Landing. Bring the haunches back here and Dana will do the rest.",
        None,
    ),
    "az_wolves_on_the_road": (
        "The Autumn Timber Wolves have learned that the supply carts out of the Landing carry meat. They follow them "
        "through the forest now, and twice they've pulled a driver off the seat. Half my drivers are newcomers who'd "
        "never seen a wolf outside a picture before the Integration, and they're ready to quit. I need those wolves "
        "taught to stay off the road between here and the crossroads. Thin them out until the pack decides the carts "
        "aren't worth it.",
        "Autumn Timber Wolves run the forest between here and the crossroads. Thin them out.",
        None,
    ),
    "az_plumes_for_the_pillows": (
        "My brother and I ran a guesthouse on the Red Sea before the Integration, and I know what a decent bed looks "
        "like. The beds at the Landing are a disgrace, and the magisters remind me of it every morning at breakfast. "
        "The cliff hippogryphs on the Ursolan heights drop the best feathers I've ever seen, soft as anything I "
        "bought back home. They nest up on the cliffs north of here, and they don't give them up kindly. Bring me "
        "their plumes and I'll stuff pillows that even an elf won't complain about.",
        "The cliff hippogryphs nest up on the Ursolan heights, north of here. Bring me the plumes.",
        None,
    ),
    "az_ghosts_in_my_dreams": (
        "Half my guests dream the same street every night: a white marble boulevard running out into the sea, with "
        "people walking in it who never look at you. My brother Mohammed dreams it every single night, and he's sure "
        "it's the Drowned Promenade down on the east coast. I learned a long time ago to take his dreams seriously. "
        "I'd like to tell my guests it's a real place, or tell them it isn't, and either one would help them sleep. "
        "Go east past Stormwatch and down to the shore, and look at the people on that road.",
        "East, past Stormwatch and down to the shore. Tell me if there are people in it, and if they see you.",
        None,
    ),
    "az_two_lists": (
        "I keep a list of everything that comes out of the dig at the Ruins of Eldarath, and Magister Brightspire "
        "keeps another. They've never matched, not once in a month. Either somebody's lying or somebody's careless, "
        "and I can't tell which while I'm standing on one side of it. You've got no side yet, and that's worth "
        "something here. Eldarath's in Central Azshara, south of the lake and east of us, so walk the trenches and "
        "see what's lying in them. Tell me before you tell the elves.",
        "Eldarath's south of the lake, east of here. Walk the trenches and come back to me first.",
        None,
    ),
    "az_the_road_to_eldarath": (
        "The carts from the dig keep coming back light, and the drivers all say it's satyrs. Haldarr's rogues come "
        "down out of their encampment and cut the ropes while the carts are climbing, and the crates roll off into "
        "the trees. Half those drivers are newcomers from Earth, and they didn't sign on to fight satyrs on a hill. "
        "I want that road cleared, and I want the satyrs to know who cleared it. Their encampment's in the "
        "south-east of West Azshara, so go up there and make them regret every crate they've cut loose.",
        "Haldarr Rogues come down from the encampment in the south-east of West Azshara. Make them regret it.",
        "The carts came back full yesterday. Full, and the count still doesn't match the elves'.\n\nSo it isn't only "
        "the satyrs. Something else is taking from us.",
    ),
    "az_who_took_the_relic": (
        "The crews found a Highborne key in the trenches, gold and moonstone and as long as your arm. It was on both "
        "lists on Monday, and on Tuesday it was on neither. I think the elves have it, and the elves think I sold it, "
        "and we've stopped speaking about anything else. Dr. Okafor works for both of us and lies to neither, and "
        "she was in the trench when it came up. Take my tally down to her in the dig and ask her what she saw. I'll "
        "believe her, and so will Brightspire.",
        "Take my tally to Dr. Okafor. She's down in the dig, usually up to her knees in it.",
        None,
    ),
    "az_the_overseers_report": (
        "I've got a report for Orgrimmar that I don't want to write, and I've written it anyway. The relics are "
        "keys, the naga want them, and the palace they open is coming up out of the sea off our coast. Elder Torgun "
        "won't like it, and he'll think I've been sitting in the sun too long. He'll believe it from someone who's "
        "been down there and seen the naga's dig with their own eyes. Take it to him in Orgrimmar, and the north "
        "gate's the quickest way. Tell him everything you saw.",
        "Take it to Elder Torgun in Orgrimmar. The north gate's quickest.",
        None,
    ),
    "az_the_tidelord": (
        "I've got my orders from the Overseer, and I'm passing them to you because I can't swim. The naga in the "
        "Drowned Palace answer to Tidelord Vashj'ren, and his warriors are the ones who took the relic off our yard. "
        "He sits on a coral throne in the palace's flooded halls with the sea all round him. The palace door's at "
        "the head of the Drowned Court, off the East Azshara shore. Durgash wants the Warchief's answer delivered to "
        "that throne in person. Take a lot of friends, because he won't be alone down there.",
        "The palace door's at the head of the Drowned Court, off the East Azshara shore. Take plenty of friends.",
        None,
    ),
    "az_shades_in_the_trenches": (
        "My crews won't work the deep trenches at Eldarath after dark, and I can't blame them. The Highborne dead "
        "come up out of the ground at night looking for what was theirs, and they don't care whose shovel is in the "
        "way. Two of my diggers are from Earth, and they say back home the ghosts at least stayed in the stories. "
        "I need the Eldarath Shades put back down so the night shift can dig. They walk the ruins all round the "
        "dig, south of the lake in Central Azshara.",
        "The Eldarath Shades walk the ruins round the dig. They're dead already, so you won't feel bad.",
        None,
    ),
    "az_crab_season": (
        "I promised the dig crews a crab boil after the big lift, and now I've got to deliver it. Dana Whitfield "
        "cooked on a North Sea rig before the Integration, and she swears she knows how to do it properly. The "
        "shorecrabs on Southridge Beach are the size of shields, and I've seen them take a boot off a man. That "
        "beach is the south coast of Central Azshara, a fair walk from here. Crack the Southridge Shorecrabs open "
        "and bring me the meat, because Dana's already got the pot on.",
        "Southridge Beach is the south coast of Central Azshara. Bring the meat back here.",
        None,
    ),
    "az_cores_for_the_crane": (
        "The Conclave's crane at the dig runs on arcane cores, and the elves won't spare a single one for an orc "
        "lift. So my crews carry stone by hand while the crane sits there humming at them. I've noticed the Eldarath "
        "Constructs stomping round the ruins have cores of their own, bigger than the Conclave's. Break those "
        "constructs open near the dig and bring me what's inside them. The elves can't say no to a crane that runs "
        "on Highborne parts.",
        "The Eldarath Constructs stomp round the ruins near the dig. Bring me their cores.",
        None,
    ),
    "az_the_lost_crew": (
        "I sent one of my crews up the coast to Hetaera's Clutch to salvage a spire that washed up there. That was "
        "four days ago, and they haven't come back. The naga have a beachhead on the Clutch, and I should have known "
        "it before I sent anyone. Hetaera's Clutch is the headland past the Bay of Storms, in the north-east of "
        "Central Azshara. The Stormbay Tidehunters hold the beach, so break them and look for my people. I want my "
        "crew back, or I want to know.",
        "Hetaera's Clutch is past the Bay of Storms, north-east Central Azshara. Break the Tidehunters and look.",
        None,
    ),
    "az_hetaera": (
        "My crew went into Hetaera's Grotto under the Clutch, and nobody came out. The naga keep a hydra down there "
        "called Hetaera, and they feed her whatever they catch. I'm not sending another digger into that cave. The "
        "grotto's the sea cave in the crag on Hetaera's Clutch, and the hydra keeps to a deep pool off the second "
        "turn of the spiral. I want her dead before she eats anyone else. Take people with you, because a lot of "
        "heads means a lot of bites.",
        "The grotto's the sea cave in the crag on the Clutch. Hetaera's off the second turn of the spiral.",
        "So the hydra's dead, and I'm glad of it.\n\nI'll carve my crew's names on the crane. They lifted more than "
        "anyone, and they'd want it there.",
    ),
    "az_keepsakes_of_the_highborne": (
        "The Eldarath Shades are looking for things they lost: rings, combs, lockets, the small things people carry. "
        "Every one of them has a name cut into it, and the names are our history. The orcs call it robbing graves, "
        "and the newcomers on the crews call it archaeology. I call it the only record left of ten thousand years. "
        "The shades walk the ruins round the dig, so take what they carry and bring it to me. I'll write down every "
        "name, and then we'll all argue about it.",
        "The Eldarath Shades walk the ruins round the dig. Take what they carry.",
        "This one belonged to a scribe. This one belonged to a child.\n\nWe forget they were people. It's easier to "
        "dig them up when we forget.",
    ),
    "az_the_ravencrest_records": (
        "The monument at Ravencrest has the names of Highborne lords cut into it, and the Conclave wants a rubbing "
        "of every line. I'd do it myself, but the Ravencrest Shades don't let anyone that close. They still guard "
        "their lord's stone after all this time. It's in the middle of West Azshara, east of the Landing, and you "
        "can't miss it. Clear the shades round it and take the rubbing on the paper I gave you, not the cheap orc "
        "stuff.",
        "The monument's in the middle of West Azshara, east of the Landing. Clear the shades and take the rubbing.",
        None,
    ),
    "az_the_bound_magister": (
        "Haldarr's satyrs keep a Highborne magister bound in the far pocket of their den. They've kept him there "
        "for ten thousand years, and the Conclave wants him freed. I know what freeing him probably means after "
        "that long, and I'm asking you anyway. Haldarr Den is under the satyrs' encampment in the south-east of "
        "West Azshara, and he's in the farthest pocket off the taproot. Free him gently if you can. I don't think "
        "it'll be gentle.",
        "Haldarr Den is under the encampment in the south-east of West Azshara. He's off the taproot.",
        "So he's gone, and that means he's free.\n\nTen thousand years in chains, and he fought you for the chains. "
        "I'll write that down too.",
    ),
    "az_the_chamberlains_ledger": (
        "The Drowned Chamberlain keeps the palace's ledger in its flooded archive. It holds ten thousand years of "
        "who owed the queen what, and what she owed in return. I believe it's the most important book in the world, "
        "and I don't say that lightly. The archive's in the Drowned Palace's flooded halls, past the collapsed "
        "gallery. The Chamberlain won't lend it, so you'll have to take it from him. Please try not to get it any "
        "wetter than it already is.",
        "The archive's in the palace's flooded halls, past the collapsed gallery. Take the ledger off him.",
        None,
    ),
    "az_the_font": (
        "The leylines under this coast meet at the Mennar Font on Lake Mennar, and they've started pulling toward "
        "the sea. They've been restless since the Integration, but never like this. My instruments can tell me "
        "something's wrong, but they can't tell me which way. I need someone to stand in the Font and feel which "
        "way the water turns. Lake Mennar's in the south-west of Central Azshara, and the Font's on its north-east "
        "shore, ringed with crystal trees.",
        "The Font's on Lake Mennar's north-east shore. Stand in it, and you'll feel which way it pulls.",
        None,
    ),
    "az_wyrm_essence": (
        "The mana wyrms at Lake Mennar drink straight from the Font, so whatever's in the water is in them. Their "
        "essence holds a little of the leyline's pull, enough to measure once it's in glass. I want to know "
        "exactly what they've been drinking and how strong it's become. The Mennar Mana Wyrms swarm round the Font "
        "and the whole lake. Bottle what's in them and cork it fast, because it climbs the glass.",
        "The Mennar Mana Wyrms swarm round the Font and the lake. Bottle what's in them.",
        "Every vial leans toward the sea. Even the essence wants to go home.\n\nI was hoping I'd be wrong about this.",
    ),
    "az_the_blues_who_guard": (
        "The blue dragonflight guards the leylines at Lake Mennar, and has for longer than we've been keeping "
        "records. The Azure Dragonspawn won't let the Conclave's tappers anywhere near the Font. They aren't evil, "
        "they're just in the way, and I've tried talking until they stopped listening. I need the tappers in the "
        "water this week. The dragonspawn stand guard all round the lake, so drive them off the Font.",
        "The Azure Dragonspawn stand guard all round Lake Mennar. Drive them off the Font.",
        None,
    ),
    "az_azurewing": (
        "The dragonspawn answer to a blue drake called Azurewing, and she circles Lake Mennar every day. I'd much "
        "rather not fight a dragon, and I've said so to everyone who'd listen. But Azurewing has started burning "
        "the Conclave's tappers where they stand, and I keep those people alive. She hunts over the lake and lands "
        "at the Font when she's done. Be there when she lands, and dress warm, because she breathes frost.",
        "Azurewing hunts over Lake Mennar. When she lands at the Font, be there.",
        "I'm sorry it came to that. The blues were right to guard the Font. They just didn't know what was pulling "
        "at it.",
    ),
    "az_magistrix_elaria": (
        "Under the Drowned Palace there's a vault the sea never reached, and inside it waits a magistrix who never died. "
        "Magistrix Elaria the Undying keeps the cracked well at its heart, and it's her well the leylines are "
        "pulling toward. I keep the Conclave's wards, and they won't hold against that pull forever. Go down the "
        "flooded stair past the Tidelord's throne and into the Queen's Vault, and you'll find her at the well in the "
        "Arcanum. She drinks from it to heal, so hit her hard and don't stop.",
        "Down the flooded stair past the Tidelord's throne, into the Queen's Vault. She's at the well.",
        None,
    ),
    "az_pearls_with_runes": (
        "I've found the same rune on half the naga's pearls and on the Highborne stones in the dig. I dug Iron Age "
        "sites in Nigeria for twenty years, and I've never seen two peoples share a mark like this. Either they "
        "learned it from each other, or they both learned it from the same place. The Stormbay Sirens on the Bay of "
        "Storms carry those pearls. Bring me as many as you can, and don't wear them, because they sing.",
        "The Stormbay Sirens on the Bay of Storms carry the pearls. Don't wear them.",
        None,
    ),
    "az_the_relic_trail": (
        "There was seawater in the crate, and wet footprints across the yard that weren't orc or elf. I followed "
        "them down to the shore, where they went into the water. The naga raiding the Bitter Reaches have been "
        "trading Highborne gold up and down the coast, and I think our key went north with them. The Reaches are "
        "East Azshara's north coast, all wrecks and a naga shrine. One of the Bitter Reaches Raiders has our key, "
        "so find it and bring it home.",
        "The Bitter Reaches is East Azshara's north coast. One of the raiders has our key.",
        None,
    ),
    "az_tide_priestess": (
        "The naga's dig is run from Hetaera's Grotto by a sea witch called Tide-Priestess Sel'thira. She reads "
        "those runes better than anyone in the Landing, including me. I'd much rather sit down and talk with her, "
        "but she'd rather drown people. The grotto's under Hetaera's Clutch, and she keeps the drowned hall at the "
        "heart of the spiral. If she has notes, bring them to me, and if she doesn't, bring her down anyway.",
        "Sel'thira keeps the drowned hall at the heart of the grotto's spiral. Bring her notes.",
        None,
    ),
    "az_lady_ssiriss": (
        "The naga's siren queen is Lady Ssiriss, and she holds the court just inside the Drowned Palace's door. "
        "Every naga on this coast sings what she sings, and I'm sure now she's the one who wanted the keys. "
        "Everything we've chased up and down this shore goes back to her. Go through the Drowned Court's door and "
        "into the Siren's Court, where she sits on a coral dais in the pool. There's one fallen column out to her, "
        "and you mustn't listen when she sings.",
        "Through the Drowned Court's door into the Siren's Court. Don't listen to her sing.",
        None,
    ),
    "az_the_leylines_pull": (
        "The spirits of this coast are restless, and the leylines are dragging them toward the sea. They've been "
        "uneasy since the day the world changed, and the coast is the worst of it. The Tower of Eldara on East "
        "Azshara's northern cape still hums, and I think it's the only thing holding them back. The elves won't "
        "believe a shaman, but they might believe you. Go to the tower on the northern cape and stand at its foot, "
        "and listen.",
        "The tower's on the northern cape of East Azshara. If it's humming, it's holding. If it's quiet, run.",
        None,
    ),
    "az_imps_at_forlorn_ridge": (
        "The fel gate at Forlorn Ridge never quite closed, and the imps keep crawling out of it into the woods. I "
        "can hear the trees complaining from here, and they're right to. The imps set fires wherever they go, and "
        "they've already started on the oldest trees. Forlorn Ridge is in the south-west of Central Azshara, and the "
        "Forlorn Imps swarm round the gate. Burn them out before they burn the forest down.",
        "Forlorn Ridge is the south-west of Central Azshara. Burn the imps out of the trees.",
        None,
    ),
    "az_the_gate_that_wont_close": (
        "I want the gate at Forlorn Ridge shut for good, and that means dealing with the ones holding it open. The "
        "Legion left leftovers behind when it went: the Forlorn Eredar who keep the rite going, and the Forlorn "
        "Doomguard who guard them while they chant. Kill only one side and the other just finds new help. They're "
        "all up on the ridge round the gate. You've got to break both of them.",
        "Up on Forlorn Ridge, round the gate. Break the Eredar and the Doomguard both.",
        None,
    ),
    "az_gatekeeper_azgaroth": (
        "One doomguard still stands at the gate on Forlorn Ridge, and he's the one the Legion left in charge. His "
        "name's Gatekeeper Azgaroth, and as long as he stands that gate will open again. The rite's broken, but he "
        "could start it up in an afternoon. He keeps to the gate itself and won't leave it. He hits like a falling "
        "tree and burns like one too, so bring a healer.",
        "Azgaroth keeps the gate on Forlorn Ridge. Bring a healer.",
        None,
    ),
    "az_satyrs_on_the_road": (
        "I watch the road for satyrs, and lately the Haldarr Tricksters have been setting curses on it. A cart that "
        "drives over one goes round in circles in the woods until the driver cries. The carters are newcomers who'd "
        "never seen a satyr in their lives, and I've had three quit this week. The tricksters come down from their "
        "encampment in the south-east of West Azshara. Break their tricks, and then break them, because they're "
        "cowards when it's done to them.",
        "The Haldarr Tricksters come down from the encampment in the south-east of West Azshara.",
        None,
    ),
    "az_the_shadowcasters_of_legash": (
        "The curses on our road don't start with the Haldarr. They come from the satyrs' war camp at Legash "
        "Encampment, under the northern mountains. The Legash Shadowcasters teach them to the Haldarr, and the "
        "Haldarr carry them down to us. If I take the teachers away, the students forget. Legash is in the north of "
        "Central Azshara, and the shadowcasters keep to the tents round the throne.",
        "Legash Encampment's in the north of Central Azshara. The shadowcasters keep to the tents round the throne.",
        None,
    ),
    "az_warlord_sethrak": (
        "Warlord Seth'rak sits on the throne at Legash Encampment, under a Timbermaw totem the satyrs stole. He's "
        "noticed his shadowcasters are gone, and he'll send more. I want him off that throne before he can. The "
        "Timbermaw would very much like their totem back as well. His throne is at the heart of Legash, and he "
        "fights with a glaive that'll pin you to it if you let him.",
        "Seth'rak's throne is at the heart of Legash Encampment. Watch the glaive.",
        None,
    ),
    "az_valormok_burned": (
        "The satyrs burned Valormok to the ground a month ago, and I'm the only one of the watch still standing "
        "here. We built it three years ago, when the Integration opened the road north, and I helped raise every "
        "wall. The Haldarr Felsworn did the burning, and I watched them do it. They came down from their "
        "encampment to the east and went back up laughing. Go up there and burn them the way they burned us, and "
        "don't leave a tent standing.",
        "The Haldarr Felsworn came down from the encampment to the east. Burn them the way they burned us.",
        None,
    ),
    "az_vrexx_the_hornbreaker": (
        "The satyr who led the raid on Valormok is Vrexx the Hornbreaker. I watched him laugh while the tower came "
        "down, and I haven't stopped hearing it since. You've made a start on his felsworn, but he's the one who "
        "owes me. He keeps to the Haldarr Encampment, east of here. He's big and horned, with fel fire in both "
        "hands, so make him stop laughing.",
        "Vrexx is up in the Haldarr Encampment, east of here. Make him stop laughing.",
        "So he's dead, and I'm glad of it.\n\nI'll build the watchtower back myself, one log at a time.",
    ),
    "az_thunder_in_the_mere": (
        "The thunder lizards in the Sundering Mere have started coming up onto the Orgrimmar road. They lie across "
        "it in the sun like they own it, and the caravans won't run past them. I've watched a whole wagon turn "
        "round and go back to Orgrimmar rather than try. The Mere's south of here, east of the road, and the Mere "
        "Thunderhides wallow in the shallows. Drive them back into the water where they belong.",
        "The Sundering Mere's south of here, east of the road. Drive the Thunderhides back into the water.",
        None,
    ),
    "az_old_stormhide": (
        "The biggest thunder lizard in the Mere is Old Stormhide, and every caravan driver on this road has a story "
        "about it. I laughed at those stories until I saw it myself. It's twice the size of the others, and it "
        "leads them up onto the road. It wallows at the heart of the Sundering Mere. When it stamps the whole Mere "
        "shakes, so don't let it put you on your back.",
        "Old Stormhide wallows at the heart of the Sundering Mere. Don't let it put you on your back.",
        None,
    ),
    "az_raiders_of_the_reaches": (
        "The naga on the Bitter Reaches strip every wreck that washes up on East Azshara's north coast. That was "
        "their business until lately, when they started on the Horde's supply boats too. Captain Zarga at "
        "Stormwatch has asked the Landing for help, and I'm sending you. The Reaches are the north coast, with "
        "wrecks everywhere, and the raiders work every one of them. They'll fight you for the wrecks, so let them.",
        "The Bitter Reaches is the north coast. The raiders work the wrecks and they'll fight you for them.",
        None,
    ),
    "az_the_wavecallers": (
        "The raiders don't wreck my boats themselves, they haven't got the strength for it. The Bitter Reaches "
        "Wavecallers call up the waves that do it, singing from the naga shrine on the Reaches. I've lost two boats "
        "this month to a sea that was flat an hour before. The shrine's on the north coast, among the wrecks. Shut "
        "the wavecallers up, and the sea will calm.",
        "The Bitter Reaches Wavecallers sing from the shrine on the north coast. Shut them up.",
        None,
    ),
    "az_captain_ssarith": (
        "The raiders answer to Captain Ssarith, a naga who sails a stolen Kul Tiran hull up and down my coast. She "
        "takes my cargo and laughs at my crews from the deck. I want the captain dead, and I want that hull, because "
        "it's a better ship than anything I've got. She holds the biggest wreck on the Bitter Reaches. She fights "
        "with a trident made from a ship's anchor, so don't let her hook you.",
        "Ssarith holds the biggest wreck on the Bitter Reaches. Don't let her hook you.",
        None,
    ),
    "az_the_temple_guard": (
        "The naga have taken the Temple of Zin-Malor on the southern headland and filled it with guards. Raiders I "
        "understand, because they want my cargo. A temple full of soldiers is something else, and I want to know "
        "what they're protecting. The temple's on the southern headland, and the Zin-Malor Wardens hold the steps. "
        "Break the guard and see what's under it.",
        "The Temple of Zin-Malor's on the southern headland. The Wardens hold the steps.",
        None,
    ),
    "az_high_priestess_nazeth": (
        "Under all those guards is a door going down, and the naga are digging a tunnel from it. The temple's high "
        "priestess, Naz'eth, is the one who ordered it dug. I don't know where it goes, and I don't want to find out "
        "by having naga come up under Stormwatch. I want it to stop with her. She keeps the heart of the Temple of "
        "Zin-Malor, and she'll flood the floor under you, so don't stand still.",
        "Naz'eth keeps the heart of the Temple of Zin-Malor. Don't stand still.",
        None,
    ),
    "az_the_court_dead": (
        "The sea came up over Quel'Thalas's coast the day the world changed, and the Conclave has been looking for "
        "a shore ever since. Out here we found a whole court of our own dead. The Drowned Court is full of "
        "Highborne who think it's ten thousand years ago, and the Court Sentinels still guard the streets for a "
        "queen who isn't there. Go out along the causeway from the Promenade to the Drowned Court. Let the "
        "sentinels rest, because they've stood watch long enough.",
        "Out along the causeway from the Promenade to the Drowned Court. Let the sentinels rest.",
        None,
    ),
    "az_seals_of_the_court": (
        "Every Promenade Noble still carries the seal of their office, and the Conclave can read the names on them. "
        "The sea takes a little more of that road every year, and when it goes the names go with it. I want them "
        "written down before that happens. The nobles walk the marble road into the sea, east of here. Take their "
        "seals gently if you can, because they were somebody once and they don't know they've stopped.",
        "The Promenade Nobles walk the marble road into the sea, east of here. Take their seals gently.",
        None,
    ),
    "az_the_weeping_duchess": (
        "One of the names on those seals is a duchess who drowned waiting for her husband to come back from the "
        "palace. She's still waiting, and the other ghosts follow her through the streets. While she walks, none "
        "of them will rest. The Weeping Duchess keeps to the heart of the Drowned Court. Her grief's a weapon, so "
        "don't let her hold you.",
        "She walks the heart of the Drowned Court. Don't let her hold you.",
        None,
    ),
    "az_eldaras_guardians": (
        "The Tower of Eldara on the northern cape still hums, and it's the reason the leylines haven't torn this "
        "coast apart. I want to know how it works before it stops working. The Eldara Arcane Guardians won't let the "
        "Conclave anywhere near it. They walk the tower's foot on the northern cape. Break enough of them and the "
        "door should open for you.",
        "The tower's on the northern cape. Break enough Arcane Guardians and the door should open.",
        None,
    ),
    "az_magus_valethion": (
        "The tower's keeper is a Highborne magus who never left, Magus Valethion, and the whole tower answers to "
        "him. He still thinks he's in charge of a kingdom that drowned. I want the tower to answer to the Conclave "
        "instead, so we can keep it holding. He's inside the Tower of Eldara. He'll ward himself when he's hurt, so "
        "break the ward first and then break him.",
        "Valethion's inside the Tower of Eldara. Break the ward, then him.",
        None,
    ),
    # ------------------------------------------------------------------ Timbermaw Hold
    "az_hippogryphs_on_the_pass": (
        "The cliff hippogryphs on the Ursolan heights have started diving at anyone who climbs the pass to the Hold. "
        "My gate's full of furbolgs too scared to go down for supplies, and the stores are getting thin. The Hold's "
        "had more visitors since the Integration than in the hundred years before it, and the hippogryphs don't like "
        "any of them. They nest along the Ursolan pass, just below the gate. Bring a few of them down and the rest "
        "will learn to keep their distance.",
        "The Cliff Hippogryphs nest along the Ursolan pass, below the gate. They're clever birds, and they'll learn.",
        None,
    ),
    "az_the_shadowsong_dead": (
        "The Timbermaw and the night elves of Shadowsong Shrine kept the peace in these woods for a long time. "
        "When the Sentinels died they never left their shrine, and now they don't know friend from foe. I've lost "
        "two walkers to people I used to share a fire with. Shadowsong Shrine is east of the Hold, in the trees of "
        "West Azshara's north-east. Lay them to rest kindly, and say a word for them if you can.",
        "Shadowsong Shrine's east of the Hold, in West Azshara's north-east. Let them go kindly.",
        None,
    ),
    "az_heartwood_for_the_spring": (
        "I keep the Hold's spring clean with heartwood charms, and the old charms have started going dark. A charm "
        "lasts a year when the water's healthy, and these have lasted a month. Something's wrong with the spring, "
        "but first I need charms that can stand up to it. The autumn treants in the woods of West Azshara grow the "
        "best heartwood there is. Bring me some and I'll carve new ones.",
        "The Autumn Treants walk the woods all over West Azshara. They'll give up their heartwood if you insist.",
        None,
    ),
    "az_the_spring_goes_green": (
        "The new charms went dark in a day, and that's never happened in my lifetime. Something's coming up into "
        "the spring from below, and it's turning the bottom of the pool green. I've seen that same green in the "
        "water at the Sundering Mere, and I'm afraid it's spreading. The Mere's in the south-east of West Azshara. "
        "Look at the water near the reeds, and tell me if it's green at the bottom.",
        "The Sundering Mere's in the south-east of West Azshara. Look at the water near the reeds.",
        None,
    ),
    "az_sporecloud_samples": (
        "Down past the deep gate the air itself has gone rotten, and I want to know what's in it. If I know what "
        "it's made of, I can make a charm that keeps it out of my spring. The Drifting Sporeclouds in the Rotroot "
        "Deeps are made of the stuff, and bursting them seems to kill it. They float through the Sporegarden under "
        "the Hold. Breathe through a cloth while you're down there.",
        "The Drifting Sporeclouds float through the Sporegarden under the Hold. Breathe through a cloth.",
        None,
    ),
    "az_dreamfoil_for_the_healers": (
        "The Hold's healers are running out of dreamfoil, and the herbs on the Ursolan slopes have gone brown. The "
        "newcomers who climb the pass bring sicknesses our healers have never seen, and dreamfoil's the only thing "
        "that helps with most of them. I need fresh leaves from lower down, where the ground's still soft. It grows "
        "all over West and Central Azshara. Pick it fresh, and leave anything brown at the edges.",
        "Dreamfoil grows all over West and Central Azshara where the ground's soft. Leave the brown leaves.",
        None,
    ),
    "az_golden_sansam": (
        "Golden sansam is what our healers use for rot fever. Since the spring went green there's been a lot more "
        "rot fever, and I'm down to the last jar. Every family in the Hold has someone coughing. It grows in the "
        "forest across Azshara, mostly near water. Dig up the whole root, because it's no good without it.",
        "Golden sansam grows in the forest across Azshara, mostly near water. Dig the whole root.",
        None,
    ),
    "az_a_totem_for_valormok": (
        "I heard the satyrs burned out the watch at Valormok, and that one orc stayed when the rest were gone. The "
        "Timbermaw give a totem to anyone who holds a gate alone, and I've carved him one. It's small, but it's "
        "good wood and it'll last longer than the satyrs will. Valormok's down the road to Orgrimmar, south of the "
        "crossroads. Give it to the grunt there, and tell him the Hold knows what he did.",
        "Valormok's down the road to Orgrimmar, south of the crossroads. Tell him the Hold knows what he did.",
        None,
    ),
    "az_the_stolen_totem": (
        "The satyrs at Legash stole a Timbermaw totem when they came through the Ursolan pass. I carved that totem "
        "myself when I was young, and they stood it over their warlord's throne like a trophy. The warlord's dead "
        "now, but his satyrs are still sitting under it. Legash Encampment is under the northern mountains in "
        "Central Azshara. Break the satyrs between you and the throne and bring my totem home, it's the one with "
        "the bear on it.",
        "Legash Encampment's under the northern mountains. The totem's the one with the bear on it.",
        None,
    ),
    "az_samples_from_haldarr": (
        "I was a soil scientist back home in Tromso, and I've been taking samples from round the Hold since the "
        "spring went green. The rot isn't random, it's coming from somewhere, and I think I can trace it. The worst "
        "readings I've had are downhill from the satyrs. I need soil from right under their encampment, in the "
        "south-east of West Azshara over the den. Take it from under the tents and be quick, because they won't "
        "like it.",
        "The Haldarr Encampment's in the south-east of West Azshara. Take a sample from under the tents.",
        None,
    ),
    "az_samples_from_legash": (
        "If the Haldarr satyrs are feeding the rot, I'd bet the Legash camp is too. I need to prove it before I "
        "take this to the Elder, because a guess won't open a gate. The Legash Felhounds dig under the tents all "
        "day, and what's under their paws is exactly what I need. Legash Encampment's in the north of Central "
        "Azshara. Bring me what they're digging in.",
        "Legash Encampment's in the north of Central Azshara. Bring me what the felhounds dig in.",
        None,
    ),
    "az_tell_the_elder": (
        "I've got samples from the Mere, from Haldarr and from Legash, and they all say the same thing. The rot runs "
        "downhill from the satyrs' camps, and it all ends under the deep gate in the Hold's floor. I've written it "
        "plainly, with every number. The Elder should hear it from someone the Hold trusts, and that's you more than "
        "me. Take this to him, and when he asks if it's true, tell him what you've seen.",
        "Take these to the Elder. He'll ask you if it's true, and you've seen it.",
        None,
    ),
    "az_who_feeds_it": (
        "The rot spreads fastest where the satyrs work it. I've watched the Haldarr carry it into the woods on their "
        "blades, and the readings jump wherever they've been. Fewer satyrs means a slower rot, and that's time the "
        "Hold needs. The Haldarr Felsworn tend the fel fires in the encampment over the den, far to the south-east "
        "in West Azshara. Put the fires out, and the ones who tend them, and don't breathe the smoke.",
        "The Felsworn tend the fel fires in the Haldarr Encampment. Don't breathe the smoke.",
        None,
    ),
    "az_the_ursolan_totems": (
        "The totems along the Ursolan pass mark the Timbermaw's road, and I can feel each of them from the Hold. One "
        "of them has gone quiet, and I can't tell which from up here. A quiet totem means something's wrong with "
        "the wood, and the road isn't safe past it. The pass runs down from the Hold's gate into West Azshara. Walk "
        "it to the bottom, and the quiet one will feel cold when you pass it.",
        "The pass runs down from the Hold's gate into West Azshara. The quiet one will feel cold.",
        None,
    ),
    "az_satyrs_at_haldarr": (
        "Haldarr's satyrs knock down every Timbermaw totem they find. I've carved enough replacements this season "
        "to build a second Hold, and my hands are tired. I'd rather the satyrs stopped. The Haldarr Tricksters run "
        "the curses at their encampment, far to the south-east in West Azshara, and they love knocking totems over. "
        "Show them how it feels to be knocked over.",
        "The Haldarr Tricksters run the curses at the Haldarr Encampment, far to the south-east.",
        None,
    ),
    "az_haldarr_the_hornlord": (
        "The satyrs' lord, Haldarr, lives in the hollow at the top of the den under his encampment. Every satyr in "
        "West Azshara answers to him, and every totem they've broken was broken on his word. It ends with him. "
        "Haldarr Den's under the encampment in the south-east of West Azshara, and you climb the taproot to his "
        "hollow. He'll pin you to the tree if you let him.",
        "Haldarr Den's under the encampment. Climb the taproot to his hollow.",
        None,
    ),
    "az_orgrimmars_hand": (
        "I've been the Warchief's man in the Hold for three years, since the tunnel opened. The Hold and the Landing "
        "ought to be talking, and they aren't. The elves don't come up the mountain, and the furbolgs don't go down "
        "it. I've written a letter to Overseer Durgash, and I want it in his hand. Take it down to the Landing, "
        "where he'll be on the high ground watching the dig.",
        "Take it down to the Landing. Tell him the furbolgs are better neighbours than the elves.",
        None,
    ),
    "az_boars_for_the_hold": (
        "The furbolgs eat honey, roots and fish, and they're very generous with all three. I haven't had a proper "
        "piece of meat in a month, and I'm starting to dream about it. The russet boars root all over West "
        "Azshara's woods, and I can hear them from the gate. Bring me their haunches. I'll roast them out back where "
        "the furbolgs can't see.",
        "The Russet Boars root all over West Azshara's woods. Bring me the haunches.",
        None,
    ),
    "az_word_down_the_tunnel": (
        "The Timbermaw in the tunnel above Felwood need to hear about the rot under the Hold. The Deadwood drank "
        "the same thing, and we always told ourselves they were just unlucky. The tunnel's far mouths came down the "
        "day the world changed, and the Felwood one's the only one still open. Go out the Hold's west door and "
        "along the East Passage into the tunnel. Pathfinder Grosk is in the Lower Galleries, watching Felpaw, and "
        "he needs to hear it's the same rot.",
        "Out the Hold's west door and along the East Passage. Grosk's in the Lower Galleries.",
        None,
    ),
    "az_open_the_deep_gate": (
        "I've decided, and the Hold will have to live with it. We sealed the deep gate in the basin floor to keep "
        "the rot out, and now it's coming up anyway. I'll open it, and I need someone to go down first. The first "
        "thing waiting below is Old Mossjaw, our own chieftain, the first the rot took. The wardens will open the "
        "gate for you, south of here, and he lies on his bier at the end of the burial halls. Put him to rest, "
        "because he was a good chieftain.",
        "The deep gate's in the basin floor, south of here. Mossjaw lies at the end of the burial halls.",
        None,
    ),
    "az_xavras_the_gloomtender": (
        "At the bottom of the deeps, on an island in the fel lake, is the satyr who planted the rot. Her name is "
        "Xavras the Gloomtender, and everything the Hold has lost started with her. Our spring, our chieftain, our "
        "shamans, all of it. She's through the deep gate south of here, on her throne island in the Gloomhollow, "
        "with one causeway out to her. At the end she'll bring the rot up out of the lake, so don't be standing in "
        "it.",
        "She's at the bottom of the Rotroot Deeps, on her island in the Gloomhollow. Don't stand in the rot.",
        None,
    ),
    "az_what_the_satyrs_were": (
        "The furbolgs remember what the elves would rather forget. The satyrs were Highborne once, Azshara's own "
        "court, before they gave themselves to the Legion. The rot is their magic gone bad, and it's been sitting "
        "under our feet for ten thousand years. The Conclave should hear that, and they should hear it from me. "
        "Take this to their archivist at the Landing, and let him read it before he argues.",
        "Take this to the Conclave's archivist at the Landing. Let him read it first.",
        None,
    ),
    "az_echo_of_the_queen": (
        "At the bottom of the Drowned Palace, in front of an empty throne, something made of moonlight and water is "
        "waiting in the queen's shape. The Overseer and I agree on one thing, and we've agreed on very little. "
        "Whatever's in that vault, nobody gets it, not Orgrimmar and not the Conclave. Go through the palace and "
        "down into the Queen's Vault, past the well, to the throne room. She'll call her court, and then she'll "
        "call the sea, so go with everyone you trust.",
        "Through the palace into the Queen's Vault, past the well, to the throne room. Go with everyone you trust.",
        None,
    ),
    "az_down_the_deep_gate": (
        "I've stood on the deep gate for three years, listening to the Hold's dead walk around under it. Now it's "
        "open, and I can hear them better. The Rotroot Furbolgs were our people once, and some of them were my "
        "friends. I want them quiet. Go down the gate stair into the burial halls and put them down, and don't hate "
        "them for what they've become.",
        "Down the gate stair into the burial halls. Don't hate them for what they've become.",
        None,
    ),
    "az_mother_sporeheart": (
        "Past the burial halls the floor has gone to fungus, and the thing that grows it sits on an island in the "
        "middle. We call her Mother Sporeheart, and I'm sure the spores in our spring come from her. Lessa hasn't "
        "slept properly in a month for worrying about it. She's on the big island in the Sporegarden, past the "
        "first slope. Kill the clouds she makes first, then kill her.",
        "She's on the big island in the Sporegarden, past the first slope. Kill the clouds, then her.",
        None,
    ),
    "az_rotwarden_kazthul": (
        "The satyrs keep cages down there, a long hall of them, and the one with the keys is Rotwarden Kaz'thul. "
        "I've heard those cages from the gate, at night when the Hold's quiet. Some of what's in them used to be "
        "furbolg. The Warden's Gauntlet is the long hall past the Sporegarden, and he's at the far end. He'll cage "
        "you, and then he'll open the other cages.",
        "The Warden's Gauntlet is past the Sporegarden. Kaz'thul's at the far end.",
        None,
    ),
    "az_thornblight": (
        "Under the cages is a cathedral the roots made, and those roots are the Hold's own. They grew down into the "
        "rot and came back wrong, as something we call Thornblight. Thornblight is holding the whole hall up, and "
        "I don't know what happens to the Hold above if it falls. Go down past the gauntlet into the Root "
        "Cathedral, where the floor's a fel lake and the roots are the only bridges. It's on the middle knot, and "
        "when it's dying it'll try to bring the roof down.",
        "Down past the gauntlet into the Root Cathedral. Thornblight's on the middle knot.",
        None,
    ),
    "az_the_rotroot_mystics": (
        "The Hold's own shamans went down after the rot years ago, and they never came up. My teacher went with "
        "them. Now they're down there as Rotroot Mystics, healing the rot the way they used to heal the Hold. "
        "They walk the burial halls and the Sporegarden. They'll heal the others, so kill them first.",
        "The Rotroot Mystics walk the burial halls and the Sporegarden. Kill them first.",
        None,
    ),
    "az_the_rot_tenders": (
        "The satyrs who tend the rot keep it fed, and as long as they're feeding it the Hold can't win. I want every "
        "Satyr Rot-Tender in the deeps dead before our people go down to the lake. They work the gauntlet and the "
        "cathedral. They heal each other when they stand together. Don't let them stand together.",
        "The Satyr Rot-Tenders work the gauntlet and the cathedral. Keep them apart.",
        None,
    ),
    "az_what_our_ancestors_did": (
        "I've read the Chamberlain's ledger, and I've read the Elder's word, and they say the same thing. The rot is "
        "Highborne magic, and the satyrs are what the court became. The Conclave has to say so to the Hold, out "
        "loud and in writing. The Grand Magister wrote this herself, and I'd like it carried by someone who isn't "
        "an elf. Take it up to the Elder at Timbermaw Hold.",
        "Take it up to the Hold. It isn't an apology. We'd need a longer page for that.",
        None,
    ),
    "az_the_moonguard_revenant": (
        "My brother Mohammed dreams of a knight under the sea whose spirit won't rest. Farseer Thrag says the dream "
        "is true, and I've stopped arguing with either of them. The knight swore an oath to a queen who isn't "
        "coming back, and he's still keeping it. The Moonguard Revenant holds the processional in the Queen's "
        "Vault, down the flooded stair. It'll put up its shield and then charge, so let it go.",
        "Down the flooded stair into the Queen's Vault. The Revenant's at the end of the processional.",
        None,
    ),
}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/azshara_story.py.
from voice.azshara_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])


from voice.azshara_beats import BEATS as _BEATS
for _qid, _a in _BEATS.items():
    _o = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_o[0], _a, _o[2])
