"""The Timbermaw Tunnel's people: the furbolgs who keep the tunnel between Felwood, Moonglade and Winterspring
(22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "Small towns can be 15-20". The tunnel is a Timbermaw waystation,
so its people are furbolgs who live in its galleries: honey-gatherers, path-keepers, cubs and elders, and one or two
travellers who stopped for the honey and didn't leave. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("tmt_tf_waystation_cook", "Cook Barkbelly", "furbolg", M, "The Waystation",
     "Travellers come through the tunnel hungry, so the waystation pot is always full. Honey in everything, because Timbermaw believe honey makes friends."),
    ("tmt_tf_waystation_cub", "Little Moss", "furbolg", F, "The Waystation",
     "The travellers who come through the tunnel are very tall and very strange. Some of them give me sweets, and some of them are scared of me, which is silly."),
    ("tmt_tf_waystation_lamp", "Lamp-Keeper Dimfur", "furbolg", M, "The Waystation",
     "Every lamp in the waystation gallery gets trimmed at noon and at midnight, though nobody down here can tell which is which. The lamps count the time for us."),
    ("tmt_tf_honey_gatherer", "Gatherer Goldpaw", "furbolg", F, "The Honey Galleries",
     "The bees in the honey galleries know Goldpaw's smell, so they mostly don't sting. The honey's worth the stings that do."),
    ("tmt_tf_honey_cub", "Little Sticky", "furbolg", M, "The Honey Galleries",
     "Not allowed to eat the honey before it's jarred, the honeykeeper says. That's a very hard rule for a cub, and it gets broken a lot."),
    ("tmt_tf_root_hall_elder", "Elder Rootbeard", "furbolg", M, "The Root Hall",
     "The great roots in the hall were here before the Timbermaw dug the tunnel. We dug round them, never through, because the roots were first and that's fair."),
    ("tmt_tf_root_hall_weaver", "Weaver Softpaw", "furbolg", F, "The Root Hall",
     "Root fibre makes the softest rope, and the Root Hall has the most roots. Every climbing line in the Hold started as a root in this hall."),
    ("tmt_tf_elders_tender", "Tender Greymuzzle", "furbolg", F, "The Elders' Rest",
     "The oldest Timbermaw sleep in the Elders' Rest, where it's warmest. Somebody has to keep their fires lit and their honey pots full, and that's an honour."),
    ("tmt_tf_elders_storyteller", "Old Thistlecoat", "furbolg", M, "The Elders' Rest",
     "Before the corruption, the Timbermaw were friends with everyone. The stories from that time are the best ones, and they're getting harder to remember."),
    ("tmt_tf_spring_watcher", "Watcher Clearwater", "furbolg", F, "Selva's Spring",
     "Selva's spring is clean, the cleanest water this side of the Hold. Watching it's a small job and an important one, because clean water's rare now."),
    ("tmt_tf_spring_cub", "Little Splashpaw", "furbolg", M, "Selva's Spring",
     "The spring is cold enough to make a furbolg squeak, and the windtalker says that's why it's clean. Bad things don't like the cold."),
    ("tmt_tf_gallery_digger", "Digger Stonepaw", "furbolg", M, "The Lower Galleries",
     "The lower galleries needed shoring after the last rockfall, and every beam was hauled in by hand. The tunnel holds because furbolgs are stubborn."),
    ("tmt_tf_storeroom_keeper", "Keeper Acornsnout", "furbolg", F, "The Storeroom",
     "Nuts, roots, dried fish and honey, enough to feed the tunnel through two winters. Counting it's my job, and eating it's everybody else's."),
    ("tmt_tf_traveller", "Liesel Brandt", "human", F, "The Waystation",
     "A geologist from Austria, walking through a tunnel dug by bear people, and the rock here is fascinating. The honey's even better than the rock, which says a lot."),
    ("tmt_tf_tauren_guest", "Hania Stillwind", "tauren", M, "The Root Hall",
     "The Timbermaw keep the old ways with the earth the same as we do, only underground. The elders let me sit in the Root Hall and listen, and that's a privilege."),
]
