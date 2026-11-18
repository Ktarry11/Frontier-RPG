"""
Harvest finds: the strange things you turn up while mining, picking herbs, skinning and fishing, and the fishing
extras. Content only; tools/build_harvest_finds.py builds the game's data from it and holds it to every rule. The
design is docs/harvest_finds_design.md.

Kyle, 18 Nov 2026: "Junk and salvage from fishing, yes. Lets have it as the occasional green item and maybe something
unique to fishing! Something fun. Also maybe some quest starts! OOOOOOOOH Why don't we have some quests starting FROM
harvesting. Like 'Odd living copper chunk - starts quest' or 'Mutated silverleaf' --- that'd be cool!" His picks: about
16 starters, four a trade; turn-ins mixed (trainers, transplants, druids, places); for fishing, Collection mounts, Earth
junk, fishing-only gear and titles; an art sheet with stand-ins until it lands.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first. The first quest of each chain is started by the item, so its accept text is the find speaking
for itself: what it is and who'd know.
"""

# ---- who the chains go to (all existing; at most one new quest given by any of them)
PRIZZLE, AHNMAR = "razorhill_goblin_engineer", "cb_shrine_keeper"
BAINE, RURK = "pt_taurajo_forge", "sb_bonehunter"
INNIK = "arathi_ring_scholar"
NOOR, KENJI = "bs_geologist", "dw_kenji"
SHAZRA, ZURM = "pt_org_herbs", "orgrimmar_alchemist"
NAWA = "pt_sun_rock_herbs"
VASHKA, DELLWYN = "pt_hammerfall_herbs", "hammerfall_apothecary"
MYLLA, SANDVIK = "pt_mg_herbs", "mg_sandvik"
URZUL = "pt_razorhill_hide"
DELL = "hbe_mill_hunter"
DORGUN = "gromgol_smith"
ANDERS, DORIAN = "wpl_pf_bat_keeper", "wpl_bulwark_apothecary"
GRIBBLE = "ratchet_fishmonger"
SPROCKET, LINDQVIST = "pt_ratchet_essence", "sr_transplant_geologist"
ULUA = "stvc_marsh_fisher"
ILYSSA, DANNY = "pt_mg_fish", "mg_dreamer"

