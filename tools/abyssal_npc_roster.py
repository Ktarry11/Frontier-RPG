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
        "Everything a camp needs and nothing a camp cannot carry on four carts.\n\nThat is the "
        "rule and I did not make it. Four carts is what we can strike and move in a day, and we "
        "have moved in a day twice, and both times I was glad about the rule and nobody else "
        "was."),
    "ab_cook": (
        "Cook Marda Pell", "goblin", "female", 23,
        ["bread_and_cheese", "roasted_meat", "meal_trailbread", "meal_spiced_haunch",
         "drink_barley_beer", "drink_waterskin", "healing_potion_superior"], False,
        "Bedrolls under the awning and the pot is on. Both of them come with the posting.\n\nI "
        "have fed this camp in four places and the food has got better every time, which is not a "
        "thing anybody expected including me. You learn a desert's pantry eventually. It is a "
        "short pantry and I know all of it now."),
    "ab_smith": (
        "Smith Gorra Blacktooth", "goblin", "female", 17,
        ["whetstone", "flux_strong", "coal", "glue", "thread_fine", "resin"], True,
        "Bring it before it goes, not after. There is no second forge between here and the "
        "port.\n\nI shoe nothing and I shod kodo for nine years, which tells you what this posting "
        "is. These days it is peg irons, chain, and whatever the crawlers have been at."),
    "ab_reagents": (
        "Brewer Sepp Narrow", "goblin", "male", 11,
        ["healing_potion_superior", "mana_potion_superior", "battle_elixir_superior",
         "guardian_elixir_superior", "elixir_of_greater_endurance", "vial_empty"], False,
        "Mixed thin, because everything out here has to survive a cart.\n\nI came out with the "
        "second camp on a three-month contract. That was two years and two camps ago and nobody "
        "has ever mentioned the contract again, including me."),
}

ABYSSAL_AMBIENT = {
    "ab_surveyor": (
        "Chief Surveyor Peska Vane", "goblin", "female", 20,
        "Fourth Peg. Seven months on this one, which is the longest any of them has stood.\n\nThe "
        "first went in with the ground under it. The second is sitting on the lip of the Wide Sink "
        "being perfectly accurate about a place that is no longer there. The third we moved "
        "ourselves because Hask did not like the hardpan, and four days later he was right, and I "
        "have still not got him to tell me how he knew in a way I can write down.\n\nI am not "
        "trying to build a road. I want that clear. I am trying to find out whether a road is "
        "POSSIBLE, and those are different jobs with different answers and only one of them has "
        "ever been funded."),
    "ab_rodman": (
        "Rodman Hask Quill", "goblin", "male", 14,
        "Somebody has to stand at the far end holding the staff, and out here the far end is "
        "usually somewhere nobody has walked.\n\nI like it. I know how that sounds.\n\nYou can "
        "read this ground if you are willing to go slowly. The hardpan rings different over a void "
        "- not much, but different, and it is louder in the morning when it is cold. Peska wants "
        "me to write that down as a method. I have tried. It comes out sounding like a man "
        "guessing."),
    "ab_teamster": (
        "Teamster Odd Varrow", "goblin", "male", 2,
        "Nineteen Mile. I was on the box and the lead pair were six lengths ahead of me when it "
        "went.\n\nI did not do anything clever. The cart went down and I came off the back of it "
        "and the ground I landed on held, and that is the entire story and I have told it four "
        "hundred times.\n\nThe part nobody asks about: the lead pair went in. I could hear them "
        "for about a day and a half. So when the camp talks about the ground like it is weather, "
        "I let them, and I go and stand somewhere else."),
    "ab_digger": (
        "Rope-Hand Vizzi Trask", "goblin", "female", 26,
        "Somebody has to go down them. Not far. Far enough to see whether there is a floor and "
        "whether the floor is going anywhere.\n\nNine of the eleven have floors. Two do not, and "
        "the two that do not are the two on the east side, and east is where the ground is worst "
        "and nobody has to tell me twice why.\n\nPeska logs it as 'no bottom observed'. I would "
        "log it differently. I would log it as 'do not'."),
}
