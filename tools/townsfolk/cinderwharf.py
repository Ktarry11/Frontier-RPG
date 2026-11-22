"""Cinderwharf's people: the Ashclaim's town on Tempest Isle, a goblin wharf welded onto a Dark Iron hold (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." Dark Iron dwarves in the Hold, goblins on the Wharf, both of them in the Seam, and a few orcs and
Earthborn who came for the work. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Hold
    ("cwf_tf_hold_guard", "Hearthguard Brun Ashfist", "dwarf", M, "The Hold",
     "The gatehouse was built from Khaz Varun's own stone, carried here block by block. The goblins say that's freight, and we say it's coming home."),
    ("cwf_tf_hall_steward", "Steward Agna Emberbrow", "dwarf", F, "The Hold",
     "The Thane's Hall gets swept, polished and guarded like it's the old throne room. He says it's too grand for a claim office, and he never asks us to stop."),
    ("cwf_tf_hold_elder", "Old Gorm Cindervein", "dwarf", M, "The Hold",
     "My grandfather's grandfather was born in Khaz Varun, before the mountain took it. Now I'm living in its stones, and it feels like visiting relatives."),
    ("cwf_tf_hold_child", "Little Hilde Ashfist", "dwarf", F, "The Hold",
     "My father guards the gate, and my mother carves the runes on the gatehouse. When I grow up, I'm going to guard the gate and carve runes on it at the same time."),
    ("cwf_tf_hold_scribe", "Runescribe Torvald Embermark", "dwarf", M, "The Hold",
     "Every stone from Khaz Varun gets its old rune read and written down before it's set. Thora says the claim depends on it, and the stones deserve it anyway."),
    ("cwf_tf_hold_forge_hand", "Bellows Girl Durra", "dwarf", F, "The Hold",
     "Ulfa's forge never cools, and the bellows are mine from dawn till the horn. My arms are the strongest in the Hold, and I've beaten every goblin at wrestling."),
    # ---- the Seam
    ("cwf_tf_seam_inn_regular", "Grumbleton Sprocket", "goblin", M, "The Seam",
     "Dolla's inn is the one building where dwarves and goblins drink at the same tables. Every night there's an argument, and every night it ends in a toast."),
    ("cwf_tf_seam_dwarf_regular", "Old Barra Coalseam", "dwarf", F, "The Seam",
     "The goblins drink too fast and the dwarves drink too slow, so the inn sells a lot of both. Dolla's getting rich from the difference, and nobody minds."),
    ("cwf_tf_seam_porter", "Porter Kragg", "orc", M, "The Seam",
     "Came over from Saltspur for the work, because Cinderwharf pays better than anywhere on the coast. The dwarves don't talk, the goblins don't stop, and I carry."),
    ("cwf_tf_seam_clerk_hand", "Ledger Hand Sami Gupta", "human", M, "The Seam",
     "Insurance actuary from Mumbai, and now I help Priya work out what the goblins owe the dwarves. The answer changes every week, and somebody always disagrees."),
    ("cwf_tf_seam_cobbler", "Cobbler Fizzik Sole", "goblin", M, "The Seam",
     "Dwarven boots and goblin boots get mended at the same bench, and they're nothing alike. The dwarves want them heavier, and the goblins want pockets."),
    ("cwf_tf_seam_widow", "Widow Gerta Slagbrow", "dwarf", F, "The Seam",
     "My husband died in the first dig at the old gate, and the Thane gave me a house in the Seam. I'm close to the Hold and close to the inn, and both help."),
    ("cwf_tf_seam_earth_cook", "Ana Lima", "human", F, "The Seam",
     "Cooking in Dolla's kitchen for dwarves who want everything spicy and goblins who want everything fried. Bahia trained me for both, so I'm the only cook who lasted."),
    # ---- the Wharf
    ("cwf_tf_wharf_crane", "Crane Jockey Zizzle", "goblin", F, "The Wharf",
     "The crane gantry lifts ore off the barges and onto the ships, and it's mine to drive. It's dropped a crate exactly twice, and neither time was my fault."),
    ("cwf_tf_wharf_docker", "Docker Grub Rattlebolt", "goblin", M, "The Wharf",
     "Cargo gets stacked where it lands and sorted when somebody shouts. Skezz shouts a lot, so the wharf stays mostly sorted."),
    ("cwf_tf_wharf_rigger", "Rigger Nell Hookline", "goblin", F, "The Wharf",
     "Ropes, pulleys and nets for every ship on the wharf, spliced by hand. Goblin knots hold, and dwarf knots hold forever, and nobody can untie either."),
    ("cwf_tf_wharf_sailor", "Sailor Mok", "orc", M, "The Wharf",
     "The ore ships run from Cinderwharf to Saltspur and back, and the crossing's rough. The storms here hit like a war hammer, and the ships still come home."),
    ("cwf_tf_wharf_kid", "Squirt Gearsnap", "goblin", M, "The Wharf",
     "Running messages between the wharf and the Hold pays a copper a trip. The dwarves tip in iron nails, and I've got a bucket of them saved up."),
    ("cwf_tf_wharf_earth_welder", "Siobhan Doyle", "human", F, "The Wharf",
     "Shipyard welder from Belfast, and the goblins can't believe how fast I fix their hulls. They keep asking what spell I use, and I keep telling them it's practice."),
    # ---- the Shrine Terrace
    ("cwf_tf_shrine_acolyte", "Acolyte Varn Emberhold", "dwarf", M, "The Shrine Terrace",
     "The shrine burns for the ones who died when Khaz Varun fell, and for the ones who've died digging it out. Keeper Morn says the fire doesn't know the difference."),
    ("cwf_tf_shrine_pilgrim", "Pilgrim Ilsa Forgeheart", "dwarf", F, "The Shrine Terrace",
     "Came all the way from the Burning Steppes to see the old city's gate with my own eyes. The terrace looks right at it, and I've been looking for a week."),
    ("cwf_tf_shrine_goblin", "Vex Ticktock", "goblin", F, "The Shrine Terrace",
     "Goblins don't usually pray, so the dwarves were surprised to see me at the shrine. My partner died in the dig too, and the fire listens to anyone."),
    # ---- the Salvage Yard
    ("cwf_tf_salvage_sorter", "Sorter Gizmo Rustcog", "goblin", M, "The Salvage Yard",
     "Everything that comes out of the old city gets sorted into three piles: sellable, useful, and haunted. The haunted pile's bigger than you'd think."),
    ("cwf_tf_salvage_dwarf", "Salvager Holm Blackbar", "dwarf", M, "The Salvage Yard",
     "The goblins call it salvage, and the dwarves call it our grandfathers' things. Tazz pays us a share, so we've agreed to call it both."),
    ("cwf_tf_salvage_smoker", "Smoker Brakka", "orc", F, "The Salvage Yard",
     "The smokehouse feeds the dig crews, and the dig crews eat like wolves. Smoked fish from the wharf, smoked boar from Saltspur, and nobody complains."),
]