#: The sixteen starters. trade, where it turns up (materials for the node trades, beast levels for skinning), the
#: level band a character finds it in, and its two quests. ("deliver", npc) hands the item over; ("explore", map,
#: subzone) sends you to a named place on a map and back to the giver.
STARTERS = [
    # ------------------------------------------------------------------------------------------------ mining
    dict(id="hf_ticking_copper", name="Ticking Copper Nugget", trade="mining", mats=["ore_copper"], band=(6, 18),
         desc="A nugget of copper that's warm in your hand. Hold it still and you can feel it tick, slow and even, "
              "like something asleep.",
         q1=dict(title="Something in the Copper", to=PRIZZLE, lvl=(8, 14),
                 desc="A nugget of copper ore ticks like a heartbeat. Prizzle Boltwrench in Razor Hill takes apart "
                      "anything that ticks.",
                 accept="It's ticking in your hand. Not like a clock, which is what you'd expect, but slower, and it skips now and "
                        "then the way a sleeper's breath does. The goblin in Razor Hill builds things that tick, and "
                        "if anyone can say what's inside a nugget of copper, it's her.",
                 done="Give it here, and let me listen. I've had seven inventions explode on me this year, and none of them felt "
                      "like this. There's nothing in there to wind. It's alive, or it's dreaming about being alive."),
         q2=dict(title="The Stone Is Listening", obj=("deliver", AHNMAR), lvl=(12, 16),
                 desc="Prizzle won't take apart a living thing. She wants Keeper Ahnmar Stonetotem at the shrine in "
                      "the Central Barrens to see the nugget.",
                 accept="I'm an engineer, and I don't open up things that tick on their own. There's a tauren at the "
                        "shrine in the Central Barrens, Keeper Ahnmar, who says the stone talks to him. I always "
                        "laughed at that, and I'm not laughing now. Take it to him, and tell him I didn't drop it.",
                 done="Put it on the stone, gently, and listen. Do you hear how it slows? It's a seed of the earth, a "
                      "little spirit that hadn't woken yet, and your pick found it early. It'll sleep here with the "
                      "others now, and it'll remember you kindly.")),
    dict(id="hf_tin_fossil_tooth", name="Tin Ore With a Fossil Tooth", trade="mining", mats=["ore_tin"], band=(18, 28),
         desc="A lump of tin ore with a tooth sunk in it, long and serrated and longer than your hand. Whatever it "
              "came out of was big, and it was hungry a very long time ago.",
         q1=dict(title="A Tooth in the Tin", to=BAINE, lvl=(18, 22),
                 desc="A fossil tooth is sunk in a lump of tin ore. Forge Baine at Camp Taurajo has the steady hands "
                      "to free it.",
                 accept="The tooth's longer than your hand, and it's sunk in the tin like something bit the rock. A "
                        "smith would know how to get it out without cracking it. There's a forge at Camp Taurajo, "
                        "and Forge Baine has steady hands.",
                 done="That's no kodo's tooth. I've split a lot of ore and found shells in it, and once a fern "
                      "pressed flat, but I've never found a tooth. I'll free it for you. Hold still while I tap."),
         q2=dict(title="Bones Under the Plain", obj=("deliver", RURK), lvl=(20, 24),
                 desc="Forge Baine wants Bonehunter Rurk Gravetusk in the Southern Barrens to see the tooth.",
                 accept="There's a bonehunter out on the plain, Rurk Gravetusk, who says giants walked the Barrens "
                        "once. I've always said he spends too long in the sun. Take him the tooth and let him tell "
                        "you which of us is right.",
                 done="Give it here. Oh, look at that. The giants I dig are thunder lizards, the old kind, but this "
                      "is a hunter's tooth, and it's from something bigger than any of them. You found it in tin from "
                      "the hills? Then the hills are older than I thought, and I've got a lot more digging to do.")),
    dict(id="hf_singing_mithril", name="Singing Mithril Shard", trade="mining", mats=["ore_mithril"], band=(36, 46),
         desc="A shard of mithril ore that hums one clear note when you hold it, and a lower one answers when you "
              "hold it near another stone.",
         q1=dict(title="The Ore That Sings", to=INNIK, lvl=(36, 40),
                 desc="A shard of mithril ore hums, and stones answer it. Scholar Innik Barrowmouth has spent years "
                      "on the old stones of Arathi.",
                 accept="It's humming, one clear note you feel in your teeth more than you hear, and a lower note "
                        "answers when you hold it near a stone. The scholar at the Ring in Arathi has spent years on "
                        "why the old stones stand where they do. He'll want to hear this.",
                 done="Hold it up, higher than that. Do you hear that? The circle's answering it. I've measured these "
                      "stones for nine years and I've never once heard them make a sound. This shard was cut from "
                      "the vein the builders used, I'd bet my notes on it."),
         q2=dict(title="Ring the Circle", obj=("explore", "Arathi Central", "The Ring Road"), lvl=(37, 41),
                 desc="Scholar Innik wants the shard carried round the circle on the Ring Road while you listen for "
                      "where its note changes.",
                 accept="I need you to carry it round the circle on the Ring Road, slowly, and listen for where the "
                        "note changes. Don't hurry it. I'll write down whatever you tell me, and if it means what I "
                        "think it means, the stones were never a calendar at all.",
                 done="Three places where it rose and one where it went quiet? Then they're not markers, they're a "
                      "chord. The builders tuned a valley. I'm going to need a great deal more paper, and probably "
                      "a drink.")),
    dict(id="hf_thorium_fingerprint", name="Thorium With a Fingerprint", trade="mining", mats=["ore_thorium"],
         band=(50, 60),
         desc="A chunk of thorium ore with one glassy face, and pressed into the glass, a fingerprint. A human one, "
              "small and clear, as if someone touched the ore while it was still molten.",
         q1=dict(title="A Fingerprint in the Glass", to=NOOR, lvl=(50, 54),
                 desc="Somebody's fingerprint is pressed into a glassy face of thorium ore. Noor Haddad, a geologist "
                      "from Earth, works out on the Black Strand.",
                 accept="Somebody touched this while it was molten, and the glass kept their fingerprint. That isn't "
                        "possible, and it's sitting in your hand anyway. There's a geologist out on the Black Strand, "
                        "Noor Haddad, who came through from Earth. She'll know how hot rock has to be to take a "
                        "print.",
                 done="Oh, that's a real print. Rock doesn't do this. Glass this clean only forms in a flash, a "
                      "second of heat and then cold, and somebody's hand was on it in that second. I think I know "
                      "which second. I think it's the one that brought us here."),
         q2=dict(title="Whose Hand", obj=("deliver", KENJI), lvl=(54, 58),
                 desc="Noor Haddad wants the print taken to Kenji Watanabe at Ariden's Watch, who keeps the "
                      "Liquidators' board of names.",
                 accept="The Liquidators at Ariden's Watch keep a board with the names of everyone who came through "
                        "near the wound in Deadwind, and their surveyor, Kenji Watanabe, took prints when people would "
                        "let him. Take the stone to him. If the print's on his board, somebody's family deserves to "
                        "know where it ended up.",
                 done="Let me see, and give me a minute with the cards. Here it is. It matches a volunteer called Ilse Brandt, "
                      "from the first week. She went into the Stopped Places and didn't come out. She'd have liked "
                      "knowing a piece of her ended up somewhere solid. I'll put the stone on the board beside her "
                      "name.")),
    # ------------------------------------------------------------------------------------------------ herbalism
    dict(id="hf_mutated_silverleaf", name="Mutated Silverleaf", trade="herbalism",
         mats=["herb_silverleaf", "herb_peacebloom"], band=(5, 14),
         desc="A sprig of silverleaf with one leaf too many, growing out of the stem where no leaf should be. The "
              "veins in it are purple.",
         q1=dict(title="One Leaf Too Many", to=SHAZRA, lvl=(6, 10),
                 desc="A sprig of silverleaf has grown a leaf it shouldn't have, veined in purple. Apothecary Shazra "
                      "teaches herb lore in Orgrimmar.",
                 accept="One of the leaves on this sprig shouldn't be there, and its veins have gone purple. "
                        "Herbalists will tell you silverleaf never sports. Shazra teaches herb lore in Orgrimmar, and "
                        "he'll want to see a silverleaf that broke the rule.",
                 done="Let me look. That's not a sport, that's something in the ground. Purple runs in a plant when "
                      "it's drinking what it shouldn't. I've seen it once before, in a crate of herbs off a Forsaken "
                      "ship."),
         q2=dict(title="What the Roots Drink", obj=("deliver", ZURM), lvl=(8, 12),
                 desc="Shazra wants Apothecary Zurm in Orgrimmar to taste the sprig and say what it's been drinking.",
                 accept="Zurm brews in the Drag, and he's tasted more bad water than anyone in this city. Take him the "
                        "sprig and ask him what it's been drinking. Don't let him eat it, because he'll try.",
                 done="Ha, don't worry, I only lick it. Bitter, then sweet, then numb. That's plague water, a little "
                      "of it, carried a long way through the ground from wherever it was spilled. Somebody's been "
                      "washing their cauldrons in a river, and rivers go everywhere. I'll write to the Warchief's "
                      "people. You keep picking, and bring me the next odd one.")),
    dict(id="hf_bleeding_kingsblood", name="Kingsblood That Bleeds", trade="herbalism", mats=["herb_kingsblood"],
         band=(24, 34),
         desc="A kingsblood flower cut at the stem. The stem bleeds slow red drops that don't dry, and it's warm the "
              "way a hand is warm.",
         q1=dict(title="The Herb That Bleeds", to=NAWA, lvl=(26, 30),
                 desc="A cut kingsblood won't stop bleeding. Herbalist Nawa Greenmane at Sun Rock Retreat knows every "
                      "plant that came back after the fires.",
                 accept="Kingsblood's named for its colour, and it isn't supposed to bleed when you cut it. This one "
                        "hasn't stopped. Sun Rock's herbalist, Nawa Greenmane, knows every plant that came back after "
                        "the fires, and she'll know if this is one of them.",
                 done="It's still bleeding? Let me hold it. It's warm, like a hand. This didn't come back after the fires. "
                      "Something's feeding it, and plants only bleed like this when the ground under them is hurt."),
         q2=dict(title="Hurt Ground", obj=("explore", "Stonetalon West", "The Venture Cutline"), lvl=(28, 32),
                 desc="Nawa wants you to walk the Venture Cutline and see whether anything else on it bleeds.",
                 accept="The goblins have been cutting the old trees on the Venture Cutline, roots and all. Walk the "
                        "cutline for me and see whether anything else on it bleeds. Don't touch it if it is. "
                        "Come back and tell me what you saw.",
                 done="The stumps are weeping too? Then it's the roots. The great trees held that ground together "
                      "for a thousand years, and now nothing does. I'll take this to the elders. Thank you for "
                      "looking, when most people would've just sold the flower.")),
    dict(id="hf_unfading_fadeleaf", name="Fadeleaf That Won't Fade", trade="herbalism", mats=["herb_fadeleaf"],
         band=(34, 44),
         desc="Fadeleaf turns see-through within an hour of picking. This one went half clear and then stopped, as "
              "if it got stuck partway.",
         q1=dict(title="Stuck Halfway", to=VASHKA, lvl=(35, 39),
                 desc="A fadeleaf has stopped fading halfway. Apothecary Vashka at Hammerfall works fadeleaf into "
                      "her scouts' potions.",
                 accept="Fadeleaf goes clear as glass within an hour of picking, and this one's been half clear since "
                        "you pulled it. It's stuck partway. Vashka at Hammerfall works fadeleaf into the potions that make a "
                        "scout hard to see, so she'll know what it's meant to do.",
                 done="It's stuck halfway, and I've never seen that. A fadeleaf that won't finish fading would make a potion "
                      "that hides half of you, which is worse than useless. Dellwyn's been writing about something "
                      "like this for months."),
         q2=dict(title="Halfway Down the Jar", obj=("deliver", DELLWYN), lvl=(37, 41),
                 desc="Vashka wants Apothecary Dellwyn Voss to set the leaf beside his jars of water from the Sunken "
                      "Mere.",
                 accept="Dellwyn Voss, our apothecary, has been writing about the Sunken Mere for months, because his "
                        "water samples from it stopped settling halfway down the jar. He'll want this leaf beside "
                        "them. He's just across the yard.",
                 done="Put it here, beside the jars. Look, the silt in every one of them stopped at the same height "
                      "your leaf stopped fading. Something's catching things halfway, and it isn't only in the mere. "
                      "I'll be writing all night.")),
    dict(id="hf_dreaming_dreamfoil", name="Dreamfoil That Dreams", trade="herbalism", mats=["herb_dreamfoil"],
         band=(50, 60),
         desc="A sprig of dreamfoil whose leaves curl closed like eyelids. Hold it close and you'd swear it's "
              "breathing slowly, the way a sleeper does.",
         q1=dict(title="Dreamfoil That Dreams", to=MYLLA, lvl=(54, 58),
                 desc="A sprig of dreamfoil has curled its leaves shut and is breathing. Herbwarden Mylla Starbloom "
                      "in Nighthaven knows the plants that sleep.",
                 accept="Its leaves curled shut the moment you picked it, like eyes closing, and it's breathing. "
                        "Slowly, the way a sleeper breathes. If anyone knows a plant that sleeps, it's the herbwarden "
                        "in Nighthaven, Mylla Starbloom.",
                 done="It's dreaming, that's what this is. I've grown dreamfoil all my life, and it was always named for what it does to "
                      "you, never for what it does itself. Since the Integration, half the beds in my garden curl "
                      "shut at night. I didn't want it to be true until somebody else brought me one."),
         q2=dict(title="Eight Breaths a Minute", obj=("deliver", SANDVIK), lvl=(55, 59),
                 desc="Mylla wants Dr. Ingrid Sandvik of the Wakened to measure the sleeping dreamfoil.",
                 accept="Take it to Dr. Sandvik on the west shore. She studies sleepers, and she's the only one in "
                        "the glade who'll measure it rather than pray over it. I'd rather know than wonder, and so "
                        "would she.",
                 done="Hold it still. It's breathing eight times a minute, the same as the sleepers in the Barrow "
                      "Dens. That can't be chance. Whatever's dreaming in the Dens is dreaming through the plants "
                      "too, or the plants are dreaming with it. I'll keep it by the cots and see if it wakes when "
                      "they do.")),
    # ------------------------------------------------------------------------------------------------ skinning
    dict(id="hf_scratched_hide_map", name="Hide With a Map Scratched In", trade="skinning", band=(6, 16),
         desc="A scrap of hide with a map scratched into the underside: a crooked path, a rock shaped like a tusk, "
              "and an X.",
         q1=dict(title="X Marks a Hide", to=URZUL, lvl=(7, 11),
                 desc="Somebody scratched a map into a beast's hide. Tanner Urzul in Razor Hill has handled every "
                      "hide in Durotar.",
                 accept="Somebody scratched a map into this hide while it was still on the beast, and the beast "
                        "healed round it. There's a path, a rock like a tusk, and an X. The tanner in Razor Hill, "
                        "Urzul, has handled every hide in Durotar, and he might know the rock.",
                 done="That's a smuggler's mark, and an old one. They'd scratch a map into a young boar so it "
                      "carried the way for them, and nobody looks twice at a boar. The tusk rock's out on Kolkar "
                      "Crag."),
         q2=dict(title="Where the Boar Went", obj=("explore", "Durotar", "Kolkar Crag"), lvl=(9, 12),
                 desc="Urzul wants you to find the tusk rock on Kolkar Crag and see what the smugglers left.",
                 accept="Go out to Kolkar Crag and find the rock shaped like a tusk. Whatever was buried there's "
                        "probably long gone, but smugglers always left something for the next crew. Come back and "
                        "tell me what you find, and we'll split it.",
                 done="A rusted strongbox with three copper coins in it? Smugglers were always poor. Keep the coins, "
                      "and keep the hide too. It's a better story than the treasure ever was.")),
    dict(id="hf_tagged_ear", name="Tagged Ear", trade="skinning", band=(20, 30),
         desc="A beast's ear with a bright yellow tag clipped through it, smooth and hard and printed with numbers. "
              "It's the kind of tag they put on animals on Earth to follow where they go.",
         q1=dict(title="Tag 0417", to=DELL, lvl=(22, 26),
                 desc="A beast you skinned wore an Earth wildlife tag. Huntsman Dell Varrow at Tarren Mill was a "
                      "gamekeeper before the Integration.",
                 accept="That's a wildlife tag, plastic and printed with a number, the sort a ranger clips on a deer "
                        "back on Earth. This beast came through with the rest of us. The huntsman at Tarren Mill was "
                        "a gamekeeper before the Integration, and he'll know what to make of it.",
                 done="Well, I'll be. That's a deer tag from the Peak District, and I clipped hundreds like it. "
                      "It's number 0417. I don't remember that one, but I know the series. So the animals came through "
                      "too, not just us. Some of them, anyway."),
         q2=dict(title="The Rest of the Herd", obj=("explore", "Western Hillsbrad", "The Foothill Pastures"),
                 lvl=(23, 27),
                 desc="Dell Varrow wants you to look over the Foothill Pastures for more tagged beasts.",
                 accept="If one tagged beast came through, there'll be more of the herd near where it landed. The "
                        "Foothill Pastures look the most like home, and that's where I'd go if I were a confused "
                        "deer. Have a look round, and count any ear with a tag in it.",
                 done="Four of them, grazing like nothing happened? That's the best news I've had since I got here. "
                      "I'll go and see them tomorrow. I'm not going to clip anything, I just want to say hello.")),
    dict(id="hf_great_scale", name="Scale From Something Bigger", trade="skinning", band=(34, 44),
         desc="One scale, dark green with a bronze edge, as big as a shield and heavier than it looks. It came off a "
              "beast that was carrying it the way you'd carry a borrowed coat.",
         q1=dict(title="Too Big for the Beast", to=DORGUN, lvl=(35, 39),
                 desc="A scale as big as a shield was stuck in a beast's hide. Smith Dorgun at Grom'gol knows armour.",
                 accept="The beast you skinned had this one scale stuck in its hide, and it's as big as a shield. "
                        "Nothing that size lives in Stranglethorn, or nothing anyone talks about. The smith at "
                        "Grom'gol, Dorgun, knows armour, and he'll know if it's anything he can use.",
                 done="Big as a shield and harder than one. Damp doesn't touch it either, and damp touches everything "
                      "here. That's a crocolisk scale, but the croc that grew it would be the size of a boat. The "
                      "fishers say they've seen something like that in the Snapjaw Marsh."),
         q2=dict(title="Something in the Snapjaw", obj=("explore", "Central Stranglethorn", "The Snapjaw Marsh"),
                 lvl=(36, 40),
                 desc="Smith Dorgun wants you to look for the giant crocolisk in the Snapjaw Marsh, and not fight it.",
                 accept="Go and look in the Snapjaw Marsh. Don't fight it if it's there, just look, and tell me how "
                        "big it is. If it's shedding scales like this, I want to be the smith who makes a shield out "
                        "of the next one.",
                 done="You saw the wake and nothing else? That's plenty to go on. A wake that wide means it's still growing. "
                      "I'll make you something out of this one, and I'll pay the fishers for any more they find.")),
    dict(id="hf_stitched_hide", name="Stitched Hide", trade="skinning", band=(50, 60),
         desc="A patch of hide made of two animals' skins, stitched together with black thread while both were still "
              "alive. The stitches are neat. Somebody took care.",
         q1=dict(title="Stitched While Living", to=ANDERS, lvl=(51, 55),
                 desc="Two beasts' hides were stitched together while they lived. Anders Holm keeps the hawks at the "
                      "Bulwark and knows every beast in the fields.",
                 accept="This is two hides stitched into one, and they were stitched while the animals were alive, "
                        "because the edges healed together. The stitching's neat and careful. Anders Holm keeps the "
                        "hawks at the Bulwark and knows every beast in these fields. He'll want to know what's out "
                        "there.",
                 done="My hawks won't go near it. Look at them. That's the Cult's needlework. They've started "
                      "stitching living beasts together to make something stronger than either, a wolf and a bear "
                      "from the fur. Somebody out there's building an army that breathes."),
         q2=dict(title="The Needlework", obj=("deliver", DORIAN), lvl=(52, 56),
                 desc="Anders Holm wants Apothecary Dorian Vesk to learn what keeps the stitched beasts alive.",
                 accept="Take the hide to Dorian Vesk, our apothecary. He's been studying what the Scourge brew in "
                        "the fields, and if they're stitching living things now, he'll want to know what they use to "
                        "keep them alive while they do it.",
                 done="Black thread soaked in plague water. That's what keeps the halves from rejecting each other. "
                      "It's clever, and I hate that it's clever. Thank you. I'll have something to fight it by the "
                      "end of the week, if I don't sleep.")),
    # ------------------------------------------------------------------------------------------------ fishing
    dict(id="hf_message_bottle", name="Message in a Bottle", trade="fishing", band=(6, 18),
         desc="A green glass bottle crusted with barnacles. There's a rolled note inside, and the cork's sealed with "
              "candle wax by somebody who meant it to last.",
         q1=dict(title="Message in a Bottle", to=GRIBBLE, lvl=(10, 14),
                 desc="A bottle with a goblin's note in it names Ratchet. Fishmonger Gribble knows every crew that "
                      "ever sailed from there.",
                 accept="You'd have to break the bottle to read the note properly, but you can make out a goblin's "
                        "hand and the word Ratchet through the glass. The fishmonger there, Gribble, knows every crew "
                        "that ever sailed out of that harbour, and he'll know who wrote it.",
                 done="That's my cousin Snazz's writing. He went down with the Silver Sprocket off the Merchant Coast "
                      "three years ago. Says here he buried the crew's pay before she sank, under a rock with a "
                      "gull's nest on it. Snazz never told the truth in his life, but he never lied about money."),
         q2=dict(title="Snazz's Last Joke", obj=("explore", "Northern Barrens", "Merchant Coast"), lvl=(12, 15),
                 desc="Gribble wants you to find the rock with the gull's nest on the Merchant Coast and dig under it.",
                 accept="Go to the Merchant Coast and find a rock with a gull's nest on it, then dig under it. If "
                        "there's a box, half's yours. If there's nothing, then Snazz finally told a lie I'll laugh "
                        "at, and that's worth something too.",
                 done="A box with a rusty lock and a note in it saying Gotcha, Gribble? That's Snazz all over. I "
                      "haven't laughed like that in three years. Here, take this. It's more than his box ever had in "
                      "it.")),
    dict(id="hf_waterlogged_phone", name="Waterlogged Phone", trade="fishing", band=(20, 32),
         desc="A phone from Earth, its screen cracked across and full of water, with a strand of seaweed caught in "
              "the case. It hasn't had a signal in three years and it never will.",
         q1=dict(title="No Signal", to=SPROCKET, lvl=(22, 26),
                 desc="You fished up a phone from Earth. Tinker Sprocket in Ratchet opens anything with a seam in it.",
                 accept="It's a phone, from home. The glass is cracked and there's water behind it, but it isn't "
                        "crushed. The tinker in Ratchet, Sprocket, opens anything with a seam in it. Maybe there's "
                        "still something in there worth saving.",
                 done="Ooh, Earth tech. No gears, no steam, just a slab of glass with a tiny brain behind it. It's "
                      "full of water. I can't fix the brain, but I know who'd have the trick for drying it. There's "
                      "an Earth lady at Sun Rock who studies volcanoes."),
         q2=dict(title="A Bag of Rice", obj=("deliver", LINDQVIST), lvl=(26, 30),
                 desc="Sprocket wants Dr. Hannah Lindqvist at Sun Rock Retreat to try drying out the phone.",
                 accept="Take it to Dr. Lindqvist at Sun Rock Retreat. She's from Earth, so she'll know what these "
                        "things want. Bring me a drawing of the insides if she opens it, because I'd love to see how "
                        "the tiny brain's wired.",
                 done="You put it in rice, that's the trick, and I keep a jar of it for exactly this. Let's see "
                      "what it does. There, it's on, just for a second. A photo of a dog on a beach, a golden one with a "
                      "stick. Then it's gone. Whoever's phone this was, they had a good dog. I'll keep it, if that's "
                      "all right. I'd like to try again.")),
    dict(id="hf_kelp_journal", name="Kelp-Wrapped Journal", trade="fishing", band=(34, 46),
         desc="A sailor's journal wrapped in kelp and tied with rope, swollen with seawater. The last pages are dry, "
              "as if somebody wrapped it carefully before it went into the sea.",
         q1=dict(title="The Last Dry Pages", to=ULUA, lvl=(36, 40),
                 desc="A Bloodsail mate's journal came up wrapped in kelp. Netsetter Ulua has pulled Bloodsail wrecks "
                      "out of Stranglethorn's water.",
                 accept="Somebody wrapped this journal in kelp and tied it tight before it went over the side, so the "
                        "last pages stayed dry. The skulls in the margins make it a Bloodsail mate's. The fisher who "
                        "works the Snapjaw nets, Ulua, has pulled Bloodsail wrecks out of that water before.",
                 done="It's Bloodsail, yes. The last page names a cove on the Drowned Coast where the mate meant to hide "
                      "from his own captain. He wanted out, and they don't let anyone out."),
         q2=dict(title="The Mate Who Wanted Out", obj=("explore", "Southern Stranglethorn", "The Drowned Coast"),
                 lvl=(38, 42),
                 desc="Netsetter Ulua wants you to find the mate's cove on the Drowned Coast.",
                 accept="Go down to the Drowned Coast and find the cove he wrote about. If he made it, there'll be a "
                        "camp, and if he didn't, there'll be something worse. Either way, he wrote it down so "
                        "somebody would come looking.",
                 done="A cold fire, a hammock and his name carved on a post? Then he made it, for a while at least. "
                      "Good for him. I'll row out and carve a line under his name, to say somebody read it.")),
    dict(id="hf_rubber_duck", name="Rubber Duck Named Mo", trade="fishing", band=(50, 60),
         desc="A small yellow rubber duck, faded almost white on top. Tied round its neck on a bit of string is a "
              "tag, and on the tag in marker it says MO.",
         q1=dict(title="A Duck Named Mo", to=ILYSSA, lvl=(54, 58),
                 desc="A rubber bath duck from Earth came up in your line with a tag that says Mo. Ilyssa Moonwater "
                      "keeps the pier at Nighthaven, where the Wakened keep their list of names.",
                 accept="It's a rubber bath duck from Earth, bobbing about in a fishing pool like it belongs there, "
                        "and the tag round its neck says Mo. The Wakened in Moonglade keep a list of everyone who "
                        "came through with them, and Ilyssa, who keeps the pier there, will know whose name to check.",
                 done="A duck called Mo. I'll ask round, but I know who'll want to see it first. Danny Kowalczyk "
                      "talks about his boys every night on the pier, and the youngest one's called Mo."),
         q2=dict(title="Mo", obj=("deliver", DANNY), lvl=(55, 59),
                 desc="Ilyssa wants Danny Kowalczyk of the Wakened to see the duck.",
                 accept="Take it to Danny. I don't know if it's theirs, and I don't think it matters. He'll want to "
                        "hold something from home that floated all this way.",
                 done="That's not it. Mo's duck had a chip out of the beak, and this one's fine. It's not his. But "
                      "somebody wrote Mo on it, so somebody's kid called Mo had it in a bath somewhere. I'm keeping "
                      "it. When I get home, I'll tell him a duck crossed two worlds looking for him.")),
]

