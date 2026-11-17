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


# ======================================================================================================================
# Batch 2: Silverpine South, Deathknell, the Undercity, Bloodmoon Village, Eastern Tirisfal, the Sepulcher and Brill.
# These zones put the giver's speech in the description and a short parting line in accept_text, and the moves keep
# that.
# ======================================================================================================================
NEW_NPCS.update({
    "sp_pyre_cipher_clerk": dict(
        name="Cipher-Clerk Avery Lusk", zone="silverpine_south", near=(87, 92), race="forsaken", gender="male",
        variant=2,
        greeting="Loremaster Sennarath sent me down from the Undercity to copy every mark the cult leaves in "
                 "Pyrewood. Brand lets me sit by his fire, as long as I keep the door shut."),
    "sp_amber_apprentice": dict(
        name="Apprentice Nell Coombe", zone="silverpine_south", near=(67, 46), race="forsaken", gender="female",
        variant=1,
        greeting="I was one of Haskell's apprentices at the mill. There aren't many of us left, and he's got the rest "
                 "of us sorting nails so we don't go near the tower."),
    "fen_village_wisewoman": dict(
        name="Old Wenna", zone="bloodmoon_village", near=(18, 25), race="forsaken", gender="female", variant=1,
        greeting="I've lived on Fenris longer than anyone left in this village, alive or dead. I know the island's old "
                 "stories, and I've started to wish I didn't."),
    "fen_rearguard_liaison": dict(
        name="Deathguard Halsey", zone="bloodmoon_village", near=(29, 27), race="forsaken", gender="male", variant=2,
        greeting="The Rear Guard sent me to Fenris to write down what's happening here. They don't believe a word of "
                 "my reports yet, so I've started asking for proof."),
    "et_cave_deathguard": dict(
        name="Deathguard Mira Holloway", zone="eastern_tirisfal", near=(58, 111), race="forsaken", gender="female",
        variant=1,
        greeting="I hold the mouth of the cave for Boneward Calder. He goes down to study the bones, and I go down to "
                 "break them."),
})

