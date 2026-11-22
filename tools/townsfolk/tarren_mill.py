"""Tarren Mill's people: the mill town in the Hillsbrad foothills, the Forsaken's apothecarium beside it (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." Tarren Mill leans two ways at once: the living millers and farmers who stayed when the Forsaken came,
and the Forsaken who run the apothecarium and the garrison. An orc or two with the wind-riders. None of them gives a
quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Mill Yard
    ("tm_tf_mill_hand", "Millhand Joss Tanner", "human", M, "The Mill Yard",
     "I carry the sacks from the millstone to the granary, a hundred a day in the good season. The Forsaken buy most of "
     "the flour now, and they pay on time, which the old lord never did."),
    ("tm_tf_flour_wife", "Martha Reed", "human", F, "The Mill Yard",
     "I'm the miller's sister, and I bake the bread for the whole town from his flour. The Forsaken can't taste it, but "
     "they buy it for the living ones who pass through, and they always say thank you."),
    ("tm_tf_smith_apprentice", "Apprentice Hal Cobb", "human", M, "The Mill Yard",
     "I shoe the horses and mend the mill's ironwork, and the smith says I'm nearly ready to work on my own. The "
     "Forsaken bring me their swords too, and I try not to look at what's dried on them."),
    ("tm_tf_forsaken_carter", "Carter Abel Dunn", "forsaken", M, "The Mill Yard",
     "I drove a cart through this town when I was alive, and I drive one through it now I'm dead. The living ones were "
     "frightened of me at first, and now they wave."),
    # ---- the Apothecarium
    ("tm_tf_vat_tender", "Tender Morwenna", "forsaken", F, "The Apothecarium",
     "I stir the vats on the platform, and I've learned to keep my face out of the fumes. I don't need to breathe, but "
     "my eyes still water, which seems unfair."),
    ("tm_tf_apoth_courier", "Courier Felix Grave", "forsaken", M, "The Apothecarium",
     "I carry sealed crates from the apothecarium to the bat roost, and I never ask what's inside. Some of them are "
     "heavier on the way back than they were on the way out."),
    ("tm_tf_garrison_grunt", "Deathguard Pell", "forsaken", M, "The Apothecarium",
     "I guard the tents round the apothecarium, and the living townsfolk give us a wide berth. I don't blame them, and "
     "I give the vats an even wider one."),
    ("tm_tf_orc_rider", "Wind-Rider Groka", "orc", F, "The Apothecarium",
     "I fly the wind-riders out of the roost for Ghulrak, and Tarren Mill's the strangest posting I've had. The dead "
     "and the living share one street here, and nobody's killed anybody yet."),
    ("tm_tf_bat_keeper_aide", "Hobble", "forsaken", M, "The Apothecarium",
     "I keep the bats fed beside the wind-riders' roost, and the bats and the wyverns don't like each other. Most "
     "nights I'm just keeping the peace between them."),
    # ---- the Weir
    ("tm_tf_weir_fisher", "Fisher Old Tom", "human", M, "The Weir",
     "I fish below the sluice, where the trout gather in the eddies. My father fished here and his father too, and the "
     "Forsaken don't eat fish, so I've got it all to myself."),
    ("tm_tf_sluice_boy", "Pip Weller", "human", M, "The Weir",
     "I help Pate open and close the sluice gates when the river's high. He says the whole mill depends on us, and I "
     "think he's only half joking."),
    ("tm_tf_washerwoman", "Washerwoman Sal", "human", F, "The Weir",
     "I wash the town's linen in the millrace, and I wash the Forsaken's too, now. Their sheets don't get dirty the same "
     "way, and I've stopped asking why."),
    # ---- Mill Row
    ("tm_tf_cottage_mother", "Goodwife Ada Pell", "human", F, "Mill Row",
     "My husband went off to the war and never came back, and the Forsaken asked me if I wanted him to. I said "
     "no, and they respected that, and I've never forgotten it."),
    ("tm_tf_cottage_child", "Little Bess", "human", F, "Mill Row",
     "The Forsaken man down the lane gives me sweets on market day. My mother says not to take them, but they're always "
     "wrapped, and he always smiles, even if his smile's a bit crooked."),
    ("tm_tf_inn_regular", "Ned Barlow", "human", M, "Mill Row",
     "I drink at the inn every evening and argue with the Forsaken about the old king. They knew him, some of them, and "
     "they win most of the arguments, which I find annoying."),
    ("tm_tf_stable_girl", "Molly Teague", "human", F, "Mill Row",
     "I help my father with the horses, and they won't go near the Forsaken's skeletal ones. I think they're jealous, "
     "because the skeletal horses never get tired."),
    ("tm_tf_forsaken_neighbour", "Mr. Pennick", "forsaken", M, "Mill Row",
     "I lived in the cottage at the end of the row before I died, and I came back to it after. The neighbours took a "
     "while to warm up to me, and now they bring me their broken clocks to fix."),
    # ---- the Chapel Hill
    ("tm_tf_chapel_sexton", "Sexton Ambrose", "human", M, "The Chapel Hill",
     "I keep the chapel graveyard, and I've had to learn which graves are empty on purpose. The Forsaken who climbed out "
     "of them sometimes come back to tidy them, which I find very touching."),
    ("tm_tf_chapel_widow", "Widow Clara Finch", "human", F, "The Chapel Hill",
     "I pray at the chapel every morning for the living and the dead both. The chaplain says the Light doesn't choose "
     "sides, and I've decided to believe him."),
    ("tm_tf_hill_shepherd", "Shepherd Gil", "human", M, "The Chapel Hill",
     "I graze my sheep on the hill above the chapel, and they've never once wandered toward the apothecarium. Sheep are "
     "smarter than people give them credit for."),
    # ---- the Burnt Lane
    ("tm_tf_burnt_cottage", "Old Agatha", "human", F, "The Burnt Lane",
     "My cottage burned in the war, and I live in the shed behind it now. The Forsaken offered to rebuild it, and I "
     "told them I'd rather keep the ashes, because they're mine."),
    ("tm_tf_lane_scavenger", "Scavenger Ruth", "forsaken", F, "The Burnt Lane",
     "I pick through the burnt houses for anything worth keeping, and I give the keepsakes back to the living families. "
     "Most of them cry, and I've learned that's a good thing."),
    ("tm_tf_lane_lookout", "Deathguard Olin", "forsaken", M, "The Burnt Lane",
     "I watch the east road from the end of the lane for anything coming over from Durnholde. It's quiet most nights, "
     "and I like it that way."),
]
