"""
Tempest Shallows (52-55) and Khaz Varun, the Black Hollow. Thirty-five quests.

Read by tools/build_tempest_quests.py. See that file for the rules these are held to.

WHAT THIS HALF OF THE ISLAND IS ABOUT. You come off a boat onto a jetty where everything has been
carried up by hand. The landing's work is ordinary and physical: feed the camp, keep the road
open, find out why the barges keep sinking. Under it are two longer things:

  THE GATE (11)     Khaz Varun went dark four generations ago and the people who walk in now come
                    out wrong, or camp in the forecourt and never leave. Bron counts them. The
                    Thane's three quests go down through the city to the thing sitting in his
                    great-grandfather's chair, and the dungeon's other work is given in Cinderwharf
                    by the people who each want something different out of the same hole.
  THE STEEL SHIP (2) A murloc drops a ship's log written in English. It starts a quest that ends
                    with the landing's doctor, who is from Mombasa, reading the crew list.

EVERYONE WHO GIVES A QUEST ABOUT A PLACE STANDS SOMEWHERE ELSE. The two people in the Green Belt
send you to the gate and the slope; the Green Belt's own work is given at the landing.
"""
from tools.tempest_quest_kit import (  # noqa: F401
    TS, CW, KV, Q, k, boss, explore, deliver, talk, carry, fetch,
    GREKKA, DURN, PIM, HALLA, IMANI, ROZZ, BRON, HESTA, TEODORA, JEX,
    THANE, MORN, NIX, TAZZ, BRENNA, THORA, PELL, SKEZZ)

#: (item_id, name, description) drops three times in four; a fourth value overrides the rate,
#: which is only used for the one thing a boss carries.
FETCH_DROPS = {
    "Bargebreaker Crab": [
        ("tmp_crab_claw", "Bargebreaker Claw", "As long as a forearm and full of sweet meat."),
        ("tmp_jex_boot", "Goblin Sea Boot", "A small tarred boot with a brass toe. It's been "
                                            "chewed, and it's still in better shape than most."),
    ],
    "Ashfur Gorilla": [
        ("tmp_bitterbark", "Chewed Bitterbark", "A wad of grey bark, chewed soft. The gorillas "
                                                "pack it on their burns."),
    ],
    "Shallows Snapper": [
        ("tmp_snapper_fat", "Snapper Fat", "Clean white fat from under the shell. It doesn't "
                                           "go rancid in the heat."),
    ],
    "Wreckpicker Murloc": [
        ("tmp_wreck_timber", "Seasoned Wreck Timber", "Oak that's been under salt water for "
                                                      "years. It's harder than the day it "
                                                      "was cut."),
        ("tmp_cargo_cask", "Sealed Cargo Cask", "Small, heavy and still sealed with pitch. "
                                                "Something inside it shifts."),
        ("tmp_discharge_book", "Seaman's Discharge Book",
         "A small stiff booklet with a photograph inside the cover and stamps from ports "
         "that aren't on any map here."),
    ],
    "Gate-Squatter Brawler": [
        ("tmp_supply_crate", "Ashclaim Supply Crate", "Stencilled with the Ashclaim's mark "
                                                      "and a jetty tally number."),
    ],
    "Gate-Squatter Ashpreacher": [
        ("tmp_ash_tablet", "Ash-Prayer Tablet", "A slate rubbed grey with ash. The same line "
                                                "is scratched into it over and over."),
    ],
    "Rubble Basilisk": [
        ("tmp_gizzard_stone", "Basilisk Gizzard Stone", "A pebble polished in a basilisk's "
                                                        "gut. This one has a silver streak."),
    ],
    # ---- inside Khaz Varun
    "Crazed Miner": [
        ("tmp_black_dust", "Pouch of Black Dust", "Fine as flour and black as a chimney. "
                                                  "It clings to the cloth."),
    ],
    "Ash-Wretch": [
        ("tmp_name_tablet", "Ashhold Name-Tablet", "A thumb of iron with a name punched into "
                                                   "it. Every Dark Iron of Khaz Varun "
                                                   "carried one."),
    ],
    "Masked Zealot": [
        ("tmp_zealot_mask", "Zealot's Iron Mask", "Riveted shut at the back. Whoever wore it "
                                                  "didn't mean to take it off."),
    ],
    "The Crusher": [
        ("tmp_stonecast_plate", "Stonecast Breastplate",
         "Dented, black with soot and unmistakably fine work. There's a maker's mark under "
         "the left arm.", 1.0),
    ],
    "Overseer Grall": [
        ("tmp_roll_of_oaths", "Roll of Oaths", "A scroll of thin iron leaves on a ring. Every "
                                               "leaf is a name and a promise.", 1.0),
    ],
}
STARTER_DROPS = {
    "Gate-Squatter Brawler": [("tmp_pay_chit", "Ashclaim Pay Chit",
                               "A brass tag from the landing stores, stamped with a porter's "
                               "number. A squatter was wearing it on a string.", 0.22)],
    "Wreckpicker Murloc": [("tmp_ships_log", "Waterlogged Ship's Log",
                            "A hardbound book swollen with sea water. The writing is in ink, "
                            "in a language the dwarves and goblins don't read.", 0.22)],
}
STARTER_IDS = {"tmp_pay_chit": "tmp_pay_chit", "tmp_ships_log": "tmp_the_ships_log"}


