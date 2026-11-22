"""The Bulwark's people: the Forsaken's wall between Tirisfal and the Plaguelands, with the Order of the Pale Flame camped
inside it (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30". Two quarters that don't love each other:
the Forsaken of the wall north of the street, and the Order's people south of it, humans of Lordaeron and the Earthborn
who joined them. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the West Gate
    ("blw_tf_gate_deathguard", "Deathguard Wilkes", "forsaken", M, "The West Gate",
     "Tirisfal's road runs straight through this gate, and so does everybody. The Order's people still flinch when I check their papers, and I enjoy it a little."),
    ("blw_tf_inn_regular", "Old Barnabus", "forsaken", M, "The West Gate",
     "Sabine's inn serves the living ale and the dead nothing at all. I sit here anyway, for the company and the noise, and she doesn't charge me for the chair."),
    ("blw_tf_bat_feeder", "Feeder Molly Gaunt", "forsaken", F, "The West Gate",
     "The bats eat at dusk, and they eat more since the Order moved in. Tobias says it's the smell of living blood, and I say they're just greedy."),
    ("blw_tf_courier", "Courier Ned Ashcroft", "forsaken", M, "The West Gate",
     "Letters from the Undercity come through this gate twice a day, and they all go to the High Executor. She reads every one and burns half of them."),
    # ---- the Forsaken Row
    ("blw_tf_barracks_guard", "Deathguard Ilse Thorne", "forsaken", F, "The Forsaken Row",
     "The barracks hold forty Deathguard, and none of us sleep, so the bunks are for show. We stand the wall in shifts and argue in between."),
    ("blw_tf_mausoleum_keeper", "Keeper Elias Grimm", "forsaken", M, "The Forsaken Row",
     "The mausoleum holds the ones who fell on the wall, the ones who stayed fallen. We bury our own, and we don't let the Plaguelands have them back."),
    ("blw_tf_store_hand", "Shopgirl Agatha Pell", "forsaken", F, "The Forsaken Row",
     "My cousin Ezra runs the store, and I sweep it and count the stock. The Order's people buy more bandages than anyone, which tells you something."),
    ("blw_tf_watchtower", "Watcher Gideon Marsh", "forsaken", M, "The Forsaken Row",
     "From the tower you can see the Plaguelands' first fields, grey from here to the horizon. Something always moves out there, and it's usually not friendly."),
    ("blw_tf_bone_carver", "Carver Hester Moss", "forsaken", F, "The Forsaken Row",
     "Bone wards hung on the wall keep the worst of the dead at a distance. I carve them from what the wall gives us, and the wall's very generous."),
    # ---- the Apothecary's Yard
    ("blw_tf_vat_hand", "Vat Hand Silas Grey", "forsaken", M, "The Apothecary's Yard",
     "The vats bubble day and night, and Dorian won't say what's brewing in them. The smell would kill a living man, and that might be the point."),
    ("blw_tf_wagon_driver", "Wagoner Ruth Cole", "forsaken", F, "The Apothecary's Yard",
     "The wagon shed sends supplies east to the Pale Watch and the Dawn's chapel. The Order pays for the hauling, and they've never once paid late."),
    ("blw_tf_store_keeper", "Storekeeper Abel Dunn", "forsaken", M, "The Apothecary's Yard",
     "Everything in the storehouse is sealed, labelled and watched, because the apothecaries' stores are worth killing for. Nobody's tried yet."),
    ("blw_tf_apoth_student", "Student Imogen Vale", "forsaken", F, "The Apothecary's Yard",
     "Dorian took me as his student after Brill's academy closed. He says I've a gift for poisons, and my mother would've been horrified."),
    # ---- the King's Road
    ("blw_tf_road_sweeper", "Sweeper Tom Barlow", "forsaken", M, "The King's Road",
     "The King's Road through the Bulwark gets swept every night, because the High Executor likes a tidy street. The Order says it's the only tidy thing about us."),
    ("blw_tf_az_peddler", "Peddler Wynn Ashgrove", "human", M, "The King's Road",
     "Living merchant on a dead road, and both sides buy from me because neither trusts the other's store. It's a very profitable kind of hate."),
    ("blw_tf_az_refugee", "Marta Kell", "human", F, "The King's Road",
     "Our farm was west of Andorhal, and the plague took everyone but me. The Order gave me a bed, and the Forsaken gave me directions, and both were kind."),
    # ---- the Order's Lane
    ("blw_tf_az_pf_squire", "Squire Elias Brand", "human", M, "The Order's Lane",
     "The Order came down from Sorrow Hill when the hill went back to the dead. Ser Aldren says the Bulwark's a better post, and I say it's a stranger one."),
    ("blw_tf_az_pf_novice", "Novice Lark Meadows", "human", F, "The Order's Lane",
     "The pale flame in the chapel burns without smoke, and the novices tend it in shifts. It's never gone out, not once since the Order was founded."),
    ("blw_tf_earth_pf_volunteer", "Marek Kowalczyk", "human", M, "The Order's Lane",
     "A firefighter from Krakow, and the Order took me in because I don't panic. The pale flame doesn't burn the way ordinary fire does, and I've stopped trying to understand it."),
    ("blw_tf_earth_pf_cook_hand", "Lucia Romano", "human", F, "The Order's Lane",
     "I help Priya feed the Order's quarter, and between us we make the Bulwark's only proper food. The Forsaken can't taste it, and they still come to watch us cook."),
    ("blw_tf_az_pf_trainee", "Trainee Garret Holt", "human", M, "The Order's Lane",
     "Kofi drills us in the training yard until our shields feel like part of our arms. He says the dead never get tired, so neither can we."),
    ("blw_tf_az_pf_hawk_girl", "Little Tessa", "human", F, "The Order's Lane",
     "Anders lets me feed his hawks if I'm very quiet and very quick. They carry the Order's letters, and one of them carried mine to my grandmother."),
    ("blw_tf_earth_pf_medic", "Dr. Yusuf Demir", "human", M, "The Order's Lane",
     "Trauma surgeon from Ankara, working beside a Forsaken surgeon who doesn't need anaesthetic himself. We disagree on nearly everything, and we save a lot of people."),
    ("blw_tf_az_pf_stable", "Stablehand Joss Burrows", "human", M, "The Order's Lane",
     "The Order's horses live in the stable by the east gate, the furthest corner from the bats. The horses insisted, and they were right to."),
    ("blw_tf_az_pf_chapel_widow", "Widow Agnes Fairweather", "human", F, "The Order's Lane",
     "My husband held the hill with the Order for six years before it fell. Odile lets me keep the chapel's flowers, and they're the only ones in the Bulwark."),
]
