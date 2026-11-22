"""Aurelion's people: a thousand-year city that's lived in, ring by ring (21 Nov 2026).

Kyle: "why is a captial so fucking empty? And everyone is in two districts", and "These people have lived here 1000s of
years". Every ring gets its own residents going about their day: the plaza's idlers and gossips, the palace staff, the
council's clerks, students and tutors, gardeners, the Skydocks' crews, the North Gate's travellers, the Eighth's Rest's
refugees, and a few ground-walkers finding their feet. None of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    ("au_tf_bridge_sweeper", "Old Pell Arro", "aetherian", M, "The Bridgefoot",
     "Fifty years sweeping this bridge every morning, and my father before me. You'd be amazed what people "
     "drop when they see the city for the first time."),
    ("au_tf_porter", "Porter Liss Vandry", "aetherian", F, "The Bridgefoot",
     "Bags, crates, a whole family's furniture once. If it came over the bridge, I've probably carried it up a"
     " ring. My knees would like the council to build a lift."),
    ("au_tf_bridge_child", "Mira Corse", "aetherian", F, "The Bridgefoot",
     "My mother says I mustn't stare at the ground-walkers, so I'm looking at your boots instead. They're very"
     " dirty. Is it all dirt down there?"),
    ("au_tf_orc_traveller", "Grunt Harnak", "orc", M, "The Bridgefoot",
     "A letter for the Embassy, and nobody warned me about the bridge. Rope bridges over lava never turned my "
     "stomach like this one did."),
    ("au_tf_plaza_gossip", "Dame Orla Penmore", "aetherian", F, "The Grand Plaza",
     "What the herald reads in the plaza is only half the news. What everyone says about it afterwards is the "
     "better half."),
    ("au_tf_plaza_painter", "Tobin Arle", "aetherian", M, "The Grand Plaza",
     "Every painter in Aurelion has painted the Spire from this plaza for six hundred years. Mine has more "
     "clouds in it, at least."),
    ("au_tf_plaza_couple_a", "Fenna Strake", "aetherian", F, "The Grand Plaza",
     "We met on this plaza forty years ago, and we still walk it every evening. He says it's for the view. I "
     "know it's because the pastry cart stops here."),
    ("au_tf_plaza_couple_b", "Wendel Strake", "aetherian", M, "The Grand Plaza",
     "My wife will tell you I come for the pastries, and she's right. The view's lovely too, but the view "
     "doesn't come with honey."),
    ("au_tf_plaza_tauren", "Hulda Grainmane", "tauren", F, "The Grand Plaza",
     "My people tell the time by the sun on the plains, and up here it rises so close I could almost touch it."
     " I've stood on this plaza every morning since I arrived, and I'm not tired of it yet."),
    ("au_tf_palace_steward", "Steward Callis Moor", "aetherian", M, "The Spire Palace",
     "The palace has a hundred and forty rooms, and I know where every key is kept. Please don't touch the "
     "banisters. They were polished this morning, and they'll be polished again tonight."),
    ("au_tf_palace_lamplighter", "Lamplighter Sefa Dunmere", "aetherian", F, "The Spire Palace",
     "Every lamp on the Spire is lit by hand at dusk. The crystal could do it on its own, but the keepers say "
     "a city should remember how to light its own lamps."),
    ("au_tf_palace_guard", "Spireguard Anvel Roke", "aetherian", M, "The Spire Palace",
     "My house has stood guard at the Spire for nineteen generations. Nobody's tried to get in for about four "
     "hundred years, but we stand here anyway, in case someone forgets that."),
    ("au_tf_council_clerk", "Clerk Ennis Varrow", "aetherian", M, "The Council Ring",
     "Six hours yesterday arguing over the wording of a single sentence, and every word's in my notes. "
     "You're welcome to read it."),
    ("au_tf_council_page", "Page Rilla Sorn", "aetherian", F, "The Council Ring",
     "I carry messages between the houses. Half of them are invitations to dinner, and the other half are "
     "polite ways of saying no to the first half."),
    ("au_tf_council_petitioner", "Haddon Kell", "aetherian", M, "The Council Ring",
     "The steps outside my house on the Fourth Ring have been cracked for eleven years. The council might fix "
     "them in the twelfth."),
    ("au_tf_council_old_house", "Lady Vessaline Harrow", "aetherian", F, "The Council Ring",
     "The House of Harrow has had a seat on the council since the Third Ring was laid. We don't say much these"
     " days, but we listen to everything, and we remember it."),
    ("au_tf_student_late", "Ivo Brenn", "aetherian", M, "The Academies",
     "A lecture on crystal harmonics is starting without me, and it's dreadfully dull. Please don't tell "
     "Master Oune you saw me out here."),
    ("au_tf_student_keen", "Selka Morrow", "aetherian", F, "The Academies",
     "Is it true the ground has libraries? Real ones, with books nobody up here has read? I've asked everyone "
     "on the faculty and none of them will give me a straight answer."),
    ("au_tf_tutor", "Tutor Ambrose Leclair", "aetherian", M, "The Academies",
     "Thirty-one years teaching the same first-year course, and this year three students asked what the ground"
     " thinks of us. There wasn't an answer to give them."),
    ("au_tf_archivist", "Archivist Junia Caul", "aetherian", F, "The Academies",
     "The Academy archive holds eight hundred years of lecture notes. Most of them disagree with each other, "
     "which the faculty considers a sign of good health."),
    ("au_tf_human_scholar", "Priya Nair", "human", F, "The Academies",
     "Chemistry at a university in Kerala, and now the Academy's lectures, where everyone is politely "
     "confusing. Never so happily lost in my life."),
    ("au_tf_garden_apprentice", "Pim Ashgrove", "aetherian", M, "The Gardens",
     "My aunt Tamsin runs the Gardens, and I count the gold apples every morning. There were three hundred and"
     " twelve today. If there are fewer tomorrow, I'll know it was you."),
    ("au_tf_garden_reader", "Calla Venn", "aetherian", F, "The Gardens",
     "The Gardens are the only quiet place in the Inner Ring. The trees are older than the Academy, and "
     "they've heard every argument the city ever had."),
    ("au_tf_garden_fisher", "Grandfather Oskel", "aetherian", M, "The Gardens",
     "The fish in this pool know my step on the path, and they all swim to the near edge. The young ones think"
     " it's a trick, but it's just bread."),
    ("au_tf_garden_mother", "Delphine Arcott", "aetherian", F, "The Gardens",
     "I bring the children to the Gardens so they'll run somewhere soft. My youngest tried to climb an apple "
     "tree last week, and the gardener still hasn't forgiven either of us."),
    ("au_tf_garden_troll", "Zul'jani", "troll", F, "The Gardens",
     "Dey grow dese trees in de sky with no jungle round dem, and still dey come up strong. I been askin' de "
     "gardener how she does it. She says patience, mon, and a thousand years."),
    ("au_tf_embassy_goblin", "Sprocket Fizzlegear", "goblin", M, "The Ground Embassy",
     "I'm here for the Cartel, pricing crystal before anyone else does. These Aetherians bargain like they've "
     "got a thousand years to do it, and I suppose they have."),
    ("au_tf_embassy_clerk", "Clerk Wren Haddock", "aetherian", F, "The Ground Embassy",
     "Every visitor from the ground gets their papers stamped at this desk. The Horde's envoys use the forms "
     "to start fires, so there's a bucket by the desk now."),
    ("au_tf_embassy_blood_elf", "Envoy Saelis Dawnbrook", "blood_elf", F, "The Ground Embassy",
     "The Conclave sent me to open talks with the High Houses. My people kept records for seven thousand "
     "years, and we're still the young ones in this room."),
    ("au_tf_embassy_transplant", "Daniel Okonkwo", "human", M, "The Ground Embassy",
     "A schoolteacher from Leeds, explaining the ground to the council. Two hours last week describing a cow, "
     "and they were very polite about it."),
    ("au_tf_dock_rigger", "Rigger Tamsen Hale", "aetherian", F, "The Skydocks",
     "The long-haulers are older than my grandmother, and they creak like her too. Not once have they dropped "
     "anyone off the rigging."),
    ("au_tf_dock_captain", "Captain Orrin Feld", "aetherian", M, "The Skydocks",
     "Four ports on the eastern route when I started flying it, twenty-six years ago, and two now. We fly the "
     "whole route anyway, in case the others come back."),
    ("au_tf_dock_loader", "Brask Tolley", "aetherian", M, "The Skydocks",
     "Crystal goes out and grain comes in, every week for my whole life. Lately it's grain from the ground, "
     "and it's better than ours, which the farmers on the islands won't hear a word about."),
    ("au_tf_dock_watcher", "Old Ninna Gale", "aetherian", F, "The Skydocks",
     "My husband flew the northern route, and he didn't come back from the last trip. I come to the docks "
     "every evening to watch the ships come in. It's a good place to remember someone."),
    ("au_tf_dock_cabin_boy", "Tam Feld", "aetherian", M, "The Skydocks",
     "My father's the captain of the Steadfast, and next year I'm allowed to sail with him. I've already "
     "learned all the knots, even the ones he says I'll never need."),
    ("au_tf_dock_orc", "Durza Ironhand", "orc", F, "The Skydocks",
     "The Horde wants to know if these airships can carry soldiers. I've spent a week on the docks and I still"
     " can't work out what holds them up. The captains just smile when I ask."),
    ("au_tf_gate_carter", "Carter Joss Merrin", "aetherian", M, "The North Gate",
     "Every ten days the supply cart goes down to the low islands. The road's long and quiet, and the horse is"
     " a good listener."),
    ("au_tf_gate_pilgrim", "Sister Aveline Crest", "aetherian", F, "The North Gate",
     "I'm walking to the old shrines on the islands, the way my mother did and her mother before her. It takes"
     " a month there and back. The walking is most of the point."),
    ("au_tf_gate_recruit", "Gatehand Rolf Teague", "aetherian", M, "The North Gate",
     "This is my first season on the gate. The warden says nothing ever happens out here, and so far he's "
     "right. I keep my spear polished anyway, just in case."),
    ("au_tf_gate_farmer", "Bettany Rook", "aetherian", F, "The North Gate",
     "Eggs and cheese from the low islands fetch twice what they're worth in the city. Don't tell the Fourth "
     "Ring, or they'll start keeping chickens."),
    ("au_tf_rest_widow", "Marta Ashlane", "aetherian", F, "The Eighth's Rest",
     "Sixty years on the Eighth Ring, three streets from the outer rail, and now a borrowed room with my "
     "sister. The council's kind, but kindness isn't home."),
    ("au_tf_rest_mason", "Mason Gideon Thorne", "aetherian", M, "The Eighth's Rest",
     "I built half the houses on the Eighth Ring, and I watched them go. I've drawn up plans to build it "
     "again. The council keeps saying next year, and I keep drawing."),
    ("au_tf_rest_children", "Lio Ashlane", "aetherian", M, "The Eighth's Rest",
     "Grandmother tells me about the Eighth Ring every night, because I was too small to remember it. Our "
     "house had a blue door, and you could see the whole sky from the step."),
    ("au_tf_rest_musician", "Fiddler Ansel Moor", "aetherian", M, "The Eighth's Rest",
     "The old Eighth Ring songs, every evening by the soup pot. The young ones don't know the words yet, and "
     "somebody has to remember how they go."),
    ("au_tf_rest_nurse", "Healer Brisa Lowell", "aetherian", F, "The Eighth's Rest",
     "I tend whoever's sick in the Rest, which is mostly the old folk and their hearts. The council sends me "
     "herbs. What they really need is somewhere that feels like theirs again."),
    ("au_tf_rest_scavenger", "Corwin Fask", "aetherian", M, "The Eighth's Rest",
     "I go out to the edge of the Eighth Ring when the wind's low and bring back whatever I can reach. Last "
     "week it was a door knocker shaped like a fish. Old Marta cried when she saw it."),
    ("au_tf_ring_mourner", "Thessaly Wren", "aetherian", F, "The Eighth Ring",
     "My parents' house stood about there, where the stone ends. I come out once a month and leave flowers on "
     "the edge. The wind always takes them, but I think they'd like that."),
    ("au_tf_ring_surveyor", "Surveyor Hollis Grey", "aetherian", M, "The Eighth Ring",
     "The council wants to know if what's left of the Eighth Ring is safe to walk. Most of it is, and some of "
     "it very much isn't. Stay on the stones I've marked with chalk."),
    ("au_tf_trainee", "Kael Durren", "aetherian", M, "The Trainers' Ring",
     "I've been training with the spear for six years and Trainer Dorrow still corrects my feet every single "
     "morning. He says that's how he knows I'm improving."),
    ("au_tf_trainee_tired", "Wynne Halloway", "aetherian", F, "The Trainers' Ring",
     "We've been running drills since dawn and my arms have stopped speaking to me. The ground-walkers who "
     "train here make it look easy, and I'd like to know their secret."),
]