def build():
    q = []

    # ================= THE LANDING'S WORK =================
    q.append(Q("tmp_off_the_boat", "Off the Boat", GREKKA, 52, 52, "landing",
               "Carry the boat's manifest from Bosun Grekka to Quartermaster Durn at Ashclaim "
               "Landing.",
               [deliver("tmp_manifest", "the boat's manifest, to Quartermaster Durn")],
               "You're the first one off who isn't carrying a crate, so you can carry this "
               "for me.\n\nIt's the manifest for the boat you came in on. Quartermaster Durn "
               "won't release a thing from the stores until he's checked it against what was "
               "landed, and I can't leave the jetty while there's a hull tied to it.\n\nHe's "
               "just along the shore to the south-east, under the big awning with all the "
               "barrels. Tell him the count's right this time.",
               "She says the count's right, does she? I'll believe that when I've counted "
               "it myself.\n\nYou're new off the boat, so I'll tell you how this place "
               "works. Everybody here has a job that's bigger than they are, and most of "
               "them will pay you to take a piece of it. Ask around the landing before you "
               "go anywhere near that gate.",
               turn_in_npc_id=DURN,
               grant_items=carry("tmp_manifest", "Boat's Manifest",
                                 "Four pages of cargo in Grekka's square hand, with a tar "
                                 "thumbprint on every one.")))

    q.append(Q("tmp_teeth_on_the_trunk_road", "Teeth on the Trunk Road", GREKKA, 52, 52,
               "greenbelt",
               "Kill Greenbelt Raptors and Canopy Panthers in the Green Belt, east of Ashclaim "
               "Landing.",
               [k("Greenbelt Raptor", 10, TS), k("Canopy Panther", 8, TS)],
               "Nobody could land on this island at all until the sea route opened three years ago, and now everything we land has to go east along the trunk road, and the trunk "
               "road goes straight through the Green Belt.\n\nThat's the jungle you can see "
               "from the jetty. The Greenbelt Raptors hunt the road in packs, and the Canopy "
               "Panthers wait in the trees over it and drop on whoever's last in the line. "
               "I've stopped sending porters out in groups smaller than six.\n\nGo east "
               "along the road until the trees close over you, and kill whatever comes at "
               "you. I'd like to send a cart out tomorrow without writing a will first.",
               "The porters who came back this afternoon said they didn't see a single "
               "raptor on the road.\n\nOne of them was almost disappointed. He'd sharpened "
               "a boathook specially. Take this from the jetty stores, and thanks for "
               "making my morning easier."))

    q.append(Q("tmp_the_road_to_the_wharf", "The Road to the Wharf", GREKKA, 54, 54, "ashclaim",
               "Carry the jetty tally to Harbourmaster Skezz in Cinderwharf, on the north-east "
               "shore of the island.",
               [deliver("tmp_jetty_tally", "the jetty tally, to Harbourmaster Skezz in "
                                           "Cinderwharf")],
               "You've been useful here, so I'm going to send you somewhere with a roof.\n\n"
               "The town's called Cinderwharf and it's on the far side of the volcano. "
               "Harbourmaster Skezz runs the berths there, and she needs my tally of every "
               "barge that's left this jetty since spring. Four of them never arrived at her "
               "end and she wants to know which four.\n\nTake the trunk road east through "
               "the Green Belt, then follow the east road north round the foot of the "
               "mountain into the Ashen Reach. Keep going north along the shore and you'll "
               "come to the town gate. It's rougher country up there than this, so don't "
               "go until you're ready for it.",
               "This is Grekka's tally, and it's exactly as bad as I thought it would be.\n\n"
               "Four barges left her jetty loaded and none of them tied up at mine. That's "
               "ore, hulls and crews, and the Underwriter has started asking whether I can "
               "count.\n\nYou walked here through the Reach, so you can handle yourself. "
               "I've got work for somebody like that.",
               nxt="tmp_four_barges", turn_in_npc_id=SKEZZ,
               requires_quests=["tmp_off_the_boat"],
               grant_items=carry("tmp_jetty_tally", "Jetty Tally",
                                 "A roll of oilcloth listing every barge that left Ashclaim "
                                 "Landing, with four names circled.")))

    q.append(Q("tmp_crab_for_the_pot", "Crab for the Pot", HALLA, 52, 52, "landing",
               "Collect Bargebreaker Claws from Bargebreaker Crabs in the Tempest Shallows, "
               "east of Ashclaim Landing.",
               [fetch("tmp_crab_claw", 8)],
               "I've got forty people to feed and the supply boat brought me flour, salt "
               "and a letter of apology.\n\nThere's good eating in the shallows if you can "
               "get it out of its shell. The Bargebreaker Crabs out there are the size of a "
               "handcart, and each claw feeds a table. They're also bad tempered, which is "
               "why I'm asking you and not going myself.\n\nFollow the trunk road east and "
               "take the strand road down to the water. The whole bay's shallow enough to "
               "wade. Bring me the claws and I'll have them in the pot before dark.",
               "Those are beautiful, and there's enough here for two nights.\n\nSit down "
               "and I'll crack one for you while it's hot. You can take this as well. "
               "Somebody left it in the long tent and never came back for it."))

    q.append(Q("tmp_carried_up_by_hand", "Carried Up by Hand", DURN, 53, 53, "landing",
               "Kill Gate-Squatter Brawlers in the forecourt of Khaz Varun's Gate and take back "
               "the Ashclaim Supply Crates they stole.",
               [k("Gate-Squatter Brawler", 10, TS), fetch("tmp_supply_crate", 5)],
               "I've lost crates off the ruin road three nights running, and I know exactly "
               "who's got them.\n\nThere are dwarves camped in the forecourt of Khaz Varun's "
               "Gate, just south-east of here where the road ends in rubble. They went into "
               "the city at some point and they came out wrong. They don't talk sense and "
               "they don't leave. The big ones, the Gate-Squatter Brawlers, come up the road "
               "at night and carry off whatever my porters set down.\n\nI want my crates "
               "back. You'll have to go through the Brawlers to get them, and I won't "
               "pretend I'm sorry about that.",
               "Every one of these has my tally number on it, and two of them haven't even "
               "been opened.\n\nI don't think they wanted what was inside. I think they "
               "just wanted to be carrying something. That bothers me more than the "
               "stealing did.\n\nHere's something for your trouble out of a crate they "
               "didn't get."))

    q.append(Q("tmp_mother_canopy", "The Last in the Line", DURN, 53, 53, "greenbelt",
               "Kill Mother Canopy, the great panther that hunts the trunk road in the Green "
               "Belt.",
               [boss("Mother Canopy", TS)],
               "I've lost three porters this month, and it was the last one in the line "
               "every time.\n\nThe others never hear a thing. They get to the far end of "
               "the Green Belt, they turn round to count heads, and they're one short. The "
               "woodcutters say it's a panther twice the size of the rest, and they call "
               "her Mother Canopy because the others seem to be hers.\n\nShe hunts the "
               "trunk road where it runs under the thickest trees, east of the landing. "
               "She's hard to find, but she seems to come out for people who are looking "
               "for her. I'd like her dead before I've got to promote somebody to the back "
               "of the line again.",
               "You've brought me her hide, and it's bigger than my awning.\n\nI'm going to "
               "hang it over the stores where the porters can see it. They've been walking "
               "that road backwards for a month.\n\nChoose from what I've put by for "
               "this. I set it aside the day I lost the first of them."))

    q.append(Q("tmp_what_its_worth", "What It's Worth", PIM, 52, 52, "landing",
               "Visit the three places Surveyor Pim hasn't been able to cost: the heart of the "
               "Green Belt, the head of the strand road, and the western pass on the Scoured "
               "Slope.",
               [explore(134, 56, "the heart of the Green Belt", TS),
                explore(168, 80, "the head of the strand road", TS),
                explore(62, 22, "the western pass on the Scoured Slope", TS)],
               "Nobody could reach this island before the change, so nobody's ever valued it. I'm supposed to put a number on the whole of it, and there are three "
               "places I haven't managed to stand in yet.\n\nThe underwriters won't accept "
               "a figure for ground nobody's walked. I've tried all three and I was chased "
               "out of each of them by something different.\n\nThe first is the middle of "
               "the Green Belt, east of here along the trunk road. The second is further "
               "east, where the strand road comes down to the water. The third is the pass "
               "on the Scoured Slope, north-west of the landing up the west road, where it "
               "climbs round the side of the volcano. Stand in each one, have a proper look, "
               "and come back and tell me what's there.",
               "You've got timber in the Belt, wrecks at the strand and nothing on the "
               "slope but ash and scorpions.\n\nThat's about what I'd guessed, but now I "
               "can write it down with a clear conscience. My cousin Nix will take the "
               "figure to the Thane and the Thane will say the island's beyond price. He "
               "says that every time, and then he signs."))

    q.append(Q("tmp_preachers_in_the_forecourt", "Preachers in the Forecourt", PIM, 53, 53,
               "khazvarun",
               "Kill Gate-Squatter Ashpreachers at Khaz Varun's Gate and collect their "
               "Ash-Prayer Tablets.",
               [k("Gate-Squatter Ashpreacher", 8, TS), fetch("tmp_ash_tablet", 4)],
               "I can't survey the forecourt of Khaz Varun's Gate, because every time I set "
               "up the tripod somebody sets fire to it.\n\nThe squatters down there have "
               "preachers. The Gate-Squatter Ashpreachers stand in the rubble and shout at "
               "the arch, and when they see a stranger they throw fire. They carry slates "
               "with writing on them, and I'd like to know what it says. If it's a claim "
               "on the property, the underwriters need to hear about it.\n\nThe forecourt's "
               "south-east of here at the end of the ruin road. Deal with the Ashpreachers "
               "and bring me a few of those slates.",
               "They all say the same line, scratched over and over until the slate's "
               "nearly worn through.\n\nIt says 'the forge is lit and we were not called'. "
               "That isn't a property claim. I don't know what it is, and I don't think I "
               "like it.\n\nI'll send these on to the Deedkeeper in Cinderwharf. She reads "
               "the old hand better than I do."))

    q.append(Q("tmp_bitterbark", "What the Gorillas Know", IMANI, 52, 52, "greenbelt",
               "Collect Chewed Bitterbark from Ashfur Gorillas in the Green Belt for Dr. "
               "Mwangi.",
               [fetch("tmp_bitterbark", 6)],
               "I've run out of anything that takes pain away, and the boat won't bring "
               "more for a month.\n\nBefore I came through I had a cabinet full of tablets. Here "
               "I've got clean water and bandages. But the woodcutters tell me the Ashfur "
               "Gorillas in the Green Belt chew a grey bark and pack it on their burns, and "
               "they've seen burned ones up and climbing again in a day.\n\nPeople have "
               "been learning medicine from animals for as long as there have been "
               "people. Aspirin started as willow bark. I'd like to know what this is.\n\n"
               "The Green Belt's east of the landing, along the trunk road. The gorillas "
               "carry the chewed bark with them. They won't give it up politely.",
               "This is it, and you can smell how strong it is.\n\nI tried a little on my "
               "own tongue while you were putting your pack down, and my whole mouth's "
               "gone numb. That's a real anaesthetic, growing on a tree forty minutes from "
               "my tent.\n\nI spent eleven years on a ferry wishing for better supplies. "
               "It turns out I needed to come to the other side of the world and ask a "
               "gorilla."))

    q.append(Q("tmp_snapper_fat", "A Dressing That Keeps", IMANI, 53, 53, "landing",
               "Collect Snapper Fat from Shallows Snappers in the Tempest Shallows for Dr. "
               "Mwangi's burn dressings.",
               [fetch("tmp_snapper_fat", 6)],
               "Nearly everything I treat here is a burn, and a burn needs a dressing that "
               "stays clean.\n\nThe smelter crews come to me with their arms cooked, and "
               "the people who've been near the gate come with worse. Butter goes off in a "
               "day in this heat. Lamp oil poisons the wound. What I need is a clean fat "
               "that keeps.\n\nThe cook says the fat from under a Shallows Snapper's shell "
               "stays sweet for weeks, and she'd know. The snappers are out in the Tempest "
               "Shallows, east along the trunk road and down the strand road to the water. "
               "Mind their beaks, because I've already stitched two hands this week.",
               "That's lovely clean fat, and there's plenty of it.\n\nI'll melt it down "
               "with the bitterbark and see what I get. If it works I'll have a burn "
               "dressing better than the one I used before I came through, made out of a turtle and a "
               "tree.\n\nYou've still got all your fingers, I see. Hold onto them."))

    q.append(Q("tmp_hulls_and_ribs", "Hulls and Ribs", ROZZ, 53, 53, "wreck",
               "Take Seasoned Wreck Timber from the Wreckpicker Murlocs in the Tempest "
               "Shallows.",
               [fetch("tmp_wreck_timber", 8)],
               "I can't build a barge out of jungle wood, because it's green and it warps "
               "before the pitch is dry.\n\nThe best timber on this island is already "
               "shaped and seasoned, and it's sitting in the wrecks out in the Tempest "
               "Shallows. The trouble is the Wreckpicker Murlocs got there first. They "
               "strip the old ships plank by plank and carry the wood off to build their "
               "own huts.\n\nGo east along the trunk road and down the strand road to the "
               "water, and take the timber off them. I need ribs and strakes, and I don't "
               "care which murloc was carrying them.",
               "Feel the weight of that plank, and then try to mark it with your "
               "thumbnail.\n\nThat's oak that's sat in salt water for longer than I've "
               "been alive. You can't buy wood like that. I'll have a hull framed by the "
               "end of the week.\n\nWhether it stays afloat is another question, and I "
               "want to talk to you about that.",
               nxt="tmp_the_barge_eater"))

    q.append(Q("tmp_the_barge_eater", "The Barge-Eater", ROZZ, 54, 54, "wreck",
               "Kill The Barge-Eater in the Tempest Shallows.",
               [boss("The Barge-Eater", TS)],
               "I've launched six hulls since spring and I've got two left, and I finally "
               "know why.\n\nOne of my crew saw it happen from the beach. A barge was "
               "crossing the bay low in the water with a full load of ore, and a crab came "
               "up underneath it. He says the claw went through the bottom planks like a "
               "pick through a crate. The jetty hands have started calling it The "
               "Barge-Eater.\n\nIt lives out in the deep part of the Tempest Shallows, "
               "south-east of here past the last of the wrecks. It doesn't show itself "
               "often, but it does seem to come up for anybody who goes out there hunting "
               "it. Kill it, or I'm building coffins.",
               "My whole crew watched you drag that claw up the beach, and nobody's done "
               "a stroke of work since.\n\nI'm going to mount it on the bow of the next "
               "hull. The goblins on the wharf will say it's bad luck. I say anything "
               "that sees it coming will think twice.\n\nYou've saved me four barges a "
               "season. Take this, and take a share of the crab while you're at it.",
               requires_quests=["tmp_hulls_and_ribs"]))

    q.append(Q("tmp_clear_the_slip", "Clear the Slip", ROZZ, 53, 53, "landing",
               "Kill Shallows Snappers and Bargebreaker Crabs along the barge channel in the "
               "Tempest Shallows.",
               [k("Shallows Snapper", 10, TS), k("Bargebreaker Crab", 8, TS)],
               "I built yachts in Booty Bay until the sea route opened three years ago and the Ashclaim offered me double. A barge needs a clear channel to get out of the bay, and mine's full of "
               "things with shells.\n\nThe Shallows Snappers lie on the bottom and bite "
               "at the steering oar. The Bargebreaker Crabs hang onto the hull until "
               "something gives. Neither of them can sink a boat alone, but between them "
               "they slow one down enough for worse to catch it.\n\nThe channel runs out "
               "through the Tempest Shallows, east along the trunk road and down the "
               "strand road. Wade out and clear whatever you find on the bottom.",
               "The pilot took a barge out on the evening tide and he says the oar came "
               "back with no new teeth marks.\n\nThat's the first time since I got here. "
               "He was so pleased that he forgot to complain about the pay.\n\nHere's "
               "something from the saw pit stores for you."))

    # ================= THE GATE =================
    q.append(Q("tmp_the_unhoused", "The Unhoused", BRON, 54, 54, "khazvarun",
               "Kill Borrik the Unhoused, who leads the squatters at Khaz Varun's Gate.",
               [boss("Borrik the Unhoused", TS)],
               "There's one of them out in the rubble that the others follow, and I knew "
               "him before he went in.\n\nHis name's Borrik. He was a mason, and the Thane "
               "sent him down with the first party to shore up the gatehouse. He was "
               "inside for six days. When he came out he wouldn't go further than the "
               "forecourt, and he told the others the city had turned him away. They've "
               "called him Borrik the Unhoused ever since.\n\nHe keeps to the broken "
               "ground south and east of where I'm standing, and he doesn't come out for "
               "everyone. He'll come out for somebody who's hunting him. I can't leave "
               "this post and I couldn't do it anyway, because I'd see the mason.",
               "So it's finished, and I'm glad I wasn't the one to see it.\n\nHe built "
               "half the hold at Cinderwharf with his own hands before he went down. I "
               "want that remembered about him, and not the rest.\n\nThe squatters will "
               "drift without him. Some of them might even walk back up the road. Take "
               "this, and don't thank me for it."))

    q.append(Q("tmp_whelps_in_the_vents", "Whelps in the Vents", BRON, 54, 54, "khazvarun",
               "Kill Ashwing Whelps on the Scoured Slope, where the old city's vents come out.",
               [k("Ashwing Whelp", 10, TS)],
               "Khaz Varun breathes through shafts that come out high on the mountain, "
               "and something's nesting in them.\n\nMy family kept those vents clear for "
               "nine generations. A city under a volcano needs air or everyone in it "
               "chokes. Now the Ashwing Whelps roost in the shaft mouths because the "
               "stone's warm, and they've packed them with ash and bones.\n\nThe vents "
               "open onto the Scoured Slope, north of here up the west road. I can't do "
               "anything about what's inside the city, but I can still do this part of "
               "my family's job, if you'll be my hands.",
               "I felt the draught change at the arch about an hour ago, and I thought "
               "it might be you.\n\nIt's blowing outward again, the way my grandfather "
               "said it should. There's no one alive down there to breathe it, but the "
               "Thane means to change that.\n\nYou've done Emberhold work today. Take "
               "this with my family's thanks."))

    q.append(Q("tmp_nine_generations", "Nine Generations", BRON, 53, 53, "khazvarun",
               "Hear Gatewatch Bron out, then carry his count book to Thane Durgan Ashhold in "
               "Cinderwharf.",
               [talk("tmp_bron_the_gate", "tmp_bron_the_count"),
                deliver("tmp_count_book", "Bron's count book, to Thane Durgan Ashhold in "
                                          "Cinderwharf")],
               "You keep looking at the arch, so I'll tell you about it before you do "
               "anything foolish.\n\nAsk me what you like. When you've heard it, I've got "
               "a favour to ask. I keep a book of everyone who goes through that gate and "
               "everyone who comes back, and the Thane hasn't seen it in two months "
               "because nobody will carry it.\n\nHe's in Cinderwharf, on the north-east "
               "shore. Take the trunk road east, then the east road north round the "
               "mountain, and follow the shore north to the town.",
               "This is Bron's book, and I can see he's kept it carefully.\n\nForty-one "
               "have gone in since the spring. Twenty-six have come out, and he's marked "
               "nine of those as 'not right'. I signed the orders for most of these "
               "names.\n\nI've been waiting for somebody who'd read this book and go "
               "down anyway. I think that might be you.",
               nxt="tmp_empty_the_gatehouse", turn_in_npc_id=THANE,
               grant_items=carry("tmp_count_book", "Bron's Count Book",
                                 "Two columns in a neat dwarven hand, in and out. The second "
                                 "column is a good deal shorter.")))

    # ================= THE GREEN BELT'S TWO =================
    q.append(Q("tmp_prospecting_by_gizzard", "Prospecting by Gizzard", HESTA, 53, 53,
               "greenbelt",
               "Collect Basilisk Gizzard Stones from Rubble Basilisks around Khaz Varun's Gate.",
               [fetch("tmp_gizzard_stone", 6)],
               "Nobody's prospected this island since the day the world changed, so I'm the first, and I've found a way to do it without digging, and you're "
               "going to think I've lost my mind.\n\nBasilisks swallow stones to grind "
               "their food. A Rubble Basilisk picks them up wherever it's been walking, "
               "and it walks over ground I can't get to. So if I open one up and there's "
               "truesilver in its gizzard, I know there's truesilver somewhere on its "
               "rounds.\n\nThe Rubble Basilisks are thickest in the broken stone round "
               "Khaz Varun's Gate, south-west of here. Bring me what's in their gizzards "
               "and I'll tell you where the seams are.",
               "Look at that streak, bright as a new coin.\n\nMost of these have truesilver in them and one's got something I don't recognise at all. "
               "That basilisk had been walking over a seam nobody's found yet.\n\nMy old "
               "master would have thrown me out of the guild for this method. He also "
               "died poor, so take your share and don't tell the goblins how I did it."))

    q.append(Q("tmp_the_colour_of_the_rock", "The Colour of the Rock", HESTA, 54, 54,
               "greenbelt",
               "Look at the two outcrops on the Scoured Slope and kill the Cinderslope Flame "
               "Spirits that gather round them.",
               [explore(82, 26, "the western outcrop on the Scoured Slope", TS),
                explore(150, 27, "the eastern outcrop on the Scoured Slope", TS),
                k("Cinderslope Flame Spirit", 8, TS)],
               "Truesilver hides in a rock that's the blue of a pigeon's neck, and I can "
               "see two patches of that colour from here.\n\nThey're both up on the "
               "Scoured Slope, on the flank of the volcano. One's to the north-west above "
               "the west road, and the other's to the north-east above the east road. I'd "
               "walk up myself, but the Cinderslope Flame Spirits gather on exactly that "
               "kind of rock. I think the metal draws them.\n\nGo up to each outcrop and "
               "look at it closely for me. You'll have to put out the Flame Spirits "
               "before they let you near.",
               "So the western one's the true colour, and the eastern one's only "
               "weathered slag.\n\nThat's saved me a week of climbing and probably my "
               "eyebrows. I'll stake the western outcrop tomorrow, before Pim costs it "
               "and the goblins decide it was theirs all along.\n\nYou've got a good eye "
               "for rock. Take this, it came out of the first seam I ever found here."))

    q.append(Q("tmp_what_grows_back", "What Grows Back First", TEODORA, 54, 54, "greenbelt",
               "Kill Ashscree Scorpions on the Scoured Slope, where the first plants are "
               "coming back.",
               [k("Ashscree Scorpion", 10, TS)],
               "There's a strip of the Scoured Slope where plants are coming back onto "
               "bare ash, and I've been watching it since I got here.\n\nI did the same thing before the change. When Cotopaxi dusted the hills south of Quito, I walked "
               "the same plots every month for two years and wrote down what grew first. "
               "It's always something small and stubborn, and here it's a red fern I'd "
               "never seen before this island.\n\nThe Ashscree Scorpions burrow in the "
               "loose ash under the ferns and tear the roots out. The slope's north of "
               "here, where the trees stop. If you can thin the scorpions I might get a "
               "full season of notes.",
               "I walked up after you and the ferns on the lower plot are still "
               "standing.\n\nYou won't think that's much to look at. I can tell you that "
               "in ten years those ferns will be soil, and in fifty that slope will be "
               "forest, and I'll have written down how it started.\n\nNobody will read "
               "it in Quito, and I've made my peace with that. Somebody will read it "
               "here."))

    q.append(Q("tmp_pressed_and_labelled", "Pressed and Labelled", TEODORA, 54, 54, "ashclaim",
               "Carry Teodora's specimen press to Alchemist Pell in Cinderwharf.",
               [deliver("tmp_specimen_press", "the specimen press, to Alchemist Pell in "
                                              "Cinderwharf")],
               "The Ashclaim pays me to say which plants are worth money, and I've got "
               "forty answers pressed between these boards.\n\nEvery one's labelled with "
               "where I found it and what it did to the mouse. Alchemist Pell in "
               "Cinderwharf is the one who decides what the Ashclaim will buy, so the "
               "press needs to reach him flat and dry.\n\nTake the east road north round "
               "the mountain into the Ashen Reach, then follow the shore north to the "
               "town. He's by the salvage yard at the south end. Please don't let him "
               "keep the boards, because I only brought the one press with me.",
               "She's labelled every one of these, and in a better hand than mine.\n\n"
               "I'll be straight with you, I expected a sack of leaves. This is proper "
               "work. Three of these I can sell tomorrow, and that red fern's going to "
               "make somebody rich.\n\nTell her she can have her boards back. Tell her "
               "the Ashclaim's doubling what it pays her as well, and that it was my "
               "idea.",
               turn_in_npc_id=PELL,
               grant_items=carry("tmp_specimen_press", "Teodora's Specimen Press",
                                 "Two boards strapped tight round forty sheets of pressed "
                                 "plants, each one labelled in small careful writing.")))

    # ================= THE SHALLOWS =================
    q.append(Q("tmp_my_boots", "My Boots", JEX, 53, 53, "wreck",
               "Wade out to the near wreck in the Tempest Shallows and get Jex's boots back "
               "from the Bargebreaker Crabs.",
               [explore(178, 92, "the near wreck in the Tempest Shallows", TS),
                fetch("tmp_jex_boot", 2)],
               "I had a good pair of sea boots when I walked out there, and I walked "
               "back in my socks.\n\nI was on the near wreck, the one you can see "
               "sticking up to the south-east. A Bargebreaker Crab got hold of one foot "
               "and I left the boot in its claw. Another one got the second boot while "
               "I was hopping.\n\nThey were made for me in Booty Bay and they've got "
               "brass toes. I want them back. The crabs round that wreck will still "
               "have them, because a crab never lets go of anything.",
               "They've been chewed, but those are my boots and they've still got "
               "their toes.\n\nI'm putting them on right now and I'm never taking them "
               "off again. You've got no idea what it's like to stand on a beach full "
               "of crabs in your socks.\n\nHere, this came out of the wreck before the "
               "crabs came out after me."))

    q.append(Q("tmp_whats_still_aboard", "What's Still Aboard", JEX, 54, 54, "wreck",
               "Search the two far wrecks in the Tempest Shallows and take the Sealed Cargo "
               "Casks the Wreckpicker Murlocs have carried off.",
               [explore(204, 90, "the eastern wreck in the Tempest Shallows", TS),
                explore(190, 120, "the southern wreck in the Tempest Shallows", TS),
                fetch("tmp_cargo_cask", 5)],
               "Now that I've got my boots, I can tell you about the wrecks that are "
               "really worth the walk.\n\nThere are two big ones a long way out. One "
               "lies to the south-east at the edge of the deep water, and the other's "
               "further south again, past the sandbar. They went down with their holds "
               "full, and whoever sailed them sealed the cargo in small casks.\n\nThe "
               "Wreckpicker Murlocs have been carrying those casks off. Go out to both "
               "wrecks and see what's left, and take back whatever casks the murlocs "
               "have got. We'll split what's inside.",
               "Let's get one of these open and see what we've got.\n\nIt's lamp oil, "
               "and good lamp oil at that. It's still clear after all those years under "
               "the bay. That isn't treasure, but Trader Gex in Cinderwharf will pay "
               "for it as if it were.\n\nTake your half in this, and I'll keep the "
               "casks. I told you they were worth the walk."))

    # ================= TWO THINGS A MONSTER DROPS =================
    q.append(Q("tmp_pay_chit", "A Porter's Number", "item:tmp_pay_chit", 53, 53, "landing",
               "A Gate-Squatter was wearing an Ashclaim pay chit. Take it to Quartermaster Durn "
               "at Ashclaim Landing.",
               [deliver("tmp_pay_chit", "the pay chit, to Quartermaster Durn at Ashclaim "
                                        "Landing")],
               "The Brawler had a brass tag on a string round its neck. It's a pay chit "
               "from the Ashclaim stores, the kind every porter at the landing is issued, "
               "and it's stamped with a number.\n\nQuartermaster Durn keeps the pay book "
               "at Ashclaim Landing. He'd know whose number this was.",
               "Where did you get this? I know this number without opening the book.\n\n"
               "This number belongs to Hedda, who carried for me all spring and was the best I had. "
               "She went to look at the gate on her rest day, because she wanted to see "
               "where her grandmother was born. I marked her down as gone home on the "
               "boat.\n\nI'll change the book. I'd sooner it said what happened to her. "
               "It was right of you to bring it back.",
               turn_in_npc_id=DURN))

    q.append(Q("tmp_the_ships_log", "The Ship's Log", "item:tmp_ships_log", 54, 54, "wreck",
               "A Wreckpicker Murloc was carrying a ship's log written in an Earth language. "
               "Take it to Dr. Mwangi at Ashclaim Landing.",
               [deliver("tmp_ships_log", "the ship's log, to Dr. Mwangi at Ashclaim Landing")],
               "The murloc had a hardbound book tucked under its arm. The pages are "
               "swollen with sea water, but the writing's in ink and most of it can "
               "still be read. It's in English, and the dates are from three years "
               "ago.\n\nThe dwarves and goblins at the landing won't be able to read "
               "it. Dr. Mwangi at Ashclaim Landing came through from Earth, and she "
               "will.",
               "Give me a moment with this, because I haven't held a book in English "
               "for three years.\n\nShe was the MV Amani, a coastal freighter out of "
               "Dar es Salaam, carrying cement and tinned fish to Mombasa. I knew that "
               "ship. I used to watch her come in past the ferry.\n\nThe last entry's "
               "the day everything changed. The mate wrote that the coast had gone and "
               "the stars were wrong, and that they were making for the only land "
               "they could see. That land was this island.",
               nxt="tmp_who_was_aboard", turn_in_npc_id=IMANI))

    q.append(Q("tmp_who_was_aboard", "Who Was Aboard", IMANI, 55, 55, "wreck",
               "Find the steel wreck in the far Tempest Shallows and recover the crew's "
               "discharge books from the Wreckpicker Murlocs.",
               [explore(206, 116, "the steel wreck in the far Tempest Shallows", TS),
                fetch("tmp_discharge_book", 4)],
               "There were eleven people on that ship, and the log gives me nothing "
               "but their ranks.\n\nEvery seaman carries a discharge book with a name "
               "and a photograph in it. If the murlocs took the log, they'll have "
               "taken those as well, because they take anything with a hard "
               "cover.\n\nThe log puts her aground at the far south-east corner of the "
               "Tempest Shallows. She'll be the only wreck out there made of steel. "
               "Would you go and see that she's really there, and bring back whatever "
               "books you can find? They've been lost for three years, and I'd like to know who they were.",
               "You found some of them, and I can read every name.\n\nThis one's "
               "Juma Otieno, the second engineer, and he was born in Kisumu. I don't "
               "know whether they drowned or walked ashore. If they walked, they may "
               "be somewhere in this world wondering if anyone knows they were "
               "here.\n\nI'm going to copy these names out and send them with every "
               "boat that leaves this jetty. Somebody may have met them.",
               requires_quests=["tmp_the_ships_log"]))

    # ================= KHAZ VARUN, GIVEN IN CINDERWHARF =================
    q.append(Q("tmp_empty_the_gatehouse", "Empty the Gatehouse", THANE, 53, 54, "khazvarun",
               "Enter Khaz Varun, the Black Hollow, and kill Gatewarden Hrun in the Gatehouse "
               "Hall.",
               [boss("Gatewarden Hrun", KV)],
               "My great-grandfather's gatewarden is still at his post, and that's the "
               "first thing I need you to put right.\n\nHis name was Hrun. He held the "
               "gate of Khaz Varun the night the city went dark, and by every account "
               "he's holding it still. The gate opened by itself three years ago, on the day the world changed, and nobody I've sent since has got past him, and those "
               "who've come back can't tell me what they saw.\n\nThe gate's on the south "
               "shore of the island, a short walk south-east of Ashclaim Landing. Go "
               "through the arch and you'll find him in the Gatehouse Hall beyond the "
               "Ember Road. He was a loyal dwarf, so make it quick.",
               "Then Hrun's relieved at last, and it's taken four generations.\n\nI'll "
               "have his name cut at the shrine tonight. He kept the gate against "
               "everything for a hundred years, and it's no shame on him that he "
               "couldn't tell friend from stranger at the end.\n\nThe gatehouse was the "
               "lock. The city's behind it, and the worst of the city's further in.",
               nxt="tmp_the_forge_lord", zone=CW,
               requires_quests=["tmp_nine_generations"]))

    q.append(Q("tmp_the_forge_lord", "The Forge Is Lit", THANE, 54, 55, "khazvarun",
               "Kill Forge-Lord Darrok at the Great Forge in Khaz Varun, the Black Hollow.",
               [boss("Forge-Lord Darrok", KV)],
               "The squatters at the gate keep saying that the forge is lit, and I've "
               "learned that they're telling the truth.\n\nThe Great Forge of Khaz Varun "
               "has been cold since before my father was born. It's burning now. "
               "Somebody's working it, and the rolls say the last Forge-Lord was a "
               "dwarf named Darrok who never left his anvil.\n\nYou'll find the Great "
               "Forge on the east side of the city, past the Counting Hall. Whatever's "
               "standing at that anvil is making something, and I don't want to learn what it's making by having it walk out of my gate.",
               "So Forge-Lord Darrok was still at it, after all this time.\n\nThe Underwriter will be "
               "delighted that the forge works. I'm less delighted about what it was "
               "being used for. You say the moulds were shaped like dwarves, and I "
               "believe you.\n\nThat leaves the hall itself. I've been putting off "
               "saying it aloud.",
               nxt="tmp_thane_morrun", zone=CW))

    q.append(Q("tmp_thane_morrun", "The Thane in the Chair", THANE, 55, 56, "khazvarun",
               "Kill Thane Morrun the Unmade in the Hall of Ashhold, at the top of Khaz Varun.",
               [boss("Thane Morrun the Unmade", KV)],
               "My great-grandfather's name was Morrun Ashhold, and he's sitting in his "
               "own chair at the top of that city.\n\nThe gate opened three years ago, and I've known it for one of them. One of "
               "the first party got as far as the Hall of Ashhold and saw him through "
               "the doors. He hasn't been a dwarf for a long time. The squatters call "
               "him the Unmade, and I've got no better word.\n\nMy claim rests on being "
               "his heir. I can't inherit from a thane who's still in the chair, and I "
               "can't lay my family to rest while he keeps them walking. The hall's at "
               "the north end of the city, beyond the Shadow Gallery. I'm asking you to "
               "kill Thane Morrun the Unmade, and I know what I'm asking.",
               "You've done it, then, and I find I need to sit down.\n\nI've carried "
               "that deed since I was a boy. I slept on it in rented rooms and I kept "
               "it dry on a goblin barge. I never once let myself picture the day it "
               "would mean something.\n\nKhaz Varun has one thane tonight. Morn will "
               "light a flame for the old one, and I'll stand beside him while he does "
               "it. Whatever the Ashclaim owes you, it won't be enough, but take it "
               "anyway.",
               zone=CW, requires_quests=["tmp_the_forge_lord"]))

    q.append(Q("tmp_a_flame_for_each", "A Flame for Each", MORN, 54, 54, "khazvarun",
               "Recover Ashhold Name-Tablets from the Ash-Wretches in Khaz Varun, the Black "
               "Hollow.",
               [fetch("tmp_name_tablet", 8)],
               "I keep one flame on this terrace for everyone still down there, because "
               "I don't know their names.\n\nEvery Dark Iron of Khaz Varun carried a "
               "name-tablet from the day they could walk. It's a thumb of iron with "
               "the name punched in. The Ash-Wretches in the lower city were our people "
               "once, and some of them will still have a tablet on them somewhere.\n\n"
               "The gate's on the south shore, south-east of Ashclaim Landing, and the "
               "Ash-Wretches keep to the Ash Pits and the Deep Way in the middle of "
               "the city. Bring me the tablets. I'd like to give each of them a flame "
               "of their own.",
               "I'm going to read every one of these names aloud "
               "before I do anything else.\n\nTwo of these are Ashholds. One's an "
               "Emberhold, so Bron at the gate will want to know. The rest I'll look "
               "up in the Deedkeeper's rolls.\n\nI've tended one flame for three "
               "years. Tonight I'll tend nine, and I'm happier about that than I can "
               "tell you.",
               zone=CW))

    q.append(Q("tmp_the_iron_mask", "The Iron Mask", MORN, 55, 55, "khazvarun",
               "Kill The Iron Mask in the Cells of Khaz Varun, the Black Hollow.",
               [boss("The Iron Mask", KV)],
               "There are dwarves in that city with iron masks riveted over their faces, "
               "and they weren't born down there.\n\nThe masks are new, and some of them are "
               "wearing Ashclaim boots. Something in the Cells is taking the people who "
               "go in, masking them and sending them back out into the halls to "
               "preach. The ones who've seen it call it The Iron Mask, because nobody's "
               "seen a face.\n\nThe Cells are on the west side of the city, below the "
               "Deep Way. I keep a flame for the dead. I can't keep one for people who "
               "are still walking about, so I need The Iron Mask stopped.",
               "Then nobody else will be masked, and that's more than I'd hoped "
               "for.\n\nThe ones already wearing them are past my help. I'll say the "
               "words for them anyway. My cousin would tell you the words don't work "
               "on the living, and he'd be right, and I'll say them all the same.\n\n"
               "Take this from the shrine's keeping, because it should be worn by "
               "someone who's been down there.",
               zone=CW))

    q.append(Q("tmp_foundry_inventory", "Foundry Inventory", NIX, 54, 54, "ashclaim",
               "Inspect the Smelter and the Great Forge in Khaz Varun, the Black Hollow, and "
               "kill Smelter-Master Vaud.",
               [explore(150, 146, "the Smelter in Khaz Varun", KV),
                explore(150, 116, "the Great Forge in Khaz Varun", KV),
                boss("Smelter-Master Vaud", KV)],
               "I've underwritten a foundry that I've never seen, and my partners have "
               "started to notice.\n\nThe whole venture rests on Khaz Varun's works "
               "being sound. The Thane says they are. The Thane also says the island's "
               "beyond price, so I'd like a second opinion from someone who's stood in "
               "them.\n\nBoth works are on the east side of the city, through the gate "
               "on the south shore near Ashclaim Landing. Look over the Smelter and "
               "the Great Forge and tell me what state they're in. I'm told the "
               "Smelter still has its master, a Smelter-Master Vaud, and that he "
               "doesn't take visitors. You'll need to remove him before anyone can "
               "do an inventory.",
               "The crucibles are whole and the flues draw, and you're telling me "
               "the Great Forge is hot.\n\nThat's better than I'd dared to put in "
               "the prospectus. I'd have settled for four walls and a chimney.\n\n"
               "I won't ask what Smelter-Master Vaud was smelting. I'll put down "
               "that the position's vacant.",
               zone=CW))

    q.append(Q("tmp_what_masks_fetch", "What It Fetches on the Mainland", TAZZ, 54, 54,
               "khazvarun",
               "Collect Zealot's Iron Masks from the Masked Zealots in Khaz Varun, the Black "
               "Hollow.",
               [fetch("tmp_zealot_mask", 6)],
               "I've got a buyer on the mainland who collects Dark Iron work, and he's "
               "asked for something I can't get anywhere else.\n\nHe wants the masks. "
               "The Masked Zealots in Khaz Varun wear iron ones, riveted shut, and "
               "there's nothing like them in any hold on the continent. He doesn't "
               "need to know where they came from, and I'd thank you not to tell the "
               "Keeper where they went.\n\nThe Zealots are all through the city, from "
               "the Gatehouse Hall inward. The gate's on the south shore near "
               "Ashclaim Landing. I'll pay well over the odds for every mask.",
               "Those are the real thing, and the rivets are still tight.\n\nI'll "
               "be honest with you, I didn't enjoy handling them as much as I "
               "expected to. They're heavier than they ought to be. The buyer can "
               "have the lot and I won't be asking for more.\n\nHere's your money, "
               "and here's something from the yard on top of it.",
               zone=CW))

    q.append(Q("tmp_grandmothers_mark", "My Grandmother's Mark", BRENNA, 54, 55, "khazvarun",
               "Recover the Stonecast Breastplate from The Crusher in the Workshop of Khaz "
               "Varun, the Black Hollow.",
               [fetch("tmp_stonecast_plate", 1)],
               "My grandmother was the best armoursmith Khaz Varun ever had, and I've "
               "never seen a single piece she made.\n\nShe got out as a girl with "
               "nothing but her hammer. Everything she'd forged stayed behind. One of "
               "the Thane's people says there's a machine in the Workshop, a great "
               "stamping engine they call The Crusher, and that it's armoured with "
               "plate taken off the walls. He swears one of those plates carries the "
               "Stonecast mark.\n\nThe Workshop's on the west side of the city, just "
               "past the Ember Road. I want that breastplate. I can't learn her hand "
               "from stories.",
               "Turn it over and let me see under the left arm.\n\nThat's her mark, "
               "three chisel cuts and a dot. She showed it to me in the dirt when I "
               "was small.\n\nLook how she's drawn the edge out thin there and left "
               "the centre thick. I've been doing that wrong my whole life. I'm "
               "going to be at the forge all night, so take this now before I "
               "forget you're here.",
               zone=CW))

    q.append(Q("tmp_the_rolls_below", "The Rolls Below", THORA, 55, 55, "khazvarun",
               "Search the Counting Hall of Khaz Varun, the Black Hollow, and take the Roll of "
               "Oaths from Overseer Grall.",
               [explore(88, 122, "the Counting Hall in Khaz Varun", KV),
                fetch("tmp_roll_of_oaths", 1)],
               "The Thane's claim stands on the rolls I keep, and the rolls I keep "
               "have a hole in them.\n\nWhen the city went dark, the Deedkeeper of "
               "the day carried out the births and the debts. He left the Roll of "
               "Oaths behind, because it was chained to the desk in the Counting "
               "Hall. Without it I can't prove who swore to the Ashholds and who "
               "didn't, and the goblins' lawyers know that.\n\nThe Counting Hall's "
               "in the middle of the city, beyond the Gatehouse Hall. The Overseer "
               "of the hall was a dwarf called Grall, and I'm told Overseer Grall "
               "still walks his rounds with the roll on his belt.",
               "It's all here, every leaf, and the ring's still closed.\n\nI can "
               "see the Emberholds, the Stonecasts and the Deepveins. Every family "
               "on this wharf swore to the Ashholds, in iron, and now I can show "
               "it to anyone who asks.\n\nThe Underwriter's going to be very polite "
               "to me tomorrow. I'm looking forward to it more than I should.",
               zone=CW))

    q.append(Q("tmp_what_they_breathed", "What They Breathed", PELL, 54, 54, "khazvarun",
               "Collect Pouches of Black Dust from the Crazed Miners in Khaz Varun, the Black "
               "Hollow.",
               [fetch("tmp_black_dust", 6)],
               "People go into that city sane and come out raving, and I'd like to "
               "know whether it's something in the air.\n\nIf it is, it matters to "
               "everyone on this wharf. We're shipping ore out of the same rock. The "
               "Crazed Miners in the lower workings have been breathing it for longest, and their clothes will be thick with it.\n\nGo "
               "through the gate on the south shore near Ashclaim Landing. The "
               "miners are in the Ember Road and the Borer Workings. Shake out "
               "their pockets and bring me the dust, and tie something over your "
               "own mouth while you're doing it.",
               "I've had a pinch of this under the glass while you were washing "
               "your hands.\n\nIt's forge soot, mostly, but there's a fine red "
               "grit in it that glows when I breathe on it. That isn't in the ore "
               "we ship, and I checked three sacks to be sure.\n\nSo it's coming "
               "from something that's burning down there now. The doctor at the "
               "landing ought to hear about this, and I'll write to her tonight.",
               zone=CW))

    return q