MOVES.update({
    # ==== Silverpine South ===========================================================================================
    "sps_deserter_tags": dict(
        giver="sp_south_quartermaster", why="Dallow over the cap; the quartermaster keeps the March's roll",
        D="Sergeant Dallow and I keep the March between us. He keeps the soldiers, and I keep their kit and their "
          "roll. Every soldier in the March carries an iron tag with a number stamped on it, and every number matches "
          "a line in my book.\n\n"
          "The deserters at Valgan's Field still wear theirs. Somebody from the Undercity will come down this road one "
          "day and ask how many walked off, and they'll want to hear that it was a few. Dallow wants to tell them who, "
          "and by what number, and he'll read it out of my book.\n\n"
          "Take the tags off the Field Deserters and bring them to me.",
        A="Iron tags, stamped with a number. Off the deserters at Valgan's Field.",
        T="That's every number I needed, and I'll enter each one against the roll tonight, in ink.\n\n"
          "Dallow can open the book now and tell the Undercity exactly who walked off. A list of names is a lot harder "
          "to wave away than a guess."),
    "sps_pyre_cultists": dict(
        giver="sp_pyre_cipher_clerk", why="Brand over the cap; the Undercity's clerk wants the cult's houses cleared",
        D="The cult in Pyrewood has taken the burned houses at the south end of the village, and they cast over the "
          "dead hearths, the stone ones that are all that's left of those homes. Brand's listened from the lane, and "
          "he doesn't know the name they pray to. He was the hearthwarden here when the village had people in it, so "
          "he's heard most of them.\n\n"
          "Loremaster Sennarath sent me to copy their marks, and I can't get near enough to copy anything while "
          "they're in there. Brand says something answers when they call, and I believe him.\n\n"
          "Clear the Pyrewood Cultists out of the burned houses, and I'll go in after you and start copying.",
        A="The burned houses at the south end of Pyrewood. They cast over the dead hearths.",
        T="Nothing answered tonight. Brand stood in the lane for an hour to be sure, and so did I.\n\n"
          "The walls in those houses are covered in the cult's marks. I'll be copying them for a week."),
    "sps_pyre_sigils": dict(
        giver="sp_pyre_cipher_clerk", why="Brand over the cap; the sigils go to the clerk who reads ciphers",
        D="Every one of the cultists carries an iron sigil. Brand took one off a body and gave it to me, and it's "
          "properly cut, not scratched. That means somebody had these made by a smith, and in a quantity, for a cult "
          "living in burned houses in a village with nobody alive in it.\n\n"
          "The Loremaster reads this sort of cipher. I'd rather send him a handful than the one, because a handful "
          "lets him lay them side by side.\n\n"
          "Take the sigils off the Pyrewood Cultists and bring them to me.",
        A="Iron sigils, off the Pyrewood Cultists. They're stamped, not scratched.",
        T="They aren't all the same. Look, that one and that one are different at the edge.\n\n"
          "So the cipher has variants, and that's a rank, or a house, or a posting. These people are organised "
          "somewhere other than here, and the Loremaster's going to want to know where."),
    "sps_ashes_south": dict(
        giver="sp_pyre_cipher_clerk", why="Brand over the cap; he gave his phial of ash to the clerk to send on",
        D="Brand scraped a phial of ash off the hall steps the night the doors were barred, and he gave it to me, "
          "because neither of us knows what's in it. The cult burned something in that hall, and it wasn't "
          "wood. Brand's been a hearthwarden his whole life, and he says it went to ash the wrong colour and it hasn't "
          "stopped being warm.\n\n"
          "There's nobody in Silverpine who can tell us what it is. There's an apothecary at Southpoint Tower, down in "
          "Hillsbrad, who's had nothing but blight to work on for years and who'll probably open it in the road.\n\n"
          "Take it to her anyway. I'd rather have a reckless answer than none.",
        A="To the apothecary at Southpoint Tower in Hillsbrad. She'll probably open it in the road.",
        T="You've come from Pyrewood? Give it here, I'm not waiting until I'm indoors.\n\n"
          "This isn't from here. I don't mean Hillsbrad and I don't mean Silverpine. I've handled blight from every "
          "corner of this continent, and this ash isn't from any of it.\n\n"
          "Sit down and start at the beginning, and don't leave anything out."),
    "sps_sfk_hounds": dict(
        giver="sp_south_hunter", why="Rynn over the cap; the post's hunter takes the keep's kennels",
        D="I hunt the hills for the Rear Guard's table, and I know what a wolf does when it's hungry. The worgs in "
          "Shadowfang Keep don't do any of it. They're Arugal's own, kennelled and fed on a schedule, on things that "
          "used to be people.\n\n"
          "Rynn says a fed worg isn't a wolf any more, because it's never had to fail at a hunt, and she's right. A "
          "wolf I can track. These sit in their kennels and wait to be let out.\n\n"
          "Thin the kennels before somebody does let them out. Kill the Keep Worgs and the Slavering Worgs both.",
        A="The kennels in Shadowfang Keep, west of the bailey.",
        T="That's a thinner pack, and a fight I can pick instead of one that picks me.\n\n"
          "The man who keeps them is still in there, though, and he keeps them hungry."),
    "sps_sfk_rethilgore": dict(
        giver="sp_south_hunter", why="Rynn over the cap; the kennel-master follows the kennels",
        D="Rethilgore keeps the hounds in Shadowfang, and he keeps them hungry on purpose. A fed hound sleeps, and a "
          "hungry one watches the door.\n\n"
          "He was a decent man in Pyrewood. Brand knew him, and so did half the village. I've watched him through a "
          "glass, and he's still careful. He checks the chains and he counts the hounds. There's enough of him left "
          "to do the job properly, and not enough to stop doing it.\n\n"
          "I'd like him buried. He's in the big pen in the west wing, and he'll have a chain in his hand.",
        A="Shadowfang Keep, in the kennels. He's in the big pen in the west wing.",
        T="He fed the hounds first, even at the end. You could see it on them.\n\n"
          "I can respect that, I suppose, and I'd rather not have had to."),
    "sps_sfk_moonwalkers": dict(
        giver="sp_sfk_nightwatch", why="Rynn over the cap; the night watch hears the keep's chanting",
        D="I keep the night watch on the Shadowfang gate, and on a full moon you can hear the keep chanting from here. "
          "That's the moonwalkers. Arugal's cult is half sorcerers and half worgen who are still turning, and the "
          "chanting is how they get the rest of the way.\n\n"
          "The darksouls are what's at the end of it. So the keep isn't a garrison with casters in it. The casters are "
          "making the garrison, out of whatever walks in.\n\n"
          "Go in wherever you hear chanting, and kill the Shadowfang Moonwalkers and the Shadowfang Darksouls. Kill "
          "the casters first, every time.",
        A="Shadowfang Keep, on its hill south-west of the Peril. Go wherever you hear chanting, and kill the casters "
          "first.",
        T="The chanting stopped early tonight. That's the first quiet full moon I've had on this gate.\n\n"
          "They'll make more, but they'll make them slower now."),
    "sps_sfk_pickets": dict(
        giver="sp_sfk_nightwatch", why="Marl over the cap; Pell has the nights on the same gate",
        D="Marl has the days on the Shadowfang gate and I've got the nights, and the road past the pickets is the worst "
          "of both. The ghouls and the stalkers crowd it, and they aren't coming down it. They're pressed up against "
          "it, facing the keep, as if something inside were calling them.\n\n"
          "There's a party going in soon, and I'd rather they spent what they've got inside instead of on the way "
          "up.\n\n"
          "Clear the Rotting Ghouls and the Feral Worgen Stalkers off the keep road.",
        A="The keep road past Beren's Peril, south of here. They're pressed against it, facing the keep.",
        T="The road's open to the portcullis.\n\n"
          "They'll drift back. Whatever's pulling them hasn't stopped pulling, but a party can get up there now "
          "without arriving tired."),
    "sps_at_tomes": dict(
        giver="sp_amber_scribe", why="Orsolo over the cap; his scribe collects the pages",
        D="The tome wraiths in Ambermill Tower are the pages of a book that learned to fly, and Magister Orsolo has "
          "asked me to collect them, since I'm the one who writes everything down. They haunt the galleries, and "
          "they're all from the same book. Nobody's noticed that, because nobody's held two of them side by side.\n\n"
          "The Magister thinks he knows who wrote it. He won't say who until he's sure, and I've stopped asking.\n\n"
          "Take the torn pages off the Tome Wraiths, enough that he can lay them out together. And don't read any of "
          "it aloud, not even to yourself.",
        A="Off the Tome Wraiths in the galleries of Ambermill Tower. Don't read aloud.",
        T="The Magister knows this hand. I watched his face when I showed him.\n\n"
          "It was Hawren, who taught him to read. He'll want to see you."),
    "sps_at_spellblades": dict(
        giver="sp_amber_apprentice", why="Haskell over the cap; his apprentice lost friends to the spellblades",
        D="I was an apprentice at Ambermill's sawmill, under Haskell. Our saws were enchanted to run themselves, and "
          "that was his idea, and he was proud of it for years. The Animated Spellblades in the tower carry the same "
          "enchantment. They're bright and quick and they don't care who they cut, because nobody gave them the part "
          "that decides when to stop.\n\n"
          "Two of my friends went into that tower on Haskell's say-so, to see whether the enchantment was the same as "
          "ours, and it is. They didn't come out, and he's had the rest of us sorting nails ever since.\n\n"
          "Break the spellblades. They're all through the tower, and they're the ones that glint.",
        A="The Animated Spellblades, all through Ambermill Tower, through the waygate south-east of here.",
        T="It's quieter in there, then. I'll tell Haskell myself.\n\n"
          "He won't let us go back in for a month, but at least there's nothing in there now to keep us out."),

    # ==== Deathknell =================================================================================================
    "dk_stray_cull": dict(
        giver="dk_sexton_marrow", why="Krell over the cap; the sexton keeps the graveyard the strays foul",
        D="The dogs and the rats have always come to the graveyard, and we've always let them, because what's in the "
          "ground is past caring. Something in the soil has turned them. The Plagued Strays are sick in a way I "
          "haven't got a word for, and they've started going for the newly risen.\n\n"
          "You'll meet people out there who woke up this week and can't work out which way the village is. They "
          "can't defend themselves. A fortnight ago, neither could you.\n\n"
          "Thin the strays, and the Grave Rats with them. The rats carry it into the stores, and then it's everyone's "
          "problem.",
        A="Round Deathknell's graves and the gate. Mind the newly risen, because they can't defend themselves.",
        T="That's the yard safe for the ones still coming up.\n\n"
          "You'll see a few of them wandering. Leave them be. They'll find their way, and I'll bury the ones who "
          "don't."),
    "dk_scavenger_scraps": dict(
        giver="deathknell_undertaker", why="Krell over the cap; the undertaker keeps the village stores",
        D="I keep Deathknell's stores, and they're shrinking. Nobody here eats, so it isn't food. It's salt tins, "
          "rope, bandages and lamp oil, the things that keep a settlement standing.\n\n"
          "The Ragged Scavengers out past the fence have been dragging it off, and they take whatever glints without "
          "the faintest idea what any of it does.\n\n"
          "I want all of it back. The Dark Lady keeps careful accounts and so do I, and that's worth learning on your "
          "first day. We aren't animals picking over a ruin.",
        A="The Burned Farmstead past the fence, where the scavengers den. Bring back every piece, because I'll know "
          "what's missing.",
        T="That's all of it. I've checked it against my list, item by item.\n\n"
          "That list is why there's a Deathknell at all. Remember that when somebody tells you we're just corpses "
          "that got lucky."),
    "dk_scout_hollow": dict(
        giver="wt_vale_ranger", why="Krell over the cap; the vale's ranger does his scouting",
        D="Gresk thinks the spiders at his claim are wandering in, and they aren't. There are too many and they come too "
          "steadily, and a wandering population thins when you cull it. This one doesn't.\n\n"
          "There's a cave beside the claim, Night Web's Hollow, and I think it's pouring them out like a spring. "
          "Before anybody goes in there to deal with it, Krell wants eyes on the inner strand, and he asked me for a "
          "scout. I'm asking you.\n\n"
          "Get to the inner strand of the Hollow, look at what's there, and come back out.",
        A="Night Web's Hollow, the cave beside the claim. Get to the inner strand and come back out.",
        T="A brood chamber, that deep in? Then it's worse than I thought.\n\n"
          "Go and tell Krell. He'll want somebody to finish it, and he'll want it to be you."),
    "dk_verrick_crypt": dict(
        giver="wt_crypt_keeper", why="Verrick over the cap; the crypt keeper walks crypts for a living",
        D="Verrick's been watching the Scarlet Crypt from his rocks for weeks, and he won't go down the nave. I keep "
          "crypts myself, so he asked me, and I'm asking you, because my knees won't take those stairs.\n\n"
          "It's the Crusade's real foothold in this valley. There's a chapel, an ossuary, a reliquary, and a High "
          "Inquisitor who likes confessions. Something is holding the doors at the far end shut, and it isn't a "
          "bar.\n\n"
          "Walk the nave to the far doors and look at what's holding them. Don't try to clear it. Just look, and come "
          "back.",
        A="Down the nave of the Scarlet Crypt to the far doors. Look at what's holding them, then come back.",
        T="Held from the inside, by something that wanted to be in there? Then this stopped being a camp outside a "
          "crypt a long time ago.\n\n"
          "I'll tell Verrick. He won't like it, but he'll want to know."),
    "dk_verrick_vaults": dict(
        giver="dk_sexton_marrow", why="Verrick over the cap; the sexton wants the valley's dead out of the ossuary",
        D="Verrick tells me the High Inquisitor's dead and the Scarlet Crypt still isn't ours. There are two vaults "
          "left, one on either side.\n\n"
          "The ossuary's under Valdric Bonewarden. That's where the Crusade put the dead they never finished burying, "
          "and most of them are our dead, from this valley. I've been asking to bury them properly since the day I "
          "woke up.\n\n"
          "The reliquary's on the other side, under Brother Wystan, and whatever the Scarlets thought worth saving is "
          "in there. Kill them both and open the vaults, and the crypt belongs to the valley again.",
        A="Both vaults of the Scarlet Crypt: the ossuary under Valdric, and the reliquary under Wystan.",
        T="Both vaults are open, and the whole crypt with them.\n\n"
          "I'll start bringing our dead out of the ossuary tomorrow and put them in ground that belongs to them. "
          "Whatever's in the reliquary can go to Krell, and then to the Undercity. Go and find Krell, too. He's run "
          "out of things to send you at."),

    # ==== The Undercity ==============================================================================================
    "ucq_sennarath_scroll": dict(
        giver="uc_market_scribe", why="Sennarath over the cap; the market scribe sends his sealed scroll",
        D="Loremaster Sennarath sealed this scroll in grave-wax and left it with me to send, because he won't let it "
          "leave the city except in a steady pair of hands, and he's decided mine shake. He's been tracking the "
          "Cult's cipher across half of Lordaeron, and he can read most of it. The rest is a key, and he thinks "
          "Keeper Oswin at Raven Hill has it.\n\n"
          "Oswin's been reading the same markings on his own stones for longer than the Loremaster's been working, "
          "and he's never written any of it down.\n\n"
          "Put it in Oswin's hand, and don't open it. The wax only takes one impression, and the Loremaster will "
          "know.",
        A="Up the shaft into Tirisfal, south through the Rear Guard into Silverpine, and down the Trunk Road to Raven "
          "Hill Cemetery on its west side. Give it to Keeper Oswin.",
        T="That's Sennarath's seal. He writes the way I read, slowly and twice.\n\n"
          "Give me a moment. There'll be a reply, and it'll be shorter than he'd like."),
    "uc_dalaran_question": dict(
        giver="uc_mage_trainer", why="Sennarath over the cap; the shield over Dalaran is a mage's question",
        D="This is curiosity rather than orders, so you can say no. The Ruins of Dalaran stand at the edge of "
          "Hillsbrad under a shield the Kirin Tor raised and have never lowered. I studied under that shield when I "
          "was alive, and I've walked round it a great many times since.\n\n"
          "Word has reached the Apothecarium that a party of blood elves got underneath it three years ago, when the "
          "world shook and a great many sealed things stopped being sealed. If the word's true, they've been living "
          "under the ruins ever since. Nobody has confirmed it.\n\n"
          "Go and look, and bring me something better than a rumour.",
        A="Into eastern Hillsbrad, within sight of the Dalaran shield. Look, but don't start anything.",
        T="Lights under the shield, and movement on a schedule? They've been down there three years, the same three "
          "years the rest of us have spent learning what the sky's doing now.\n\n"
          "This goes to the Apothecarium tonight. I expect somebody more senior than me will want to meet you."),
    "ucq_hillsbrad_writ": dict(
        giver="uc_market_scribe", why="Wrenfall over the cap; the scribe who drew up the writ sends it",
        D="The Executor signed a writ for the commander at Tarren Mill, and I drew it up for him. It gives her "
          "standing authority to act in the valley without writing north first. It sat on his desk for a month, "
          "because signing it meant admitting he can't run Hillsbrad from here.",
        A="Take it south through Silverpine, down into Hillsbrad, and east to Tarren Mill, the mill town cut in half "
          "by a water channel. Commander Thorne holds it.\n\n"
          "The Executor would rather keep that authority for himself. He signed it anyway, because the other choice "
          "was losing the valley by post.",
        T="He signed it? I've been asking for this for two years, and I'd stopped expecting it. This is permission to "
          "stop waiting.\n\n"
          "There's Alterac money in these hills, there are wizards in a scrap camp, and there's a man in Durnholde "
          "keeping a court. I can go after all three now without writing north first."),
    "sm_the_bloodmages_stone": dict(
        giver="uc_alchemist", why="Sable over the cap; her alchemist wants the stone on his bench first",
        D="Alchemist Dunmere has heard that the Crusade keeps a blood mage in the Graveyard's tomb, Bloodmage "
          "Thalnos, who's kept himself alive a long time on other people.\n\n"
          "He wants the stone Thalnos does it with. The Master Apothecary has her own uses for something that keeps a "
          "heart beating, and she's asked him to find out how it works.",
        A="Thalnos holds Honor's Tomb, at the far end of the Graveyard past the open burial ground. His ward drinks "
          "spells, so hit him with steel. The stone will be on him. Bring it to me, not to the Master Apothecary, "
          "because I want a look at it first.",
        T="It's still warm, and it's still beating.\n\n"
          "I'll take it apart tonight and send what I learn up to Lorrane. Don't mention it in the tavern."),

    # ==== Bloodmoon Village ==========================================================================================
    "fen_banshee_locks": dict(
        giver="fen_village_wisewoman", why="Gravemoss over the cap; Old Wenna has the theory about the locks",
        D="When a banshee fades on the strand, she leaves a lock of hair behind, and she does it every time. Gravemoss "
          "used to burn them, and I told him to stop, because I think they're anchors. A thing made of grief and air "
          "leaves behind the one part of a person that lasts after death, and I don't think that's an accident.\n\n"
          "I think that's what holds them to the strand, and it's why they keep coming back however often the village "
          "puts them down.\n\n"
          "Bring me the locks off the Isle Banshees. I'll bury them under the village stones, in ground that was ours "
          "before any of this, and we'll find out whether an old woman is right about something.",
        A="Gather the locks the banshees leave behind when they fade on the strand.",
        T="I've buried them one at a time, under the stones, and said a name over each. I made the names up, and I "
          "won't pretend otherwise.\n\n"
          "But a thing in the ground with a name over it makes a grave, and I'd rather they were anchored here than out "
          "on the strand."),
    "fen_noble_signets": dict(
        giver="fen_rearguard_liaison", why="Merrin over the cap; the Rear Guard's man wants the crests for Silverpine",
        D="The Cursed Nobles in Fenris Proper still wear their house signets. They've lost their faces and the use of "
          "their hands, and they haven't lost the rings. Merrin noticed it first, and she told me.\n\n"
          "I don't want them for the gold. I want the crests. The Rear Guard says Fenris was a minor holding with a "
          "minor lord and a local misfortune. I'd like to put the crests on a table in Silverpine and ask them what "
          "all those noble houses were doing at a minor lord's table on the night the curse was cast.\n\n"
          "It won't change anything on this island, but it'll change how seriously the mainland takes it.",
        A="Take the rings off the Cursed Nobles in the forecourt and the manor grounds.",
        T="Every one of these is from a different house. The Rear Guard will have to read my next report now."),
    "fen_altar_moonhowl": dict(
        giver="fen_rearguard_liaison", why="Orlan over the cap; the moon-fangs are the Rear Guard's proof",
        D="The Rear Guard wants proof that the curse is still alive before they'll send anyone else to Fenris, and "
          "Orlan's told me the best proof there is. The worgen at Shadowpine Altar howl at a moon the cavern can't "
          "see. There's no sky down there, and they still howl on the nights the moon is full and stay quiet when it "
          "isn't, and they're never wrong.\n\n"
          "The wraiths move with them, on the same nights.\n\n"
          "Thin the Moonhowl Worgen and the Altar Wraiths, and bring me the moon-fangs off the worgen. Half go to "
          "Orlan for the cairn he's building at the stair-head, and half go to Silverpine with my report.",
        A="It's north-west of here, through the arch in the ridge and down into Shadowpine Altar. The worgen and the "
          "wraiths hold its circles and the long roads between, and the fangs come off the worgen.",
        T="That's a cairn's worth for Orlan and a box for the Rear Guard. The curse should keep its distance for a "
          "season, and Silverpine should stop calling it a local misfortune."),
    "fen_altar_tael": dict(
        giver="fen_village_wisewoman", why="Orlan over the cap; the curse-keeper is in Old Wenna's stories",
        D="Orlan's told me about Curse Keeper Tael, in the Moon Circle at Shadowpine Altar. Tael feeds the moonstone "
          "whatever the cult throws at it, and he's been doing it for centuries.\n\n"
          "Here's what I can't get past. The stone doesn't need a keeper. Orlan's watched long enough to be sure, and "
          "the old stories say the same. It does what it does whether Tael's there or not. He isn't keeping the curse "
          "going. He's attending it, the way a servant attends a master who's long gone.\n\n"
          "That frightens me more than anything else on this island. Kill him, and don't watch the moonstone while "
          "you do.",
        A="Go north-west to Shadowpine Altar, then east through its caverns to the Moon Circle. Don't watch the "
          "moonstone.",
        T="He won't tend it any more. The stone will dim or it won't, and either way I'll sleep better.\n\n"
          "The old stories never said what Tael was waiting for. I hope it wasn't us."),

    # ==== Eastern Tirisfal ===========================================================================================
    "etc_warriors": dict(
        giver="et_cave_deathguard", why="Calder over the cap; the Deathguard who holds the cave takes its patrols",
        D="The Boneward studies what's in the cave, and I keep it from walking out. The Scourge Warriors patrol the "
          "rib tunnels, and they don't sleep and they don't tire. They're terrible at hiding, though. You can hear "
          "them a corridor away.\n\n"
          "I've watched a pair of them walk the same rib for days without stopping.\n\n"
          "Break the patrols. I want a stretch of that corridor that stays empty for an hour, so Calder can set a lamp "
          "in it.",
        A="In the rib tunnels of the cave. You'll hear them before you see them.",
        T="That's an hour of empty corridor. Calder's already taking a lamp down to the next rib.\n\n"
          "It's the first ground anyone's held under that farm."),
    "etc_ghouls": dict(
        giver="et_cave_deathguard", why="Calder over the cap; the Deathguard who holds the cave takes its packs",
        D="It's the same tunnels and a faster problem. The Scourge Ghouls came down with the Scourge, and they stayed "
          "when it left, because the cult keeps a plague cellar down here and leaves things out for them.\n\n"
          "So they're fed, and a fed pack isn't the starving rabble you've met out on the glades. They're fast, they "
          "hunt properly, and they turn together.\n\n"
          "Thin them out, and don't let them get behind you in the ribs.",
        A="Through the ribs. They travel in packs and they turn together.",
        T="That's the pack cut down. The cellar can only grow it back so fast.\n\n"
          "The Boneward will want to talk to you about that cellar."),
    "etc_krag": dict(
        giver="et_cave_deathguard", why="Calder over the cap; the ghoulmaster goes with the ghouls",
        D="There's a pit west of the ribs, and Ghoulmaster Krag keeps his pack in it. He's lined it with bone, and he "
          "feeds the pack on what the cult leaves behind, which is how you get a pack that size this far from "
          "anything living.\n\n"
          "He doesn't fight at the front. He sends the pack and watches how it goes, and then he changes what he's "
          "doing. I've watched him do it, and I didn't enjoy it.\n\n"
          "Break the pack where it lives, and then kill Krag.",
        A="The bone-lined pit, west of the ribs. He sends the pack first and watches.",
        T="The pit's cold. Krag's what I'd have worried about most if we'd come back in a year.\n\n"
          "Without Krag, the rest of them are only hungry, and hungry I can handle."),

    # ==== The Sepulcher ==============================================================================================
    "sep_marrow": dict(
        giver="sepulcher_mortician_supplier", why="Yseult over the cap; the mortician makes his salts from marrow",
        D="I sell preserving salts, and I make the bone dust that goes in them. The best bone in this valley is on the "
          "Risen Husks out at Raven Hill Cemetery, and Yseult will tell you the same, because she buys from me.\n\n"
          "Fresh bone's too wet, and old grave-bone crumbles. The husks are dry all the way through, and the marrow "
          "keeps.\n\n"
          "Bring me dry marrow-bones off the Risen Husks. If it's damp in your hand, it's no use to me, so leave it "
          "where it is.",
        A="Off the Risen Husks at Raven Hill Cemetery, wherever the field is thickest.",
        T="They're dry and pale, every one of them. That's salt enough for the whole Sepulcher this winter.\n\n"
          "Yseult will want the long bones for her combs. I'll let her have them, if she asks nicely."),
    "spn_wl_larder": dict(
        giver="sepulcher_gravestone_reader", why="Corvane over the cap; the reader of the stones counts the dead",
        D="I read the names on the stones, because somebody should. Corvane's told me what he wants to know about the "
          "Widow's Lair, and he can't bring himself to go and find out, so I've said I'd ask for him.\n\n"
          "He wants to know how many people that hive has eaten, and he doesn't want a rough number. He's spent years "
          "telling families in these woods that their people were lost to wolves, or to the road, and he believed "
          "most of it when he said it.\n\n"
          "The answer's in two places, deep in the lair. The Larder is where they hang the fresh ones, and the Husk "
          "Pit, at the other end, is where they drop what's left. Stand in each long enough to count, and don't bring "
          "anything out.",
        A="The Larder and the Husk Pit, deep in the Widow's Lair. Count, and bring nothing out.",
        T="Then it's more than either of us wanted. I'll cut every one of them into a stone, even without names, and "
          "Corvane can write to the families.\n\n"
          "They'll hate him for it, and he says they'll be right to."),

    # ==== Brill ======================================================================================================
    "sm_the_flamekeepers_due": dict(
        giver="brill_innkeeper", why="Novak over the cap; he left the signet and his letter with the innkeeper",
        D="Renee keeps the inn where Novak lodges, and Novak's left Stane's signet with her for you, with a letter. He "
          "wants it put into Flamekeeper Rory Callahan's hand at the Bulwark, the Forsaken's wall at the end of "
          "Tirisfal's east road, where the Order keeps its quarter.\n\n"
          "The road there runs into country that kills people who aren't ready for it. Novak says to wait until you "
          "are, and then to go.",
        A="Take the east road out of Tirisfal to the Bulwark. The Order's banners are on the south side of the "
          "street, and Rory stands at the keep's door. Novak says don't go before you're ready, and he means it."),
})

