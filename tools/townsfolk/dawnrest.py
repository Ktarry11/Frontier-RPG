"""Dawnrest's people: the old waystation on the road between Amberleaf Glade and Duskfall Woods (22 Nov 2026).

Kyle: "a small town (just a little 'hub' near the entrance between duskfall and amberleaf", and on numbers: "Small towns
can be 15-20 ... Generally cities lean towards one or two races but not exclusive." Dawnrest already had four townsfolk
of its own (the guard, the carpenter, the hunter and Andrés, in tools/build_dawnhaven_people.py); these make it sixteen.
Blood elves of the Sunreach Conclave and the Earthborn who woke on the Waking Shore and walked up the road, with a
goblin and an orc off the Durotar boat. None of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    ("dr_tf_gate_warden", "Warden Taelis Duskbrook", "blood_elf", F, "The Woods Gate",
     "I keep the north gate, and I count everyone who goes into the woods and everyone who comes back. The numbers "
     "have matched every day this month, and I'd like to keep it that way."),
    ("dr_tf_lamplighter", "Lamplighter Faelen", "blood_elf", M, "The Woods Gate",
     "The lamps along the road were dark for a thousand years, and now I light them every dusk. Some of the newcomers "
     "cried the first time they saw them lit, and I didn't understand why until I saw them cry."),
    ("dr_tf_scribe", "Scribe Annalis Quillbright", "blood_elf", F, "The Waystation",
     "I copy the Lightwarden's notes on the Lightwell, every page twice, in case one copy burns. Magister Aeron says "
     "that's paranoid, and I've told him that's exactly what a scribe is for."),
    ("dr_tf_apprentice", "Apprentice Corin Ashveil", "blood_elf", M, "The Waystation",
     "Magister Aeron is my uncle, and he's let me hold the shards from the thicket exactly once. They hummed in my hand, "
     "and he took them back before I could ask him why."),
    ("dr_tf_fletcher", "Fletcher Ilmara", "blood_elf", F, "The Huntress's Lodge",
     "I make the arrows Lyra's hunters carry into the Red Hollow, and I can tell from what comes back how the hunt went. "
     "Broken shafts mean bears, and missing ones mean spiders."),
    ("dr_tf_inn_regular", "Old Venthas", "blood_elf", M, "The Ember Hearth",
     "I served at this outpost when it was whole, and I came home with the Conclave to see it again. The hearth's in "
     "the wrong place now, but the stew's better than the garrison's ever was."),
    ("dr_tf_earth_teacher", "Sofia Berglund", "human", F, "The Ember Hearth",
     "I taught primary school in Uppsala, and I washed up on the shore with chalk dust still on my hands. Now I teach "
     "the newcomers' children their letters by the hearth, and the elves sit in the back and listen."),
    ("dr_tf_earth_mechanic", "Rahul Mehta", "human", M, "The Carpenters' Yard",
     "I fixed buses in Pune, and now I'm helping Mirelle build a boat, which is close enough. The elves don't use nails "
     "the way I'd use them, and I've stopped arguing about it because theirs hold better."),
    ("dr_tf_carpenter_boy", "Young Thalion", "blood_elf", M, "The Carpenters' Yard",
     "I carry the timber up from the Red Hollow, and Mirelle says one day I'll get to shape it. Today I sanded a plank "
     "for the skiff, and she only made me do it over twice."),
    ("dr_tf_earth_mother", "Nomvula Dlamini", "human", F, "The Newcomers' Camp",
     "I woke up on the Waking Shore with my two boys, and the elves walked us up here on the first night. I cook for the "
     "camp now, because I couldn't sit still while people fed us."),
    ("dr_tf_earth_student", "Liam O'Connell", "human", M, "The Newcomers' Camp",
     "I was halfway through a history degree in Galway, and I keep thinking how my professors would kill to see this "
     "place. The elves are patient with my questions, mostly, until I ask about the outpost's last days."),
    ("dr_tf_goblin_peddler", "Grizzle Sparkwhistle", "goblin", M, "The Quartermaster's Row",
     "I came over on the Durotar boat with a crate of goods and no idea what elves buy. Turns out it's thread, nails "
     "and anything shiny, so I'm doing all right, and I'm not telling the quartermaster my prices."),
    ("dr_tf_orc_porter", "Morga Ironhide", "orc", F, "The Glade Gate",
     "The Warchief sent a few of us over to help the Conclave settle, and I carry whatever needs carrying up from the "
     "shore. The elves thought I'd be rude, and I've decided to disappoint them."),
]
