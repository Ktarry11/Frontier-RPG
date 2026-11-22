"""Tarren Mill's people: the mill town in the Hillsbrad foothills, the Forsaken's apothecarium beside it (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." Tarren Mill leans two ways at once: the living millers and farmers who stayed when the Forsaken came,
and the Forsaken who run the apothecarium and the garrison. An orc or two with the wind-riders. None of them gives a
quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("tm_tf_mill_hand", "Millhand Joss Tanner", "human", M, "The Mill Yard",
     "A hundred sacks a day from the millstone to the granary in the good season. The Forsaken buy most of the"
     " flour now, and they pay on time, which the old lord never did."),
    ("tm_tf_flour_wife", "Martha Reed", "human", F, "The Mill Yard",
     "My brother's flour makes the bread for the whole town. The Forsaken can't taste it, but they buy it for "
     "the living ones passing through, and they always say thank you."),
    ("tm_tf_smith_apprentice", "Apprentice Hal Cobb", "human", M, "The Mill Yard",
     "The smith says the mill's ironwork will be mine to keep before long. The Forsaken bring their swords "
     "too, and it's best not to look at what's dried on them."),
    ("tm_tf_forsaken_carter", "Carter Abel Dunn", "forsaken", M, "The Mill Yard",
     "Same cart, same road, before I died and after. The living folk were frightened of me at first, and now "
     "they wave."),
    ("tm_tf_vat_tender", "Tender Morwenna", "forsaken", F, "The Apothecarium",
     "Keep your face out of the fumes when you stir the vats, that's the whole trick. Breathing's optional "
     "now, but the eyes still water, which seems unfair."),
    ("tm_tf_apoth_courier", "Courier Felix Grave", "forsaken", M, "The Apothecarium",
     "Sealed crates from the apothecarium to the bat roost, and never ask what's inside. Some of them are "
     "heavier on the way back than on the way out."),
    ("tm_tf_garrison_grunt", "Deathguard Pell", "forsaken", M, "The Apothecarium",
     "The living townsfolk give the apothecarium's guards a wide berth. Fair enough, and the vats get an even "
     "wider one from me."),
    ("tm_tf_orc_rider", "Wind-Rider Groka", "orc", F, "The Apothecarium",
     "Strangest posting a wind-rider ever had, this. The dead and the living share one street, and nobody's "
     "killed anybody yet."),
    ("tm_tf_bat_keeper_aide", "Hobble", "forsaken", M, "The Apothecarium",
     "The bats and the wyverns don't like each other one bit. Most nights the job is just keeping the peace "
     "between them."),
    ("tm_tf_weir_fisher", "Fisher Old Tom", "human", M, "The Weir",
     "The trout gather in the eddies below the sluice, same as when my father fished here. The Forsaken don't "
     "eat fish, so it's all mine."),
    ("tm_tf_sluice_boy", "Pip Weller", "human", M, "The Weir",
     "Pate says the whole mill depends on the two of us opening the sluice gates when the river's high. He's "
     "only half joking."),
    ("tm_tf_washerwoman", "Washerwoman Sal", "human", F, "The Weir",
     "The town's linen and the Forsaken's both get washed in the millrace now. Their sheets don't get dirty "
     "the same way, and it's best not to ask why."),
    ("tm_tf_cottage_mother", "Goodwife Ada Pell", "human", F, "Mill Row",
     "My husband went off to the war and never came back, and the Forsaken asked me if I wanted him to. I said"
     " no, and they respected that, and I've never forgotten it."),
    ("tm_tf_cottage_child", "Little Bess", "human", F, "Mill Row",
     "The Forsaken man down the lane gives me sweets on market day. My mother says not to take them, but "
     "they're always wrapped, and he always smiles, even if his smile's a bit crooked."),
    ("tm_tf_inn_regular", "Ned Barlow", "human", M, "Mill Row",
     "Every evening at the inn there's an argument about the old king. Some of the Forsaken knew him, and they"
     " win most of them, which is annoying."),
    ("tm_tf_stable_girl", "Molly Teague", "human", F, "Mill Row",
     "Our horses won't go near the Forsaken's skeletal ones. They're jealous, because the skeletal horses "
     "never get tired."),
    ("tm_tf_forsaken_neighbour", "Mr. Pennick", "forsaken", M, "Mill Row",
     "The cottage at the end of the row was mine before I died, and it's mine again now. The neighbours took a"
     " while, and now they bring me their broken clocks."),
    ("tm_tf_chapel_sexton", "Sexton Ambrose", "human", M, "The Chapel Hill",
     "Some of the graves on this hill are empty on purpose. The Forsaken who climbed out of them come back to "
     "tidy them, which is very touching."),
    ("tm_tf_chapel_widow", "Widow Clara Finch", "human", F, "The Chapel Hill",
     "I pray at the chapel every morning for the living and the dead both. The chaplain says the Light doesn't"
     " choose sides, and I've decided to believe him."),
    ("tm_tf_hill_shepherd", "Shepherd Gil", "human", M, "The Chapel Hill",
     "Not once have the sheep wandered toward the apothecarium. Sheep are smarter than people give them credit"
     " for."),
    ("tm_tf_burnt_cottage", "Old Agatha", "human", F, "The Burnt Lane",
     "My cottage burned in the war, and I live in the shed behind it now. The Forsaken offered to rebuild it, "
     "and I told them I'd rather keep the ashes, because they're mine."),
    ("tm_tf_lane_scavenger", "Scavenger Ruth", "forsaken", F, "The Burnt Lane",
     "Whatever's worth keeping in the burnt houses goes back to the living families. Most of them cry, and "
     "that's a good thing."),
    ("tm_tf_lane_lookout", "Deathguard Olin", "forsaken", M, "The Burnt Lane",
     "I watch the east road from the end of the lane for anything coming over from Durnholde. It's quiet most "
     "nights, and I like it that way."),
]
