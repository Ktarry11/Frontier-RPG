"""
The people of Fourth Peg (44-47). The road survey camp on the Abyssal Sands.

Data only - tools/sync_abyssal_npcs.py writes these into data/npcs/*.json and takes every
coordinate from handbuilt_abyssal_sands.NPC_POSITIONS.

EIGHT PEOPLE WHOSE JOB KEEPS BEING UNDONE.

The zone was built with no town and no road, and that stays true: there WAS a road, it is in a
hole, and there is still no new one. What there is now is eight people trying to find where a new
one could go, and a camp named for the survey stake it is pitched around - the fourth stake,
because the first three are all in holes.

  FIRST PEG   went in with the ground under it, in the second season. Nobody was standing on it.
  SECOND PEG  lasted eleven months and is now on the lip of the Wide Sink, which is to say it is
              still there and the ground it was measuring from is not.
  THIRD PEG   they moved themselves, because Hask read the hardpan and did not like it, and four
              days later he was right. That is the only one they are proud of.
  FOURTH PEG  is where you are standing and it has held for seven months.

SO THE CAMP IS NOT DESPERATE, IT IS PATIENT, and that is the distinction that makes it worth
writing. These are not survivors. They are competent people doing a job that may be impossible,
who have decided that finding out whether it is impossible is itself worth doing. Nobody here is
going to be rescued and nobody here wants to be.

THE ARGUMENT IS NOT A FEUD. Unlike Lastwater, nobody here is deadlocked against anybody - the
tension is between the camp and the GROUND. What they disagree about is method: Peska wants more
pegs and longer waits, Rullo's money wants a line by autumn, and Hask thinks you can read the
hardpan and does not have a way to prove it that anybody else can repeat.

VOICE: working surveyors. Precise about numbers, dry, and completely unromantic about the desert.
They do not say "sinkhole", they say "a hole" or "it went", because four years in they have run
out of ways to make it sound like an event. Hask is the exception; he is the only one who finds
the ground interesting rather than hostile.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

ABYSSAL_VENDORS = {
    "ab_quartermaster": (
        "Quartermaster Tobbit Lund", "goblin", "male", 5,
        ["healing_potion_superior", "mana_potion_superior", "meal_trailbread", "drink_waterskin",
         "whetstone", "flux_strong", "component_string", "parchment", "glue", "coal"], True,
        "I stock what a camp needs, as long as it fits on four carts.\n\nFour carts is what we can pack and move in a day. We've had to do that twice. I was glad of the rule both times, and I was the only one."),
    "ab_cook": (
        "Cook Marda Pell", "goblin", "female", 23,
        ["bread_and_cheese", "roasted_meat", "meal_trailbread", "meal_spiced_haunch",
         "drink_barley_beer", "drink_waterskin", "healing_potion_superior"], False,
        "There are bedrolls under the awning and the pot's on. You get both with the posting.\n\nI've fed this camp in four places and the food's got better each time. It took me a while to learn what a desert has to eat. There isn't much, but I know all of it now."),
    "ab_smith": (
        "Smith Gorra Blacktooth", "goblin", "female", 17,
        ["whetstone", "flux_strong", "coal", "glue", "thread_fine", "resin"], True,
        "Bring me your gear before it breaks. There's no other forge between here and the port.\n\nI shod kodo for nine years and there's nothing to shoe out here. These days I make peg irons and chain, and I mend whatever the crawlers have chewed."),
    "ab_reagents": (
        "Brewer Sepp Narrow", "goblin", "male", 11,
        ["healing_potion_superior", "mana_potion_superior", "battle_elixir_superior",
         "guardian_elixir_superior", "elixir_of_greater_endurance", "vial_empty"], False,
        "I mix everything thin, so the bottles survive the cart.\n\nI came out with the second camp on a three-month contract. That was two years and two camps ago. Nobody's mentioned the contract since, and I haven't either."),
}

ABYSSAL_AMBIENT = {
    "ab_surveyor": (
        "Chief Surveyor Peska Vane", "goblin", "female", 20,
        "This is Fourth Peg. The peg's stood seven months, which is longer than the other three did.\n\nThe first fell in with the ground under it. The second's on the lip of the Wide Sink, marking ground that's gone. We moved the third because Hask didn't like the hardpan, and that spot fell in four days later.\n\nThe port at Steamwheedle pays me to find out if a road can be built across the Abyssal Sands. I don't know yet."),
    "ab_rodman": (
        "Rodman Hask Quill", "goblin", "male", 14,
        "I'm the one who stands at the far end holding the staff. Out here the far end's usually somewhere nobody's walked before.\n\nI like the work. I know that sounds odd.\n\nYou can read this ground if you go slowly. The hardpan sounds different over a hollow, and it's louder on a cold morning. Peska wants that written up as a method. Every time I try, it reads like guessing."),
    "ab_teamster": (
        "Teamster Odd Varrow", "goblin", "male", 2,
        "I was driving the second cart at Nineteen Mile when the road went. The lead pair were six lengths ahead of me.\n\nThe cart went down and I fell off the back, and the ground I landed on held. I didn't do anything clever. I've told that story four hundred times.\n\nI could hear the lead pair down there for a day and a half. So when the camp talks about the ground like it's weather, I go and stand somewhere else."),
    "ab_digger": (
        "Rope-Hand Vizzi Trask", "goblin", "female", 12,
        "Somebody has to go down the pits on a rope and see if there's a floor. That's me.\n\nNine of the eleven have floors. The Throats in the southwest and Underlight in the southeast don't, as far as my line reaches.\n\nPeska writes those up as 'no bottom observed'. I'd write 'don't go down'."),
}
