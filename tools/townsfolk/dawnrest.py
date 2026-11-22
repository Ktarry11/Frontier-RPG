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
     "Everyone who goes into the woods through the north gate gets counted, and everyone who comes back. The "
     "numbers have matched every day this month."),
    ("dr_tf_lamplighter", "Lamplighter Faelen", "blood_elf", M, "The Woods Gate",
     "The lamps along the road were dark for a thousand years, and now I light them every dusk. Some of the "
     "newcomers cried the first time they saw them lit, and I didn't understand why until I saw them cry."),
    ("dr_tf_scribe", "Scribe Annalis Quillbright", "blood_elf", F, "The Waystation",
     "Two copies of every page of the Lightwarden's notes, in case one burns. Magister Aeron calls that "
     "paranoid, and that's exactly what a scribe is for."),
    ("dr_tf_apprentice", "Apprentice Corin Ashveil", "blood_elf", M, "The Waystation",
     "Magister Aeron is my uncle, and he's let me hold the shards from the thicket exactly once. They hummed "
     "in my hand, and he took them back before I could ask him why."),
    ("dr_tf_fletcher", "Fletcher Ilmara", "blood_elf", F, "The Huntress's Lodge",
     "Lyra's hunters carry my arrows into the Red Hollow, and what comes back tells the story. Broken shafts "
     "mean bears, and missing ones mean spiders."),
    ("dr_tf_inn_regular", "Old Venthas", "blood_elf", M, "The Ember Hearth",
     "This outpost was whole when I served here, and the Conclave brought me home to see it again. The "
     "hearth's in the wrong place now, but the stew's better."),
    ("dr_tf_earth_teacher", "Sofia Berglund", "human", F, "The Ember Hearth",
     "Chalk dust from a classroom in Uppsala was still on my hands when I washed up. Now the newcomers' "
     "children learn their letters by the hearth, and the elves listen from the back."),
    ("dr_tf_earth_mechanic", "Rahul Mehta", "human", M, "The Carpenters' Yard",
     "Buses in Pune, and now a boat with Mirelle, which is close enough. The elves don't use nails the way "
     "anyone else would, and theirs hold better."),
    ("dr_tf_carpenter_boy", "Young Thalion", "blood_elf", M, "The Carpenters' Yard",
     "One day Mirelle says the timber will be mine to shape. Today a plank for the skiff got sanded, and she "
     "only made me do it over twice."),
    ("dr_tf_earth_mother", "Nomvula Dlamini", "human", F, "The Newcomers' Camp",
     "My two boys and I woke on the Waking Shore, and the elves walked us up here that first night. Cooking "
     "for the camp is the least we can do."),
    ("dr_tf_earth_student", "Liam O'Connell", "human", M, "The Newcomers' Camp",
     "My history professors in Galway would kill to see this place. The elves are patient with questions, "
     "mostly, until you ask about the outpost's last days."),
    ("dr_tf_goblin_peddler", "Grizzle Sparkwhistle", "goblin", M, "The Quartermaster's Row",
     "Thread, nails and anything shiny, that's what elves buy, as it turns out. The Durotar boat brought me "
     "and a crate, and the quartermaster doesn't need to know my prices."),
    ("dr_tf_orc_porter", "Morga Ironhide", "orc", F, "The Glade Gate",
     "The Warchief sent a few of us over to help the Conclave settle, and I carry whatever needs carrying up "
     "from the shore. The elves thought I'd be rude, and I've decided to disappoint them."),
]
