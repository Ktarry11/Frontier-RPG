"""Batch: Marcus, Mariana, Marisol, Marta, Mateo, Matias.

Marisol's brother is one of the calls still waiting on Kyle, so her tabs keep only what was already written about him.
"""

VOICE = {
    "marcus_stormbringer": {
        "greeting":
            "The pressure's dropping, listen. That isn't thunder yet, that's the front arriving, and we've got about "
            "four minutes before it gets loud and I get useful.",
        "before":
            "Marcus was a meteorologist in Toronto. As a student he chased storms, badly and happily, in a battered "
            "Corolla. Then he spent fifteen years watching them on screens from somewhere warm, writing warnings and "
            "briefing people whose job was deciding the warning was inconvenient. He spent a whole career being "
            "right early and watching it change nothing. His mother in Lagos thought the job was a waste of a good "
            "degree, and said so every Christmas until the last one.",
        "adjustment":
            "He treated the whole thing as fieldwork, and it carried him through almost intact, which is better than "
            "most people managed. What wrecked him privately for a year was that at home a storm was something he "
            "could predict but never touch. Here the storm answers him. He's told everyone he's fine about that since "
            "the day it started, and they believe him, because he really is fine. He's also not, and he's given up "
            "trying to make those two things agree.",
        "now":
            "He lives in Durotar, where dry storms roll in off the sea with no rain in them and the thunder arrives "
            "without warning. His notes on where the lightning strikes have already told him something about this "
            "coast that the orcs didn't know. He can't work out how to tell them without sounding like every other "
            "outsider who turned up with a clipboard. So far he's kept it in his notebook.",
        "forward":
            "Marcus wants a full season's data written up properly, and one person on this world who cares what's "
            "in it. He's realistic about the odds, and he keeps the records anyway. What he won't say out loud is "
            "that he'd like to stand in the middle of the biggest storm there is. He's a meteorologist, and he knows "
            "how that ends.",
    },
    "mariana_priest": {
        "before":
            "Mariana was a radiation therapist at a cancer centre in Monterrey for ten years. She spent her days "
            "lining up beams to the millimetre, so the radiation hit the tumour and nothing else. She remembered every "
            "patient's birthday, and she rang a little bell for each of them on their last day of treatment. She ran "
            "with a club that met at five every morning, and her brother ran a taco stand by the stadium.",
        "adjustment":
            "She found the Light the same way she'd always found the right dose, carefully and with a lot of notes. "
            "The priests in Orgrimmar told her she prayed like an accountant, and she took it as a compliment. She "
            "heals with the Light now, and she aims it exactly the way she aimed the beams. When the liquidators "
            "asked for someone who wasn't afraid of the word radiation, she packed that same night.",
        "now":
            "She runs the infirmary at the liquidators' camp, Ariden's Watch, in Deadwind Pass, working by lamplight "
            "with a stack of notebooks. The Forsaken apothecaries bring her their worst cases, and they've stopped "
            "arguing with her charts. She's calm, precise and kind. She has a gallows humour she only lets other "
            "medics see.",
        "forward":
            "Mariana is keeping a record of everything the fallout does to a body, so whoever comes after her has "
            "something to work from. It's the only record of its kind. One day she'd like to run again, somewhere "
            "that doesn't glow. She still has the little bell, and she rings it when someone walks out of her "
            "infirmary cured.",
    },
    "marisol_priest": {
        "before":
            "Marisol spent nine years working in an emergency department in Bogota, three of them on nights and all "
            "of them short-staffed. She learned to keep a frightened person talking while her hands did something "
            "they'd rather not watch. Her brother Andres was a motorcycle courier in the same city, and she patched "
            "him up twice. The second time she shouted at him in the corridor for ten minutes, and she'd give "
            "anything to have that back.",
        "adjustment":
            "She worked flat out for eighteen months, and she'll tell you honestly that she did it to stay out of "
            "her own head. It worked, and she'd do it again, and she knows exactly what it was. Both the Light and "
            "the shadow move through her easily, and she treats them like instruments laid out on a tray. She still "
            "talks people through what she's doing, the way she always did, and half the party finds it steadying "
            "and the other half find it maddening.",
        "now":
            "She works out of the Sepulcher in Silverpine North, along the forest road where wolves and worse attack "
            "travellers, and the Forsaken garrison takes its time getting to them. Marisol gets to them faster. The "
            "garrison has noticed. The quartermaster, apparently, hasn't.",
        "forward":
            "Marisol wants a proper ward, with four beds and a roof, where an injured person can lie down for a week "
            "instead of being patched up in a field. There's an empty building at the Sepulcher that would do. She's "
            "been negotiating for it for eleven months with a Forsaken quartermaster who keeps asking whose authority "
            "she's under. She's started to enjoy the arguments.",
    },
    "marta_tinker": {
        "greeting":
            "Give it here, please, no, give it here. You've been hitting it, haven't you? People always hit it.",
        "before":
            "Marta spent nineteen years looking after the industrial sewing machines at a factory in Lodz, in "
            "Poland. She was the only person in the building who could tell what was wrong with a machine from the "
            "sound it made, and she could diagnose the whole floor from the doorway. Management called her whenever "
            "a line stopped, and only ever by her first name. Her husband Tomasz worked the other shift for fifteen "
            "years so that one of them was always home with their boys. They kissed in the doorway twice a day.",
        "adjustment":
            "It took her three weeks to settle, and she'll argue that most of that was the language. A machine is a "
            "machine, wherever you are. She was repairing goblin gear for money before she could ask where the "
            "toilet was. Goblin engineering turned out to be the same noise with more smoke, and she loves it in a "
            "way she'd be embarrassed to see written down.",
        "now":
            "She works at the Boulder Lode Mine in the Northern Barrens, where everything is broken and the goblins "
            "charge a fortune to fix it. She undercuts them by a third and fixes it properly. The goblin foreman has "
            "threatened her twice and sent her work three times. Her boys are grown, and Tomasz was on his way to "
            "work when it happened.",
        "forward":
            "Marta wants her own bench and her own sign, with nobody above her on a floor plan. She's been quoted a "
            "price for a corner of the workshop by the pumps, and she can afford it. She's found four reasons to "
            "wait. She knows all four are really the same reason.",
    },
    "mateo_starcaller": {
        "greeting":
            "Look up at it, go on, look up. Three years here and I still have to make people look up.",
        "before":
            "Mateo spent seventeen years keeping the lights on at a mountaintop observatory above the Elqui valley "
            "in Chile. He was a technician, not an astronomer, and he'll correct you on that immediately and then "
            "talk about the stars for an hour anyway. He loved the four hours before dawn, when the astronomers slept "
            "and the mountain belonged to him. His wife Paula and their two girls lived in La Serena, and the girls "
            "thought the mountain was boring. He agreed with them and went anyway, every month, for seventeen years.",
        "adjustment":
            "He arrived on a world with the wrong stars in it and spent his first winter learning them from scratch, "
            "alone, lying on his back in the grass. He was happier than he'd been in a decade. The trouble came in "
            "his second winter, when he'd finished naming the constellations and had to come back down and be a "
            "person again. That took a good deal longer than the stars.",
        "now":
            "He lives on top of a mesa in Southern Thousand Needles, where the air is dry and the nights go on "
            "forever. The goblins of the Flats think he's harmless and let him climb their towers. From the top of "
            "one he can see most of the sky at once. He's started to suspect it's the finest place to watch the stars "
            "on this whole world.",
        "forward":
            "Mateo is drawing a proper map of this sky, because he understands that a sky is also a calendar, a "
            "clock and a promise. He's eleven months into it. Twice a year he walks to Freewind Post with two names "
            "folded in his pocket and reads the whole list of the missing. He talks about the stars on the way there "
            "and says very little on the way home.",
    },
    "matias_reaper": {
        "greeting":
            "I go in front, because it's better that way. You can talk to me afterwards if you want to, but now "
            "isn't the time for talking.",
        "before":
            "Matias worked the buses in Santiago from the age of nineteen, punching tickets on a route he could have "
            "driven blindfolded. His father had the same job before him and thought it was beneath his sons. What "
            "Matias was good at was standing still in a crowd of strangers for nine hours and watching all of them "
            "at once. His father died in 2019, and they hadn't spoken for two years. His mother and his little "
            "brother were at home when everything changed.",
        "adjustment":
            "He'll tell you plainly that it went badly, if you ask him directly, and almost nobody does. He stopped "
            "speaking for most of his first year without meaning to. He ran out of things worth the effort of "
            "translating, and the quiet got comfortable, and then it got hard to leave. He's built his English from "
            "nothing in three years. People mistake his care with words for slowness about twice, and then they "
            "stop.",
        "now":
            "He fights at the front, in the Sunken Grotto of the Deep or anywhere else that's dark, because from "
            "there he can see everyone. He clicks his old ticket punch twice before every fight. Somebody once asked "
            "him if it was for luck, and he said no and didn't explain. He's only ever told one person about his "
            "family, at night, on watch.",
        "forward":
            "Matias is learning to read this world's script, slowly, from a woman at a trading post in Durotar who "
            "charges him nothing and corrects him constantly. He hasn't told anybody why. He wants to write a letter "
            "to his mother. He knows there's nowhere to send it, and he wants to write it anyway.",
    },
}
