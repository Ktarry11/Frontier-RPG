"""The Great Settlement's people: the Highbough Tribes making a city in the World Tree (21 Nov 2026).

Kyle: "we need towns as hubs...POPULATED towns". The tribes climbed the tree when the world broke and built a city in
its heart, so the people here are still making it home: families in the Lantern Ward, hands on the Trades Terrace,
the Market's stallholders and idlers, bat-keepers and scholars at the Roost, the faithful at the Falls and the
Chieftain's Rise. None of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    ("gs_tf_tea_drinker", "Old Jin'zo", "troll", M, "The Market",
     "Every mornin' I drink my tea at de same table and watch de whole tree wake up. You learn a lot about a "
     "city from who's late to work, mon, and today it was de baker again."),
    ("gs_tf_market_kid", "Little Ree'na", "troll", F, "The Market",
     "My mama says I can't go near de edge, so I count de lanterns instead. I got to two hundred and six "
     "before I lost my place, and now I gotta start over."),
    ("gs_tf_stall_helper", "Kaz'ru", "troll", M, "The Market",
     "De stallholders pay in fruit and gossip for carryin' crates. De fruit's better, but de gossip lasts "
     "longer, so it's hard to choose."),
    ("gs_tf_market_elder", "Grandmother Zalla", "troll", F, "The Market",
     "When we first climbed de tree dere was nothin' up here but bark and birds. Now dere's a market, a bank "
     "and a goblin sellin' hats. I don't know if dat's progress, but it's loud."),
    ("gs_tf_goblin_hatter", "Fizzla Brightbolt", "goblin", F, "The Market",
     "Trolls love hats, as it turns out, and business has never been better. Don't tell the Cartel, or they'll"
     " want a cut."),
    ("gs_tf_lantern_lighter", "Lanternman Ozzi", "troll", M, "The Lantern Ward",
     "Every lantern in de ward gets lit at dusk, and dere's more every week as more families climb up. De "
     "ladder's gettin' tired, mon, and so am I."),
    ("gs_tf_ward_mother", "Ama'tika", "troll", F, "The Lantern Ward",
     "Four little ones and a hut de size of a rowboat. Dey sleep stacked like firewood, and still somebody "
     "ends up in my hammock every night."),
    ("gs_tf_ward_builder", "Builder Tanzo", "troll", M, "The Lantern Ward",
     "De huts on de lower platforms ain't pretty, one plank at a time. Every one has held through a storm, and"
     " dat's what matters up here."),
    ("gs_tf_ward_singer", "Sola Nightvine", "troll", F, "The Lantern Ward",
     "Most of de young ones never saw de sea, and dey ask what a wave sounds like. De old songs from de coast "
     "are de closest dey'll get."),
    ("gs_tf_ward_twins", "Rak and Ruk", "troll", M, "The Lantern Ward",
     "We're twins, and we're not allowed to stand on de same platform any more because of what happened last "
     "week. Nobody got hurt, mon, but de chickens are still upset."),
    ("gs_tf_ward_human", "Marisa Castell", "human", F, "The Lantern Ward",
     "A midwife from Valencia, delivering troll babies in a city inside a tree. The mothers here are tougher "
     "than anyone at home, and they laugh a lot more."),
    ("gs_tf_forge_hand", "Bellows Ujo", "troll", M, "The Trades Terrace",
     "Too much fire in a city made of wood is a bad idea, so de forge stays hot and careful. Dere's always a "
     "bucket of water close by."),
    ("gs_tf_tanner_apprentice", "Neema", "troll", F, "The Trades Terrace",
     "I scrape hides for de tanner from mornin' till night. It smells terrible, but she says I got de best "
     "hands she's seen in years, so I'm stayin'."),
    ("gs_tf_herb_sorter", "Old Mazi", "troll", M, "The Trades Terrace",
     "Half de herbs comin' up from de Lower Boughs are weeds, and de young pickers can't tell yet. One leaf at"
     " a time, dey're learnin'."),
    ("gs_tf_cook_helper", "Pala Greenroot", "troll", F, "The Trades Terrace",
     "More tears over de cook's onions dan over any man, and de stew's worth every one. Come back at supper "
     "and see."),
    ("gs_tf_orc_smith", "Grosh Emberfist", "orc", M, "The Trades Terrace",
     "Orgrimmar sent me up to teach the trolls our forging, and they ended up teaching me how to work with "
     "wood. I've never made a lighter axe in my life."),
    ("gs_tf_bat_keeper", "Batkeeper Zuli", "troll", F, "The Roost",
     "Every bat pup born in de roost gets a name. Dat one's Trouble, and you can guess why, because he bit de "
     "chieftain once."),
    ("gs_tf_bat_trainee", "Kel'jin", "troll", M, "The Roost",
     "Only fallen off twice learnin' to fly de bats. Both times de bat came back for me, which de keeper says "
     "is a very good sign."),
    ("gs_tf_scholar", "Scholar Wenzi", "troll", F, "The Roost",
     "Last month a bone de size of a canoe fell out of de clouds onto de branches. Nobody in de hall can say "
     "what it came from."),
    ("gs_tf_scholar_assistant", "Tobi Halvard", "human", M, "The Roost",
     "I was a museum curator in Oslo, and Scholar Wenzi lets me label her finds. I've never had a collection "
     "like this one, and I've never had to label things in troll."),
    ("gs_tf_falls_washer", "Mother Ti'ana", "troll", F, "The Falls",
     "De water in de pool under de falls comes from somewhere above us, and it's never once run dry. De loa-"
     "speaker calls it a gift, and de ward's clothes agree."),
    ("gs_tf_falls_fisher", "Old Bonzu", "troll", M, "The Falls",
     "Dere's fish in de falls pool, little silver ones, and nobody knows how dey got up here. I catch dem "
     "anyway. Dey taste like de river back home."),
    ("gs_tf_falls_pilgrim", "Saya Moonleaf", "troll", F, "The Falls",
     "I leave a flower at de waterfall shrine every mornin' for my brother. He didn't make de climb. De shrine"
     " keeper says de water carries it down to him."),
    ("gs_tf_falls_lovers", "Jako", "troll", M, "The Falls",
     "De girl from de Lantern Ward is late again, third time dis week. Brought her flowers anyway, because I'm"
     " a fool and I know it."),
    ("gs_tf_palace_guard", "Spearwarden Ozak", "troll", M, "The Chieftain's Rise",
     "Guardin' de Heart Palace mostly means tellin' visitors de chieftain is busy. He usually is, mon, but "
     "sometimes he's just havin' a nap."),
    ("gs_tf_temple_acolyte", "Acolyte Mira'shi", "troll", F, "The Chieftain's Rise",
     "I tend de candles in de loa temple and listen to what de tribes come to say. Most of dem pray for good "
     "weather and healthy children, same as people anywhere."),
    ("gs_tf_tribe_elder", "Elder Rhazu", "troll", M, "The Chieftain's Rise",
     "De Mossjaw tribe's voice on de chieftain's council is mine. We argue a lot, but we argue up here "
     "together, and dat's better dan we ever managed on de ground."),
    ("gs_tf_bridge_mender", "Ropewright Kanji", "troll", M, "The Great Settlement",
     "I check every bridge rope in de city once a week. It's a long way down to Mossroof, and I've never lost "
     "anybody yet. I'd like to keep it dat way."),
    ("gs_tf_new_arrival", "Zeena Redtusk", "troll", F, "The Great Settlement",
     "My family only climbed up last month. Everybody keeps tellin' me I'll stop lookin' down eventually. I'm "
     "still waitin' for dat to happen."),
    ("gs_tf_lift_rider", "Old Tokka", "troll", M, "The Great Settlement",
     "I ride de Great Lift down to de Lower Boughs and back every day, just for de view. De liftwarden says "
     "I'm de best customer she's got, and I'm de only one who doesn't pay."),
]
