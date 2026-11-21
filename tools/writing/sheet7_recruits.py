# -*- coding: utf-8 -*-
"""Sheet 7: the bears (docs/recruit_art_prompts_sheet7.md), written one at a time as each is placed.

Kyle, 20 Nov 2026: "gruff bears!... some 'real' looking men", sixteen Earth transplants built by real work. The art
landed 21 Nov and is sliced. Kyle, 21 Nov 2026: "Can you move one bear recruit to lower level so the island has 3
recruits", so Rhodri Evans, the scaffolder and rugby prop, came down from the 21-30 band to Dawnhaven as its tank,
beside Liam (the healer) and Haruto. The other fifteen are written when their zones are placed.

The recruit-overhaul voice: whole sentences said out loud, no clipped fragments, no "it's not X, it's Y". Recruits are
strangers to each other, so nobody's text names another.
"""

TRAITS = {
    "rhodri_knight": "Steady, cheerful and immovable. He talks to everyone as if they're on his crew, checks every knot "
                     "twice and sings whether anyone wants him to or not.",
}

BATCH = {
"rhodri_knight": dict(
    greeting="Mind your head, that pole's not tied off yet. I've had scaffolding up the side of Caerphilly Castle, so "
             "one broken gatehouse isn't going to frighten me.",
    backstory=(
        "Rhodri propped for Pontypridd on Saturdays for fifteen years and put up scaffolding the rest of the week, from "
        "terraced streets in the valleys to the walls of Caerphilly Castle. Nobody got past him on the pitch, and "
        "nobody ever fell off anything he built. He woke on the Waking Shore last spring with his boots full of sand, "
        "and by the afternoon he was carrying poles up to Amberwatch. The night the naga came up the beach, fire came "
        "up through him to meet them, and the Conclave's magisters have been arguing about what to call it ever since."),
    before=(
        "A van with his name on the side, a crew of four lads from his own street, and the front row of a club older "
        "than anyone's grandmother.\n\n"
        "He clipped every one of those lads on before they climbed, every single time, and he was the only gaffer in "
        "the valleys who never had a fall."),
    adjustment=(
        "The first week he didn't understand a word the elves said, and he took that better than most, because half "
        "the valleys can't follow him either.\n\n"
        "What got to him was the quiet. There's no match on a Saturday and no singing on the terrace, and there are "
        "no lads. He fills it by building, because a roof going up sounds the same on any world."),
    forward=(
        "He wants Amberwatch roofed before the first proper storm, then the Spire's walls, and then whatever's "
        "next.\n\n"
        "He'd also like a game. Fifteen a side on a flat bit of grass, with anyone daft enough to pack down against "
        "him."),
    now=(
        "Amberleaf Glade, at Amberwatch, up the scaffolding on the old gatehouse with a hammer in his belt and a pole "
        "on his shoulder.\n\n"
        "When there's trouble on the cove road he climbs down, stands at the front and doesn't move. Then he goes back "
        "up and finishes the joint he was on."),
    look=("Welsh man, 38, big, broad and solid, a thick ginger beard, short reddish hair, fair weathered skin, blue "
          "eyes. Heavy crimson plate with dark iron edges and a glowing red sigil, a sword and a tall red shield."),
),
"yiannis_paladin": dict(
    greeting="Ela, come up out of the water, my friend, slowly. You're on Dawnhaven, the sea brought you, and the sea "
             "brings everybody here eventually.",
    backstory=(
        "Yiannis dived for octopus off Chania from the age of nine and beat them soft on the harbour stones for the "
        "tavernas. He sings to the sea when it's rough, and he has since he was sixteen. He woke in the surf of the "
        "Waking Shore two years ago, before the Conclave had a tent up, and the first person he pulled out after "
        "that was an elf girl who wasn't breathing. Light came into his hands while he worked on her, and she "
        "breathed. He's kept the shore ever since."),
    before=(
        "A blue boat in the old harbour at Chania, a wife who could out-argue a bishop, and two daughters, one bound "
        "for Athens and one bound for the sea.\n\n"
        "His grandfather fished those waters and so did his father. He was the careful one, and he had good reason "
        "to be."),
    adjustment=(
        "He talks to his wife and his girls every night, out loud, on the beach, and he doesn't care who hears "
        "him.\n\n"
        "The Conclave's priests asked where he learned to call the Light. He told them on a harbour wall, with a "
        "child who wasn't breathing, and they stopped asking."),
    forward=(
        "He wants nobody the sea gives up on his shore to be lost, ever.\n\n"
        "One day he'd like to sing a song he hasn't sung in thirty years, out loud, for somebody who isn't here to "
        "hear it."),
    now=(
        "Amberleaf Glade, on the Waking Shore, up to his knees in the surf.\n\n"
        "Whoever the sea gives up, he wades in and gets them, wraps them in a blanket and sings them a couplet about "
        "how they looked coming out of the water. The rangers bring him their wounded, because the Light comes when "
        "he asks."),
    look=("Greek man, 47, broad and solid, thick salt-and-pepper beard and hair, olive skin, dark eyes. White and gold "
          "plate with a sun on the chest, a round gold shield and a mace, a flat cap."),
),
"leif_primalist": dict(
    greeting="Watch where you stand. That old red one's got a dead limb up top that's been thinking about coming down "
             "all week.",
    backstory=(
        "Leif spent twenty-five years in the Oregon woods as a faller and a tree climber, and he loves trees more than "
        "anybody you'll meet. He came down out of a gold tree in Ashenvale three years ago, and the forest woke up in "
        "him the same week, which he thinks is either a joke or a sentence. When the Conclave sent word round "
        "Azshara for somebody who knew wood, he got on the boat. Now he brings in deadwood for Dawnrest, and only "
        "deadwood."),
    before=(
        "Coos Bay, where everybody's dad worked in timber, a daughter who fights wildfires, and a pickup that smelled "
        "of saw oil and coffee.\n\n"
        "His grandfather came over from Norway to work the mills. Leif went up the trees instead, and he never once "
        "fell."),
    adjustment=(
        "He spent two years with the druids in Ashenvale learning that the forest would rather he didn't. He hasn't "
        "started a saw since he came through.\n\n"
        "The elves wanted him to fell the old red trees for Dawnrest's beams. He took one look and showed them what "
        "was already lying on the ground."),
    forward=(
        "He wants to understand why the woods picked him, of all people.\n\n"
        "After that he'd like a morning in an old stand of trees with nothing to do but look at them, which he's never "
        "had in his life."),
    now=(
        "Duskfall Woods, in the Red Hollow, hauling deadwood out to the road for Dawnrest's roof.\n\n"
        "The bears in the hollow leave him alone, mostly. He looks up before he steps under anything, and he tells you "
        "to do the same."),
    look=("American man, 46, big and broad, a thick sandy-grey beard and long tied-back hair, weathered fair skin, "
          "blue eyes. Red and green plaid under worn leather and fur, a pair of axes, braces and heavy boots."),
),
}
