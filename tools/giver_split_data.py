"""The data for tools/build_giver_split.py: who's new, which quests move to whom, and the text in the new voice.

Kyle, 17 Nov 2026: "if there are NPCs who give too many quests, add new NPCs to account for it", then "Aim for 4
please". Each batch below is one town. A quest moves to someone already standing in the town where they have a
reason to give it, and to a new person only where nobody does.
"""

NEW_NPCS = {
    # ---- Light's Hope Chapel ---------------------------------------------------------------------------------------
    "epl_cg_runner": dict(
        name="Runner Pip Calder", zone="lights_hope_chapel", near=(25, 63), race="human", gender="male", variant=3,
        greeting="I run Captain Varden's letters. I used to run them up the road from Crown Guard, and now I run them "
                 "across the square, which is a lot less exciting and a lot more alive."),
    "epl_lh_brother": dict(
        name="Brother Anselm Hart", zone="lights_hope_chapel", near=(45, 38), race="human", gender="male", variant=1,
        greeting="I keep the chapel's books and write the Commander's letters. He tells me what he means, and I take "
                 "out the parts that would start a war."),
    "epl_cg_stablemaster": dict(
        name="Stablemaster Hob Kettering", zone="lights_hope_chapel", near=(14, 56), race="human", gender="male",
        variant=2,
        greeting="I kept Crown Guard's horses, and I've still got the ones that lived. I bought most of them from a "
                 "man I'd now very much like dead."),
    "epl_lh_sapper": dict(
        name="Ruth Calloway", zone="lights_hope_chapel", near=(41, 39), race="human", gender="female", variant=2,
        greeting="I dug coal in the Rhondda for twenty years before the Integration. The Dawn heard I knew mines and "
                 "asked me to look at one. I wish they hadn't."),
    "epl_lh_squire": dict(
        name="Squire Tomas Wren", zone="lights_hope_chapel", near=(82, 42), race="human", gender="male", variant=1,
        greeting="I carry Ser Roland's shield and polish his boots. He says that's how he started, and he was a knight "
                 "of Lordaeron, so I'm not complaining."),
    # ---- The Pale Watch --------------------------------------------------------------------------------------------
    "wpln_pf_escapee": dict(
        name="Pieter Vos", zone="pale_watch", near=(13, 34), race="human", gender="male", variant=2,
        greeting="Faulk's inquisitors kept me in Hearthglen for a month, asking which Scourge lord I served. I drove a "
                 "tram in Rotterdam. They didn't know what a tram was, and they took that as a yes."),
    "wpln_pf_apprentice": dict(
        name="Pia Lind", zone="pale_watch", near=(72, 52), race="human", gender="female", variant=1,
        greeting="I'm Jonah's apprentice and his daughter, in that order when he's working. He won't ask anyone for "
                 "help, so I've started asking for him."),
}

