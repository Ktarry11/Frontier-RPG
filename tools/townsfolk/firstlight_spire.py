"""Firstlight Spire's people: Dawnhaven's town under the old outpost's spire, the Sunreach Conclave's home (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." Firstlight already had its guards, a lady, a student, a fisher and a settler of its own (tools/
build_dawnhaven_people.py); these seventeen make it the island's town. Blood elves of the Conclave, the Earthborn the
shore gave up, and a few who came over on the Durotar boat. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("fls_tf_court_sweeper", "Sweeper Aelin", "blood_elf", M, "The Spire Court",
     "The spire's court gets swept twice a day, because the light off the crystal shows every speck. Spire-Keeper Lorien inspects it at noon, and I've never failed yet."),
    ("fls_tf_court_painter", "Painter Isolde Brightquill", "blood_elf", F, "The Spire Court",
     "The spire's light changes colour with the hour, and every hour gets painted. Two hundred canvases so far, and the Conclave hangs one in the hall each season."),
    ("fls_tf_hall_clerk", "Clerk Fendrel", "blood_elf", M, "The Conclave Hall",
     "Every magister's petition to the Grand Magister crosses my desk first. Most of them are about who gets the room with the better view of the spire."),
    ("fls_tf_hall_page", "Page Seris", "blood_elf", F, "The Conclave Hall",
     "Running messages between the magisters keeps a page fit. They never send a message they could have shouted across the hall, but they never shout."),
    ("fls_tf_library_reader", "Reader Thelandris", "blood_elf", M, "The Library",
     "The library tower holds every book the Conclave carried from Silvermoon, stacked three deep. Reading them standing up is the only way, there aren't enough chairs."),
    ("fls_tf_library_earth", "Dr. Oliver Grant", "human", M, "The Library",
     "A librarian from Edinburgh, cataloguing books in a language that glows. The elves have no system at all, and they think mine is charming."),
    ("fls_tf_inn_regular", "Old Ravaniel", "blood_elf", M, "The Inn Steps",
     "The inn's steps get the last of the evening sun, and that's where my evenings go. Three hundred years of evenings, and these are the best ones."),
    ("fls_tf_inn_newcomer", "Grace Mwangi", "human", F, "The Inn Steps",
     "Washed up on the Waking Shore in spring, and now a room at the inn and a job in the kitchen. Nairobi feels very far away, and the Spire feels like somewhere I could stay."),
    ("fls_tf_bank_waiter", "Lord Caelen Dawnsorrow", "blood_elf", M, "The Bank Row",
     "MerchantTusk has kept me waiting an hour for my own savings. He calls it prudence, and I call it theatre, and he smiles at both."),
    ("fls_tf_bank_goblin", "Grizzle Coinbright", "goblin", F, "The Bank Row",
     "Came over on the Durotar boat to open a currency stall, and the elves pay in coins I've never seen. Half of them glow, and I'm charging extra for those."),
    ("fls_tf_roost_keeper", "Keeper Aerith Hawkwind", "blood_elf", F, "The Hawk Roost",
     "The dragonhawks in the roost bite everybody but the Hawkmaster and me. That's not loyalty, it's that we feed them, and they remember."),
    ("fls_tf_roost_child", "Little Kaelin", "blood_elf", M, "The Hawk Roost",
     "One of the dragonhawk chicks lets me hold her if I sing to her first. My singing's terrible, and she doesn't seem to mind."),
    ("fls_tf_lane_smith_hand", "Striker Vorath", "blood_elf", M, "The Crafters' Lane",
     "Smith Torvael's forge works rune-steel, which means hammering in time with a chant. Miss the beat, and the runes come out crooked, and he makes you start over."),
    ("fls_tf_lane_alchemy_hand", "Apprentice Mirela", "blood_elf", F, "The Crafters' Lane",
     "The alchemist's shop smells of cinnamon and something that might explode. Most of my job is keeping those two things apart."),
    ("fls_tf_lane_orc_trader", "Grosha", "orc", F, "The Crafters' Lane",
     "The Warchief sent me to trade iron for the elves' enchanted thread. They stare at my tusks, and I stare at their ears, and the trade goes fine."),
    ("fls_tf_pier_hand", "Dockhand Ilyen", "blood_elf", M, "The Pier Steps",
     "The Durotar boat ties up below these steps every few days, and it always brings something strange. Last time it was a goblin selling umbrellas, in a place where it never rains."),
    ("fls_tf_gate_watch", "Watcher Saelith", "blood_elf", F, "The South Gate",
     "The south gate opens onto the road down to the woods and Dawnrest beyond. Everybody coming up it looks tired, and everybody going down looks brave."),
]