#: Earth junk: things that washed through with the transplants. Vendor trash, with a line each.
EARTH_JUNK = [
    ("ej_car_keys", "Car Keys", "A ring of car keys with a plastic charm on it. Somewhere on Earth there's a car "
     "nobody's going to drive again."),
    ("ej_flip_flop", "Single Flip-Flop", "One blue rubber flip-flop. The other one's out there somewhere, still "
     "looking."),
    ("ej_sunglasses", "Cracked Sunglasses", "Dark glasses with one lens cracked. They make the world look like a "
     "very old photograph."),
    ("ej_soda_can", "Dented Soda Can", "A faded red can, empty, dented on one side. It still fizzes faintly when you "
     "shake it, which shouldn't be possible."),
    ("ej_wristwatch", "Stopped Wristwatch", "A steel watch with a cracked face. Its hands stopped at the minute of "
     "the Integration, like every watch that came through."),
    ("ej_tennis_ball", "Waterlogged Tennis Ball", "A fuzzy ball gone heavy with water. A dog would still love it."),
    ("ej_coffee_mug", "Chipped Coffee Mug", "A white mug with a chip in the rim. Someone drank from it every morning "
     "for years, you can tell."),
    ("ej_tv_remote", "TV Remote", "A black remote with rubber buttons. You press one out of habit, and nothing in the "
     "world changes channel."),
    ("ej_garden_gnome", "Algae-Covered Garden Gnome", "A garden gnome with a red hat and a lot of algae. It's been "
     "underwater for a while and it's still smiling."),
    ("ej_toy_dinosaur", "Plastic Toy Dinosaur", "A small green plastic dinosaur. The bonehunters in the Barrens would "
     "argue about it for a week."),
]
#: Salvage: hauled from the wrecks in salvage pools. Vendor trash worth real coin, and the haul can hold more.
SALVAGE = [
    ("sv_barnacled_lockbox", "Barnacled Lockbox", "A small iron-bound box crusted with barnacles. The lock rusted "
     "shut long ago and the merchants pay for it unopened."),
    ("sv_sodden_coin_purse", "Sodden Coin Purse", "A leather purse heavy with seawater and a few coins. A merchant "
     "will take it off your hands, coins and all."),
    ("sv_goblin_canister", "Leaking Goblin Canister", "A dented goblin fuel canister leaking a rainbow slick. "
     "Somebody in Ratchet will want the fuel back."),
    ("sv_wreck_crate", "Waterlogged Wreck Crate", "A broken crate from a wreck, rope still knotted round it. Salvage "
     "merchants buy these by the pound."),
]