TEXT.update({
    "sps_pyre_hall": dict(
        T="You heard a voice giving orders? There's nobody in that hall to give orders to, and there hasn't been "
          "since before the worgen. Either he's talking to the dead, or the dead are in there with him and "
          "listening.\n\n"
          "I scraped a phial of ash off those steps the night the doors were barred, and I gave it to Avery Lusk by "
          "the fire. He'll want you to carry it south."),
    "dk_verrick_fairbanks": dict(
        T="That's Fairbanks closed. I've carried his tally in my head for a week, and I'd started adding to it in my "
          "sleep.\n\n"
          "The crypt's vaults are still shut, though. Sexton Marrow wants our dead out of the ossuary, and he'll tell "
          "you about it. He's down at the graves."),
    "fen_isle_banshees": dict(
        T="Nothing answered last night. The drowned still sang, and I sat and listened to the whole of it, and it was "
          "just a sound in the dark, the way it was when I was a boy.\n\n"
          "Old Wenna's been asking after the banshees. She has a theory about them, and she'd like a word with you."),
    "sm_the_captain_of_the_doors": dict(
        T="That's the ring. I've seen it on his hand in a doorway with the fire behind him.\n\n"
          "Rory should hear it from the one who did it. I'm writing to him tonight, and I'll leave the letter and the "
          "ring with Renee downstairs. Collect them from her when you're ready for the road east."),
})