MOVES = {
    # ==== The Bulwark ================================================================================================
    "pls_a_dispatch_for_sorrow_hill": dict(
        giver="wpl_bulwark_captain", why="Venn over the cap; her captain carries her dispatch across the street",
        A="The High Executor's written to the Order of the Pale Flame, and she's asked me to find somebody to carry "
          "it, because she won't walk across the street herself. Those banners over there are theirs. They kept a fort "
          "on Sorrow Hill until the hill got too dead even for them, and now they're inside our wall.\n\n"
          "They wear what used to be Scarlet armour, and some of them used to burn our kind. They also kill the "
          "mindless dead and leave my patrols alone, and my patrols need every friend they can get.\n\n"
          "Take it to their Flamekeeper, Rory Callahan. He stands at the keep's door on the south side of the Bulwark. "
          "Don't let him keep you talking."),
    "pls_what_the_plague_is_made_of": dict(
        giver="wpl_bulwark_surgeon", why="Vesk over the cap; the surgeon next door sends his sample case on",
        A="Dorian's packed your samples into a case, and he's asked me to send it on, because he won't leave his bench "
          "while the Haunt's sample is still moving. He studied under Apothecary Merrow Vane. She's at Sun Rock Retreat "
          "in Stonetalon now, watching the dead get up on the Mulgore side of the mountain with nobody calling them.\n\n"
          "He thinks it's the same sickness as the cauldrons. I've stitched up enough of what comes out of those "
          "fields to think he's right, and I'd like us both to be wrong.\n\n"
          "Take the zeppelin from Tirisfal to Orgrimmar and a wind rider to Sun Rock. Merrow will be the only Forsaken "
          "there. Keep the case upright, and don't let the tauren open it, however politely they ask."),
    "pls_the_school_under_the_island": dict(
        giver="wpl_pf_knight", why="Callahan over the cap; Holt knew the Barovs and already sends you to Caer Darrow",
        A="You've seen the island in Darrowmere, the one with the dead trees and the lit windows. That's Caer Darrow. "
          "I knew the Barovs when they owned it. They sold it to the Cult of the Damned for a promise, and now it's a "
          "school. The Scourge teach necromancy there the way the Kirin Tor teach fire.\n\n"
          "The headmaster is Darkmaster Gandling. Every necromancer who's put a skeleton back on its feet in Andorhal "
          "learned it in his halls. I held that town against his students for a year, and he kept making more.\n\n"
          "He keeps his study at the bottom of the school, below everything else. You won't get there alone, so don't "
          "try. Head north-east out of the Bulwark and down to the lake, take your whole company, and come back and "
          "tell me the school's closed.",
        T="The school's closed, then. They'll open it again one day, they always do, but not this year.\n\n"
          "Rory came through in the Integration with a welding ticket and a bad knee, and he's the one who taught me "
          "you can shut a school. I'll tell him tonight."),
    "pl_ts_crusaders_insignia": dict(
        giver="wpl_pf_quartermaster", why="Marchand over the cap; the Order's quartermaster pays for the badges",
        D="Bring Quartermaster Hollis Burke a handful of Crusader's Insignia from the Scarlets of the Plaguelands.",
        A="Every Scarlet in the Plaguelands carries a Crusader's Insignia, a red flame on a white field. Odile used to "
          "count them, and now the Order's asked me to, since I'm the one who pays for them.\n\n"
          "The Scarlets camp all round Andorhal, south-east of the wall, and every one of them carries a badge. Every "
          "badge is one fewer fanatic burning somebody's farm. Bring me a handful whenever you have them. I'll "
          "write each one down for Odile's book, and then the smith melts them into buckles.",
        T="That's a handful of fanatics who won't be lighting anything tonight.\n\n"
          "Here's the Order's thanks, and some of its coin. Bring me more when you've got them."),

    # ==== Light's Hope Chapel ========================================================================================
    "ple_word_to_lights_hope": dict(
        giver="epl_cg_runner", why="Varden over the cap; his runner carries his report",
        A="Captain Varden wrote this report and then gave it to me to carry, the same as he did at Crown Guard. Back "
          "then I ran it up the road and wondered whether I'd get there. Now it's a walk across the square, and he "
          "still won't hand it over himself, because Dawnbringer asks questions.\n\n"
          "It says the Crusade at Tyr's Hand is moving. I'd carry it myself, but the captain wants me on the road "
          "watch.\n\n"
          "Take it to Commander Eligor Dawnbringer. He stands on the chapel steps at the top of the town. Wait while "
          "he reads it, because he'll have something for you."),
    "ple_a_word_with_the_order": dict(
        giver="epl_lh_brother", why="Dawnbringer over the cap; the chapel's scribe wrote his letter",
        A="The Commander's written to the Order of the Pale Flame, and I wrote it down for him. They're Scarlets who "
          "walked out of the Crusade, and they kill only the mindless dead. Some of the Dawn don't trust them. He'd "
          "like to, and so would I.\n\n"
          "Their Flamekeeper, Rory Callahan, knows the Crusade from the inside. The Commander wants to talk to him "
          "about Tyr's Hand, and about Hearthglen.\n\n"
          "They're camped inside the Bulwark now, at the far west of the Plaguelands. It's a long way, so fly. Give it "
          "to Rory and tell him the Commander would like an answer, not a sermon."),
    "plw_the_sexton": dict(
        giver="epl_lh_brother", why="Edda Marris over the cap; she's asked the chapel to put her family's sexton to rest",
        A="Edda Marris came to the chapel about her family's crypt, and the chapel means me. The family's sexton "
          "buried every Marris for forty years, and he didn't stop when the plague came. Sexton Hollowell is still "
          "down there digging, and the dead he's buried sing for him. The Bone Choir, the farmhands called it, before "
          "they were in it.\n\n"
          "She'd like him put in the ground for good, and the singing stopped. I'll say the words once you've done "
          "the rest.\n\n"
          "His hall's in the middle of the crypt, and the choir sings from the chapel at the head of it. You'll hear "
          "them both. Don't listen to the words, because they'll tell you to lie down.",
        T="It's gone quiet down there, then. Edda will be glad, though she won't say so.\n\n"
          "I'll go down with her next week and we'll say their names together. Somebody in the family should, and "
          "she's the only one of them left breathing."),
    "plw_cartmaster_corin": dict(
        giver="epl_cg_stablemaster", why="Tolliver over the cap; the stablemaster bought his horses off Corin",
        A="Cartmaster Corin gave the crossing its name. He ran a carting business there before the plague, and now he "
          "runs it for the Cult, with the same ledgers and the same smile. I bought every horse in this stable off "
          "him, and he gave me a fair price.\n\n"
          "Bram says you've cleared the square. I want Corin dead and his ledgers burned.\n\n"
          "He's in the old counting house at the crossing. He doesn't fight fair and he'll call everything nearby to "
          "help him, so take friends with you.",
        T="Then the carts stop for good. Bram's burning the counting house tonight, and I've asked to hold the "
          "torch.\n\n"
          "He gave me a fair price on those horses. I keep thinking about that."),
    "ple_the_bones_of_the_east": dict(
        giver="epl_lh_sapper", why="Carrow over the cap; the Bone Mines go to the one person in town who knows mines",
        A="I dug coal in the Rhondda, back home, so when Ysolde found out where the east's dead were going, she sent "
          "for me. The Scourge has dug a mine under the Pestilent Scar. The Bone Miners in it are digging up the dead "
          "to build its constructs, and the Scourge Pit Guards keep them at it.\n\n"
          "I want the digging stopped. It's a bad mine, badly propped, and what they're digging up is people.\n\n"
          "The mine's in the hill under the Scar. Every gallery's deeper than the last, so it's a long walk down. The "
          "pit guards will keep you out if they can.",
        T="Those were people once, the bones they were digging up. Ysolde's going to say the prayer for all of them "
          "at once.\n\n"
          "I've been reading the Scourge's tallies off the pit walls. Somebody down there weighs everything that comes "
          "out, and I'd like him gone next."),
    "ple_the_overseer": dict(
        giver="epl_lh_sapper", why="Dawnreach over the cap; the Bone Mines chain stays with one giver",
        A="The tallies on the pit walls all end at one place. Overseer Marrowgrim sits in the pit at the bottom with a "
          "meat hook and a cart, and nothing leaves that mine that he hasn't weighed. We had a man like that at the "
          "colliery, and he was a lot less dangerous.\n\n"
          "I want him dead before the Scourge has bone enough for another colossus.\n\n"
          "He's in the marrow pit at the end of the deepest gallery. He's big and he's slow until he isn't, so don't "
          "stand where that hook can reach you, and watch out for the cart.",
        T="The Scar's quieter already, and Faelis says the bats have stopped circling it.\n\n"
          "There's still one more thing down there. Marrowgrim's tallies say everything went somewhere else before it "
          "came to him."),
    "ple_the_ossifier": dict(
        giver="epl_lh_sapper", why="Dawnreach over the cap; the Bone Mines chain stays with one giver",
        A="I've found a workshop off the middle of the Bone Mines, and Marrowgrim's tallies say everything the mine "
          "digs up goes there first. The Ossifier is a necromancer, and he's the one who turns the east's dead into "
          "the Scourge's constructs.\n\n"
          "Close his workshop, and I'll bring the roof down on it after.\n\n"
          "It's off the middle gallery, up a short passage. He'll be wearing bone armour, and it's thick, so be "
          "patient with it. Break that first, then break him.",
        T="That's the end of the Bone Mines, and the end of the constructs coming out of them. I'll set the charges "
          "tomorrow.\n\n"
          "I never liked closing a pit, back home. I'm glad to be closing this one."),
    "pl_ts_invaders_scourgestones": dict(
        giver="epl_lh_quartermaster", why="Hale over the cap; the Dawn's quartermaster pays for the heavy shards",
        D="Bring Quartermaster Hasana Reed a handful of Invader's Scourgestones from the Scourge in the eastern "
          "Plaguelands.",
        A="The Scourge that march in the east carry heavier shards. Invader's Scourgestones, we call them, and they're "
          "cold enough to hurt. The dead round Stratholme and Terrordale carry most of them.\n\n"
          "Archmage Hale breaks the little ones himself. These go in a lead box under my counter until the Dawn can "
          "carry them somewhere safe, and the Dawn pays twice over for every one.\n\n"
          "Bring me a handful whenever you can. Wear gloves, because they bite.",
        T="These are heavy ones. Every shard here is one less thing walking toward the wall.\n\n"
          "Into the box they go. Come back when you've got more."),
    "plw_spores_for_the_sanctuary": dict(
        giver="epl_cg_flight", why="Dr. Sun over the cap; the bat keeper finds her a courier south",
        A="Dr. Sun's sealed a sample of the vale's spores in wax, and she's asked me to find somebody going south, "
          "because she's busy with the vale. There's a botanist at the Emerald Sanctuary in Felwood, Yuki Hashimoto, "
          "who's cataloguing everything that grows back in corrupted ground. If anyone's seen something like this, "
          "it's her.\n\n"
          "The doctor would like her to compare it with what grows in Felwood.\n\n"
          "Take the zeppelin from Tirisfal to Orgrimmar, then go north through Ashenvale to Felwood. Yuki's at the "
          "Sanctuary, probably on her knees in a flowerbed. Don't break the wax, and don't let a bat sit on it."),
    "plw_the_three_ziggurats": dict(
        giver="epl_lh_flight", why="Vey over the cap; the flight master sees the ziggurats from the air",
        A="I fly over Stratholme most days, and from up there you can see what the ground can't. The Scourge raised "
          "three ziggurats in the dead half of the city, and each one has a keeper. Nerub'enkan is a spider lord out "
          "of the north. Baroness Anastari was a lady of the court and is a banshee now. Maleki the Pallid is a lich "
          "who keeps his ziggurat as cold as a tomb.\n\n"
          "While those three stand, the Baron's gate stays shut. Osric buries what comes out of the city, and he'd "
          "like it to stop. Kill all three keepers and the way opens.\n\n"
          "Go in from the service gate, where the Scourge bring their carts.",
        T="Then the gate's open. I flew over this morning, and the ziggurats have gone dark.\n\n"
          "Osric says he can stop digging for a while. You'll want to go through, I expect."),
    "plw_sigils_of_the_fallen": dict(
        giver="epl_lh_squire", why="Ashcombe over the cap; his squire keeps the tally while he watches the gate",
        A="The Gate Death Knights still wear the sigils of the houses they served when they were alive. Barov, "
          "Mardenholde, and a dozen others. Ser Roland says the houses that are left don't know what became of their "
          "sons and daughters.\n\n"
          "He'd like the sigils back, so he can tell them, and he's asked me to keep the tally while he watches the "
          "gate.\n\n"
          "The death knights wear them on their breastplates. Cut them off and bring them to me. Ser Roland will know "
          "every house by its colours.",
        T="That's Barov, and that's Mardenholde. Ser Roland says this one's his own cousin's house.\n\n"
          "He'll write to every family that's left, and I'll carry the letters. It's the least they deserve."),
    "plw_carrion_grubs": dict(
        giver="epl_cg_innkeeper", why="Lindgren over the cap; the grubs got into Greta's larder at Crown Guard",
        D="Kill Carrion Grubs along the road through the western half of the Eastern Plaguelands.",
        A="The Carrion Grubs got into the larder at Crown Guard before we left, and now they're all along the road "
          "west. They eat everything that dies out there, and then they eat everything that's alive and slow. Kaia's "
          "lost every snare she's set this month, and I've lost a cart of turnips.\n\n"
          "They swarm the road and the ditches beside it. They're slow and they're soft, but there are always more of "
          "them. Burn them if you can, because they don't like it.",
        T="That's the road clear of them for a while, anyway. I'll send the next cart out tomorrow.\n\n"
          "Here, take a pie for the road. It isn't crow, I promise."),

    # ==== The Pale Watch =============================================================================================
    "pln_a_letter_for_brill": dict(
        giver="wpln_pf_innkeeper", why="Fischer over the cap; the innkeeper sends Novak his beer and Lena's letters",
        A="Lena's written to the Order's man in Brill, and she's asked me to send it with someone, since I send him a "
          "cask of beer every month anyway. Flamewarden Teodor Novak watches the Scarlet Monastery from a window over "
          "the inn, and he's very good at it.\n\n"
          "If Hale marches out of Hearthglen, the Monastery marches with him. Teodor needs to know what Lena knows.\n\n"
          "Go south to the Bulwark and out its west gate into Tirisfal, then on to Brill. Teodor lodges over the inn. "
          "He'll offer you a drink, and you should take it. It's my beer, and it's the only good beer in Tirisfal."),
    "pln_travellers_keepsakes": dict(
        giver="wpln_pf_innkeeper", why="Brandt over the cap; the last bed before Hearthglen keeps the travellers' things",
        A="Mateo told me about the Skeletal Wanderers on the roads, and I can't stop thinking about them. This is the "
          "last bed before Hearthglen, and some of those travellers might have slept under this roof. If they had "
          "pockets, some of them still have whatever was in them. A ring, a letter, a toy for somebody waiting at "
          "home.\n\n"
          "I'd like to write down what they were. Somebody might still be waiting for one of them, and the Order "
          "keeps a book of names at the Bulwark.\n\n"
          "They walk the roads all round the Watch. Not every one of them has anything left. Bring me what you find "
          "and I'll write it all down.",
        T="A pipe, a thimble, a child's wooden horse. Every one of these belonged to somebody.\n\n"
          "Odile at the Bulwark will want these for her book. I'll send them south with the next cask."),
    "pln_a_serum_for_felwood": dict(
        giver="wpln_pf_roostkeeper", why="Kowal over the cap; the hawks won't carry glass, so the roostkeeper finds a courier",
        A="Noah's made a serum. It doesn't cure anything, and he wants me to be clear about that, but it slows the "
          "plague down long enough to matter. He asked me to send it with a hawk, and the hawks won't carry glass, so "
          "I'm asking you.\n\n"
          "There's a doctor at the Emerald Sanctuary in Felwood, Dr. Nkechi Adeyemi, who's treating a sickness that "
          "sounds a lot like this one. She sent Noah the kit he's been using all month, and he'd like to send her "
          "something back.\n\n"
          "Take the zeppelin from Tirisfal to Orgrimmar, then go north through Ashenvale to Felwood. The Sanctuary's "
          "the clean glade in the middle of it. Keep the vial out of the sun."),
    "pln_plague_bats": dict(
        giver="wpln_pf_roostkeeper", why="Byrne over the cap; the bats have started going for the hawks",
        A="The Plague Bats come out over the Thondroril at dusk, and they've started going for my hawks. Oona's been "
          "fighting them off the river with a fishing rod, and I've lost a hawk to them already this month. I'm sure "
          "they carry the plague.\n\n"
          "They roost in the trees along the river. They're fast, so don't chase them. Stand still on the bank and let "
          "them come to you, because they will.",
        T="The hawks can fly at dusk again, and Oona can fish. That's a better evening for everyone.\n\n"
          "Here's something for your trouble, and Oona says she'll keep a fish back for you at supper."),
    "pln_high_inquisitor_faulk": dict(
        giver="wpln_pf_escapee", why="Crane over the cap; Pieter is one of the newcomers Faulk questioned",
        A="High Inquisitor Faulk runs the inquisition at Hearthglen. He kept me in a cell there for a month. He's the "
          "one who decided the newcomers were the Scourge's agents, and Amalie says he decided it on a Tuesday, "
          "between breakfast and prayers.\n\n"
          "On feast days he walks the fields himself, with the Hearthglen Inquisitors at his back. Today's a feast "
          "day.\n\n"
          "He'll be in Hearthglen Fields, below the walls, close to the gate. He's got a temper and a lot of fire, and he heals himself when "
          "he's hurt. Bring friends, and bring someone who can stop his prayers.",
        T="Then it's done, and the inquisition's got nobody to lead it.\n\n"
          "I keep waiting to feel something. I think maybe I feel lighter. I'll tell Amalie tonight."),
    "pln_saw_blades": dict(
        giver="wpln_pf_apprentice", why="Lind over the cap; his daughter asks for the help he won't",
        A="My father can't cut timber without saws, and the Crusade took every saw in the Plaguelands up to the "
          "Northridge Lumber Camp. He's been shaping planks with a hatchet, and it shows. He won't ask anyone for help, so I'm "
          "asking for him.\n\n"
          "The Scarlet Lumberjacks carry good steel blades, forged in Hearthglen. They carry them on their backs in "
          "the woods.\n\n"
          "Bring me the blades and leave the handles. He'll want to make his own handles. He's a carpenter, not a "
          "smith, and he'll tell you so.",
        T="These are beautiful blades. Hearthglen's smiths know their business, I'll give them that.\n\n"
          "Don't tell my father I asked. We'll have a proper sawpit at the Watch by the end of the week, and he can "
          "think it was his idea."),
}

# Quests that stay where they are, but whose hand-in now has to say who gives the next step.
TEXT = {
    "pls_the_writhing_haunt": dict(
        T="Something's moving in this one. Look at that.\n\n"
          "I need someone who knows more about the walking dead than I do, and the only one I trust is on the other "
          "side of the sea. Surgeon Grey's sending a case to her for me, so go and see him a few doors along the "
          "street."),
    "plw_the_crossings_abominations": dict(
        T="That's the crossing's muscle gone.\n\n"
          "There's only one man left running the carts. Hob Kettering, our stablemaster, knows him better than I do. "
          "He's just along from me, and he'd like a word with you."),
    "plw_the_family_crypt": dict(
        T="Thank you. My husband's grandmother is down there somewhere, and I hope she's back where she belongs.\n\n"
          "There's more, though. Something's still singing down there, and it isn't any hymn I know. I've asked "
          "Brother Anselm at the chapel to help, so go and see him."),
}
