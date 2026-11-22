"""Lastlight's people: the last town on the Fading Firmament, round the one shrine still lit (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated". The Firmament's people left in stages over centuries as its crystal went
dark, and these are the ones who wouldn't go: old families, a few who came back, the house's scholars, two Earthborn
with the children. They're few, and it should feel that way, but every corner of the town has somebody in it. None of
them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Lamp Walk
    ("ll_tf_lamp_boy", "Aric Sollen", "aetherian", M, "The Lamp Walk",
     "I carry the taper for Toben when he lights the walk every evening. My mother keeps the inn, and she says I can "
     "be the lamplighter when he's old. He says he's already old, so I'm practising."),

    # ---- the Shelter
    ("ll_tf_grandmother", "Old Hilde Dray", "aetherian", F, "The Shelter",
     "My family's lived on the Firmament for nine hundred years, and my children all left for Aurelion. They write and "
     "ask me to come. I tell them I'll come when the shrine goes out, and we both know what I mean."),
    ("ll_tf_shelter_father", "Corvin Ash", "aetherian", M, "The Shelter",
     "We came back up the road from the Bastions last spring, because the yard wanted my hands and I didn't want to "
     "give them. Lastlight's dying, but it's ours, and my daughter sleeps here without hearing the guns."),
    ("ll_tf_shelter_girl", "Little Nessa Ash", "aetherian", F, "The Shelter",
     "Teacher Margit says I'm the best at letters in Lastlight. There are eleven of us, so it isn't hard, but I'm still "
     "the best. I write my name on every wall that isn't falling down."),

    # ---- the Shrine Court
    ("ll_tf_shrine_sitter", "Elder Rhosyn Vale", "aetherian", F, "The Shrine Court",
     "I sit by the shrine every evening, because somebody should be looking at it when the lamps are lit. I watched "
     "eight shrines go out on the Firmament in my life. I'd like to be looking away when the last one does."),
    ("ll_tf_shrine_apprentice", "Kellan Moor", "aetherian", M, "The Shrine Court",
     "I'm learning to cut crystal from Ansel, and there's almost nothing left to learn on. He makes me practise on dead "
     "shards, and I've cut forty of them, and none of them will ever light."),

    # ---- the Magistrate's Steps
    ("ll_tf_clerk", "Clerk Ivette Rane", "aetherian", F, "The Magistrate's Steps",
     "I keep the magistrate's rolls, every name of everyone who still lives on the Firmament. It used to fill three "
     "books, and now it fits on two pages. I copy it out fresh every month so it never looks crossed out."),

    # ---- the Long Memory's Rooms
    ("ll_tf_house_copyist", "Copyist Brannagh Tull", "aetherian", F, "The Long Memory's Rooms",
     "The Archivist brought her books in from the forge so they'd have a roof and a light. I copy the Kharad rubbings "
     "Rhun brings back. I can't read a word of them, but my lines are straight."),
    ("ll_tf_house_novice", "Novice Peregrine Holt", "aetherian", M, "The Long Memory's Rooms",
     "Every other house laughed when I joined the House of Long Memory. Then the giants' forge started glowing, and now "
     "my cousins write to me asking what it means. I write back that I'm not allowed to say."),

    # ---- the Forge Shed
    ("ll_tf_forge_helper", "Bryn Calder", "aetherian", M, "The Forge Shed",
     "I work the bellows for Kwabena, and he teaches me words in his language while we work. I know the word for hot, "
     "the word for careful and a word he won't tell me the meaning of."),

    # ---- the Skiff Ledge
    ("ll_tf_ledge_watcher", "Saela Tarn", "aetherian", F, "The Skiff Ledge",
     "I watch for the skiff coming home every evening from the ledge. My brother flies the cargo runs to the Bastions, "
     "and I won't go in until I see his lamp. Most nights it's late, and most nights I'm cold."),
    ("ll_tf_earthborn_widower", "Anders Lindqvist", "human", M, "The Skiff Ledge",
     "Margit and I are both from the north of Sweden, which is a strange thing to share in a place like this. I fixed "
     "boats in Lulea, and now I patch the last skiff with whatever the islands drop."),
]