#: Fishing-only gear, from salvage hauls in its band. (id, name, slot, kind, type, identity, ilvl, rarity, flavour)
FISH_GEAR = [
    ("fg_barnacled_signet", "Barnacled Signet", "ring", "armor", None, "agility", 16, "uncommon",
     "A signet ring crusted with tiny barnacles. Whoever wore it last wore it for a long time underwater."),
    ("fg_net_woven_cloak", "Net-Woven Cloak", "back", "armor", None, "caster", 24, "uncommon",
     "A cloak knotted from fishing net and lined with sailcloth. It dries faster than it has any right to."),
    ("fg_kelpweave_sash", "Kelpweave Sash", "waist", "armor", "cloth", "healer", 32, "uncommon",
     "A sash woven from dried kelp. It smells of the sea and it never quite stops being damp."),
    ("fg_tidewalker_boots", "Tidewalker Boots", "feet", "armor", "leather", "agility", 38, "rare",
     "Sealskin boots from a wreck, tar-stitched at every seam. Water rolls off them like they're offended by it."),
    ("fg_saltcrust_bracers", "Saltcrust Bracers", "wrist", "armor", "mail", "hunter", 44, "rare",
     "Mail bracers with salt grown into every ring. They creak like a ship at anchor."),
    ("fg_anchorline_girdle", "Anchorline Girdle", "waist", "armor", "plate", "tank", 49, "rare",
     "A plate girdle with a length of anchor chain worked into its buckle. It holds you where you stand."),
    ("fg_drowned_bell_pendant", "Drowned Bell Pendant", "neck", "armor", None, "healer", 54, "rare",
     "A ship's bell no bigger than a thumb, still ringing faintly. Sailors say you only hear it when you're about to "
     "be saved."),
    ("fg_captains_lost_cutlass", "Captain's Lost Cutlass", "main_hand", "weapon", "sword_1h", "strength", 58, "rare",
     "A cutlass from the bottom of the sea, its hilt wrapped in sharkskin. Its captain went down holding it."),
]

