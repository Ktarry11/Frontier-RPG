"""Light's Hope Chapel's people: the Argent Dawn's chapel town in the Eastern Plaguelands (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." Mostly humans of the Dawn and of Crown Guard's old camp, with the dwarves, high elves and Forsaken the
Dawn takes in, and the Earthborn who came to nurse and dig. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Chapel Square
    ("lhc_tf_az_acolyte", "Acolyte Merrin Ashe", "human", F, "The Chapel Square",
     "The chapel's bell rings at dawn, noon and dusk, and the dead outside the walls hate all three. You can hear them go quiet when it starts."),
    ("lhc_tf_az_pilgrim", "Pilgrim Otto Brenner", "human", M, "The Chapel Square",
     "Walked all the way from Southshore to pray on this ground before I die. The Dawn says the walking was the prayer, and the kneeling's just resting."),
    ("lhc_tf_dwarf_chaplain", "Brother Hamund Stoutheart", "dwarf", M, "The Chapel Square",
     "Ironforge sent me to help the Dawn, and the Dawn put me in charge of the candles. Four hundred candles, and every one of them lit by my hand."),
    ("lhc_tf_highelf_scribe", "Scribe Elandria Sunfall", "blood_elf", F, "The Chapel Square",
     "Every soul the Dawn lays to rest gets written in the chapel's great book. The book's on its third volume, and I've started a fourth."),
    ("lhc_tf_az_bellringer", "Young Pell Mercer", "human", M, "The Chapel Square",
     "The bell rope takes both my arms and all my weight, and Brother Hamund says I'll grow into it. My shoulders say I'm growing into it already."),
    # ---- the Infirmary
    ("lhc_tf_az_orderly", "Orderly Bettine Crowe", "human", F, "The Infirmary",
     "The field hospital takes anyone the plague hasn't finished, and some it has. Sergeant Reyes sorts them at the door, and we carry them where she points."),
    ("lhc_tf_earth_nurse", "Hannah Schulz", "human", F, "The Infirmary",
     "Twenty years as a nurse in Hamburg, and the plague here is nothing like anything we had. The Light helps, and clean bandages help nearly as much."),
    ("lhc_tf_az_patient", "Old Corwin Hale", "human", M, "The Infirmary",
     "Three weeks in the hospital now, and the fever's finally broken. The nurses won't let me out until I can walk to the gate and back, so I practise."),
    ("lhc_tf_kitchen_girl", "Dory Lowe", "human", F, "The Infirmary",
     "Greta's my aunt, and her kitchen feeds everyone in the chapel town. Soup for the sick, stew for the soldiers, and bread for the lot of them."),
    # ---- the Command Row
    ("lhc_tf_az_runner", "Runner Gil Ashby", "human", M, "The Command Row",
     "Every report from the Tyr's Hand road comes through the command tent, and I carry the answers back. My boots wear out faster than the orders do."),
    ("lhc_tf_dwarf_armourer", "Armourer Brina Coalfist", "dwarf", F, "The Command Row",
     "The Dawn's plate comes in dented and goes out straight, and the dents get worse every month. Whatever's hitting them keeps getting bigger."),
    ("lhc_tf_highelf_ranger", "Ranger Thalien Dawnsong", "blood_elf", M, "The Command Row",
     "Quel'Thalas sent a few of us south to scout for the Dawn. The plague's worse than they told us at home, and the people fighting it are braver."),
    ("lhc_tf_az_bat_boy", "Stable Lad Wil", "human", M, "The Command Row",
     "The bats at the perch frighten the new recruits, and they don't frighten me at all. Aldous says I've got the hands for it, gentle and quick."),
    ("lhc_tf_forsaken_penitent", "Penitent Ada Ward", "forsaken", F, "The Command Row",
     "The Dawn lets me stay because I asked to serve, and because I've never once raised my hand to the living. Some of them still won't look at me."),
    # ---- Crown Guard's Corner
    ("lhc_tf_az_cg_sentry", "Sentry Hal Burrows", "human", M, "Crown Guard's Corner",
     "Crown Guard's camp held the tower road for two years before we moved behind these walls. I miss the tower, and I don't miss the nights out there."),
    ("lhc_tf_az_cg_wife", "Moll Tolliver", "human", F, "Crown Guard's Corner",
     "My husband rides with the outriders, and I keep the well and the horses' water. The well's the only clean water for a day's walk, so it's a proper job."),
    ("lhc_tf_az_cg_boy", "Little Kit Tolliver", "human", M, "Crown Guard's Corner",
     "My father's horse is the fastest in Crown Guard, and one day it'll be mine. The captain says I've got to grow a foot first, so I'm eating everything."),
    ("lhc_tf_earth_engineer", "Rafael Mendes", "human", M, "Crown Guard's Corner",
     "Civil engineer from Porto, and I rebuilt Crown Guard's palisade when we came in from the tower. The Dawn prays over the posts, and I make sure they're straight."),
    # ---- the Cemetery
    ("lhc_tf_az_gravedigger", "Digger Tam Holloway", "human", M, "The Cemetery",
     "Every grave in this cemetery gets dug deep and blessed twice, so nobody in it gets up again. Ten years of digging, and not one of mine has walked."),
    ("lhc_tf_az_mourner", "Widow Ellis", "human", F, "The Cemetery",
     "My son's buried here, by the east wall where the sun comes up first. Edda says he'd want me to stop visiting every day, and she's probably right."),
    ("lhc_tf_dwarf_mason", "Mason Gorrin Flintcutter", "dwarf", M, "The Cemetery",
     "Headstones carved for everyone the Dawn buries, even the ones without a name. Those get a sun and a date, and the Light knows the rest."),
    # ---- the Gate Road
    ("lhc_tf_az_gate_guard", "Guardsman Rolf Carrow", "human", M, "The Gate Road",
     "Nothing dead gets through this gate, and the ground itself sees to that. I watch for the living who mean harm, and that's a harder job."),
    ("lhc_tf_az_carter", "Carter Joan Pike", "human", F, "The Gate Road",
     "Supplies come up the spur road by cart from Chillwind's direction, and the cart's mine. The horse knows the way better than I do, and he's braver."),
    ("lhc_tf_earth_teacher", "Amara Nwosu", "human", F, "The Gate Road",
     "A primary teacher from Accra, teaching the chapel's orphans their letters by the gatehouse. They're the bravest children alive, and the hardest to make sit still."),
    ("lhc_tf_highelf_child", "Little Saelis", "blood_elf", F, "The Gate Road",
     "My mother scouts with the rangers, and I wait for her by the gate every evening. She always comes back, and she always brings me a feather."),
]