#: The six fishing mounts: one for each kind of water, the rarest catch its pools can give.
MOUNTS = [
    ("brine_crab", "Brine Crab", ("pool_coast", "pool_brine", "pool_storm"),
     "A shore crab the size of a kodo, barnacled and patient, that followed a net up the beach and stayed."),
    ("river_otter", "Great River Otter", ("pool_river", "pool_fresh", "pool_reeds", "pool_oasis"),
     "A river otter as big as a horse and twice as cheerful. It came up out of the reeds and decided you were family."),
    ("glimmer_frog", "Glimmer Frog", ("pool_swamp", "pool_jungle", "pool_moonlit", "pool_glowing"),
     "A swamp frog the size of a kodo with gold flecks that glow at night. It doesn't hop so much as arrive."),
    ("rimefin_walrus", "Rimefin Walrus", ("pool_ice_hole",),
     "A frosty old walrus that came up through an ice hole and has been unbothered ever since."),
    ("cinder_salamander", "Cinder Salamander", ("pool_lava", "pool_bubbling", "pool_plagued"),
     "A lava salamander that came up out of a burning pool and doesn't seem to notice it's out of it."),
    ("abyssal_lurker", "Abyssal Lurker", ("pool_deep_sea", "pool_whirlpool", "pool_cave", "pool_blood"),
     "A deep-sea lurker that walked up the line after its own lure. It lights its own way and grins at everything."),
]

#: Fishing titles, earned rather than bought.
TITLES = [
    ("title_the_master_angler", "the Master Angler", "Catch a thousand fish.", {"fish": 1000}),
    ("title_who_fished_up_the_duck", "Who Fished Up the Duck", "Fish up a rubber duck named Mo.",
     {"found": "hf_rubber_duck"}),
    ("title_the_salvager", "the Salvager", "Haul up fifty loads of salvage.", {"salvage": 50}),
    ("title_of_the_deep", "of the Deep", "Fish up a mount.", {"mount": 1}),
]
