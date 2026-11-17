"""
What every Plaguelands quest says, in the voice of the person giving it. Read by the four content modules
(tools/plaguelands_quests_<part>.py), whose Q() takes its words from here.

Kyle, 16 Nov 2026: "make a note to audit the actual quests in plaguelands. Right now they dont even talk to you...no
lore no talking....the people are read as total disconnected third character... All the plaguelands quests are like
this", and "We can look at the quest writing in Emerald Sanctuary to model the other stuff off of."

So the shape is Emerald Sanctuary's (data/quests/felwood.json, the es_ givers):

    desc    one plain line of what to do and where: the quest log's line, not a story about the giver
    accept  the giver talking to you, in the first person: who they are, why it matters to them, where to go and
            what to watch for. The lore lives here, in their mouth.
    done    the giver again, when you come back
    title   only where the old one no longer fits (the towns moved: Sorrow Hill is graves again)

The Stonetalon pass's rules still hold and tools/build_plaguelands_quests.py checks them: whole sentences,
contractions, no dashes, no counts beside an objective word, every kill target named. Who knows what (Kyle): every
transplant knows they came from Earth and the Order talks about it freely; the Forsaken call them newcomers; natives
never say Earth.
"""


def V(desc, accept, done, title=None):
    return dict(desc=desc, accept=accept, done=done, title=title)


VOICE = {}

# =============================================================================================== SOUTH WPL (51-54)
VOICE.update({
    # ---------------------------------------------------------------- High Executor Marla Venn, the Bulwark
    "pls_the_line_holds": V(
        "Kill Wandering Skeletons, and every Plague-Ridden Wolf you can find, in the fields east of the Bulwark.",
        "So you're the one who walked through my gate without being asked twice, which I like. I'm High Executor Marla Venn, "
        "and this wall is mine.\n\nThe Dark Lady gave me the Bulwark when there was nothing here but a ditch and a "
        "rumour. Everything east of it wants to come west, and none of it has. The Wandering Skeletons walk the King's "
        "Road at night as if they still had somewhere to be, and the Plague-Ridden Wolves run the grass on either "
        "side of them.\n\nGo out the east gate and thin them. Stay this side of the crossroads. I don't send people "
        "past it until I know they'll come back.",
        "The wall will sleep a little easier tonight, and so will I, if I slept.\n\nYou came back, which puts you "
        "ahead of most. I've got harder work further out, if you want it."),
    "pls_andorhals_gate": V(
        "Kill Andorhal Skeletons and Andorhal Skeletal Archers at the edge of Andorhal.",
        "Andorhal was a city when I was alive. I bought bread there. Now it's the Scourge's, right in the middle of "
        "the south, and its dead march out to the crossroads every night and come looking for my wall.\n\nThe "
        "Andorhal Skeletons hold what's left of its gate, and the Andorhal Skeletal Archers stand on the broken walls "
        "and shoot anything that comes close. My patrols can't see past them.\n\nTake the road south from the "
        "crossroads toward the lake. You'll know Andorhal by the smoke. Come at the archers from the side, because "
        "they're watching the road.",
        "My patrols can see into the city now, and what they see isn't pretty.\n\nI've got a harder job for you, if "
        "you've the stomach for it."),
    "pls_the_necromancers": V(
        "Kill Andorhal Necromancers in the ruins of Andorhal and bring back their Necromantic Foci.",
        "The skeletons don't get up on their own. Somebody stands in the ruins and keeps them on their feet, and "
        "that somebody is the Andorhal Necromancers.\n\nEach of them carries a focus, a bone rod wound with black "
        "wire, and the rod does most of the work. The Royal Apothecary Society would very much like to know how. I "
        "would very much like them to stop.\n\nThey keep to the middle of Andorhal, among the burned houses. Kill "
        "them and bring me the rods. Don't hold one any longer than you have to. You'll see why.",
        "They hum, don't they? I hate that.\n\nThe Society will take them apart. One more job and Andorhal's ours "
        "to watch."),
    "pls_the_magistrate": V(
        "Kill Magistrate Andor and the Andorhal Abominations that guard him in Andorhal.",
        "I served in Lordaeron's army before I died. The man who signed my commission was Andorhal's magistrate, and "
        "he's still there. He died with his city and got up again, and he sits in what's left of the town hall "
        "giving orders as if he'd never stopped.\n\nMagistrate Andor, they call him now. The Andorhal Abominations "
        "stand guard over him.\n\nHe isn't always in the hall, so kill the abominations while you wait. He's stronger than he looks, so bring friends. And I'd rather it was you than me, which is the closest I'll come "
        "to admitting anything today.",
        "Then he's at rest, and so is Andorhal, for a little while.\n\nHe signed my commission once. I'd rather not "
        "have watched him do it again."),
    "pls_a_dispatch_for_sorrow_hill": V(
        "Carry Venn's dispatch across the street to Flamekeeper Rory Callahan, in the Order's quarter of the Bulwark.",
        "Look across my street. Those banners are the Order of the Pale Flame. They used to keep a fort on Sorrow "
        "Hill, under the Crusade's nose, until the hill got too dead even for them. Now they're inside my wall.\n\n"
        "They wear what used to be Scarlet armour and they're led by newcomers. I don't like them. They also kill "
        "the mindless dead and leave my people alone, and a wall needs every friend it can get.\n\nTake this to "
        "their Flamekeeper, Rory Callahan. He stands at the keep's door on the south side. It's a short walk, so "
        "don't let him keep you talking.",
        "Marla Venn's seal. She writes like she's sharpening a knife.\n\nShe wants to know if we'll hold the road "
        "south of Andorhal. Tell her we will, and that the Order sends its regards, which she'll hate.",
        title="A Dispatch for the Flamekeeper"),

    # ---------------------------------------------------------------- Apothecary Dorian Vesk, the Bulwark
    "pls_felstone_field": V(
        "Kill Felstone Ghouls and Felstone Cultists round the cauldron on the Felstone farm.",
        "Apothecary Dorian Vesk. Don't touch anything on the bench.\n\nThe Scourge brews its plague in cauldrons out "
        "in the fields, and I want to know what's in them. The nearest is on the Felstone farm, north of the King's "
        "Road. The Felstone Cultists tend it, and the Felstone Ghouls who used to work that field stand round it "
        "like they're still waiting for the harvest.\n\nTurn north at the crossroads and go past the dead orchard. "
        "The cauldron's in the middle of the field. Clear the ghouls and the cultists, and leave the cauldron "
        "alone. I want it whole.",
        "That'll do nicely. The way in's open now.\n\nNow for the part I actually care about."),
    "pls_a_sample_from_felstone": V(
        "Kill the Felstone Cauldron Lord and take the Felstone Cauldron Sample it carries.",
        "A sample out of the cauldron itself is no good to me. The cultists add whatever's lying around. The clean "
        "stuff, the batch they started from, is in a flask on the belt of the thing that keeps the cauldron.\n\n"
        "It's a Felstone Cauldron Lord, one of the Scourge's stitched brutes. It's big and slow and it hits like a "
        "falling barn.\n\nIt stands at the Felstone cauldron. Put it down and bring me the flask. Keep it upright "
        "and keep it out of the sun.",
        "It's still warm, and that's wonderful.\n\nThere are more cauldrons in the south. I'd like them all."),
    "pls_dalsons_tears": V(
        "Kill Dalson's Ghouls at the Dalson farm and bring back a Dalson's Cauldron Sample from its Cauldron "
        "Necrolytes.",
        "The Dalson farm has its own cauldron, and I want to set its brew beside the Felstone one. If they're the "
        "same, the Scourge has a recipe. If they're not, it's experimenting, and that's worse.\n\nThe Cauldron "
        "Necrolytes who stir it carry flasks of the brew. Dalson's Ghouls work the yard round them.\n\nIt's north "
        "and a little east of Felstone, the farm with the big red barn. Leave the barn alone. I mean that. People "
        "go in there and don't come out, and I've only got one of you.",
        "Thicker than Felstone's. They're changing the recipe from farm to farm.\n\nThat's either very bad or very "
        "interesting. I'd like one more before I decide."),
    "pls_the_writhing_haunt": V(
        "Kill Haunt Cult Tenders at the Writhing Haunt and bring back a Writhing Haunt Sample.",
        "The last cauldron in the south is at the Writhing Haunt, east of Dalson's. The Haunt Cult Tenders keep it "
        "stirred, and the banshees keep everyone else away. I sent an apothecary there last month. He came back "
        "without his voice.\n\nI want a sample, and I want the tenders thinned so the next one of us who goes "
        "comes back talking.\n\nGo east along the north road until the ground goes soft and the trees die. The "
        "tenders carry flasks. The banshees will come when you start fighting, so pick your ground and don't stand "
        "in the open.",
        "Something's moving in this one. Look at that.\n\nI need someone who knows more about the walking dead than "
        "I do, and the only one I trust is on the other side of the sea."),
    "pls_what_the_plague_is_made_of": V(
        "Carry Vesk's sample case to Apothecary Merrow Vane at Sun Rock Retreat in Stonetalon.",
        "I studied under Apothecary Merrow Vane. She's at Sun Rock Retreat in Stonetalon now, watching the dead get "
        "up on the Mulgore side of the mountain with nobody calling them. Nobody stirring a cauldron, nobody "
        "chanting, they just get up.\n\nI think it's the same sickness as the cauldrons. I'd like to be wrong. "
        "Merrow will know.\n\nTake the zeppelin from Tirisfal to Orgrimmar and a wind rider to Sun Rock. She'll be "
        "the only Forsaken there. Keep the case upright, and don't let the tauren open it, however politely they "
        "ask.",
        "These are Dorian's samples, all right. He always did label everything twice.\n\nThis one, from the Haunt, "
        "moves the way the dead on the Rim move. I'll write to him tonight, and I'm afraid of what I'll be "
        "writing."),

    # ---------------------------------------------------------------- Deathstalker Ilsa Rook, the Bulwark
    "pls_cult_couriers": V(
        "Take Cult Courier's Letters from the Haunt Cult Tenders at the Writhing Haunt.",
        "Keep your voice down. I'm Rook, and I watch the Cult of the Damned for the Undercity.\n\nThe Cult writes "
        "letters. The Haunt Cult Tenders out at the Writhing Haunt carry them off to somebody, folded small enough "
        "to hide in a boot, and I'd very much like to know who's reading them.\n\nOnly some of the tenders carry "
        "one. Bring me what you find, and don't try to read them. The cipher's a nasty one, and the last person who "
        "puzzled over it too long started dreaming in it.",
        "Every letter's in a different hand, and the same name's in all of them.\n\nI'll need the Undercity to hear "
        "this."),
    "pls_a_report_for_the_undercity": V(
        "Carry Rook's report to Deathstalker Rhyne in the Undercity.",
        "The letters name somebody in the Undercity. Somebody who's been passing the Cult our patrol routes, the "
        "Bulwark's included.\n\nI won't trust the bats with this, and I won't trust a courier I haven't met. I've "
        "met you.\n\nGo out the west gate, back through Tirisfal and down into the Undercity. Deathstalker Rhyne is "
        "in the Royal Quarter. Put it in his hand and nobody else's, and don't stop for a drink on the way. Whoever "
        "that name belongs to drinks in the same places you would.",
        "So this is Rook's report. She writes like she's afraid of running out of ink.\n\nThis name's going to make "
        "some people very unhappy. Thank you. I'll handle it from here."),
    "pls_the_mother_of_the_haunt": V(
        "Kill the Mother of the Haunt and the Haunt Banshees at the Writhing Haunt.",
        "The banshees at the Writhing Haunt answer to something. I call her the Mother of the Haunt. She's old "
        "enough to remember the farm before the plague, and she keeps the Haunt Banshees, and the banshees keep the "
        "Cult's tenders safe.\n\nWhile she's there, nobody gets near that cauldron without losing their voice. I "
        "want her silenced.\n\nShe drifts through the Haunt and she isn't always there. Thin the banshees while you "
        "wait for her. When she wails, back off and let it pass. You'll know it when you hear it.",
        "That's one less voice in the Haunt.\n\nI can hear the wind out there now, and I'd forgotten what it sounded "
        "like."),

    # ---------------------------------------------------------------- Deathguard Captain Ludo Vance, the Bulwark
    "pls_farmer_felstone": V(
        "Kill Farmer Felstone and the Felstone Ghouls who work his field.",
        "I'm Captain Vance, and I run the patrols between here and Andorhal, for what that's worth these days.\n\nThe man "
        "who owned Felstone Field still walks it. He was stubborn alive, they tell me, and he's worse dead. My "
        "patrols cut across his field to save an hour, and he's had three of them with a rusted scythe.\n\nThey call him Farmer Felstone. Put him in the ground he wouldn't leave, and his Felstone Ghouls with him. Felstone Field's north "
        "of the crossroads. Look for the one with the scythe, and bring somebody, because he's tougher than his "
        "hands.",
        "Then the field's quiet, for once.\n\nI'd have bought grain off him, once. I suppose that's the "
        "Plaguelands for you."),
    "pls_the_ghost_in_the_barn": V(
        "Kill the Dalson Ghost in the Dalson barn and the Dalson's Skeletons in its yard.",
        "Nobody goes into the Dalson barn. I lost a patrol in there. The one who came out said it was the father, "
        "Joseph Dalson, still looking for his family. He said it wasn't angry, it was looking, and it killed them "
        "anyway.\n\nThe Dalson Ghost keeps the barn and Dalson's Skeletons keep the yard. I want it ended, and I'd "
        "like it ended gently, if there's a gentle way.\n\nIt's the red barn on the Dalson farm. The skeletons walk "
        "the yard. The ghost won't come out, so you'll have to go in.",
        "He's at rest, then. I hope he found them.\n\nSome things out here make you remember you were alive once. "
        "That was one of them."),

    # ---------------------------------------------------------------- Surgeon Halbert Grey, the Bulwark
    "pls_snapjaw_shell": V(
        "Take Snapjaw Shell Plates from the Darrowmere Snapjaws at Darrowmere Lake.",
        "I'm Surgeon Grey. Mind the bucket.\n\nWhen the fields take a leg off one of the Deathguard, I put it back, and "
        "I brace the break with turtle shell. It's hard as iron and it doesn't rot, which is more than I can say "
        "for anything else out here. The best shell in the Plaguelands is on the Darrowmere Snapjaws at the "
        "lake.\n\nThey sun themselves on the shore south of the old Sorrow Hill road. Go for the legs, because "
        "you won't cut through the shell. That's the whole point of it. Bring me plates, and the bigger the "
        "better.",
        "Look at the grain on that. That'll hold a femur together for a hundred years.\n\nThere's an old one at the "
        "lake I've wanted for a long time."),
    "pls_old_darrowjaw": V(
        "Kill Old Darrowjaw and the Darrowmere Snapjaws round him at Darrowmere Lake.",
        "The oldest snapjaw in Darrowmere Lake has a name. Old Darrowjaw's been in that water since before the "
        "plague, and his shell would brace a wall, never mind a leg. I've wanted it for years.\n\nHe's a big "
        "turtle and a very bad-tempered one, and the Darrowmere Snapjaws keep close to him.\n\nHe keeps to the deep "
        "end and comes up when he likes. Thin the young ones while you wait. When he pulls you under, fight your "
        "way back to the shore and don't panic. Panicking is how I get most of my patients.",
        "Now that's a shell, a real one.\n\nI'll have the whole Deathguard braced by spring. The newcomers across the "
        "street keep asking me how we stay on our feet, and now I'll have something to show them."),

    # ---------------------------------------------------------------- Flamekeeper Rory Callahan, the Order's keep
    "pls_what_we_kill": V(
        "Kill Scarlet Outriders and Scarlet Field Chaplains on the north side of Andorhal.",
        "I'm Rory Callahan. Before you wear our flame, you need to know the one rule, so here it is. We kill the "
        "mindless dead and the fanatics who burn people, and nobody else.\n\nI wore the red for a year. When the world "
        "ended the Crusade were the only ones killing what was killing us, and I joined them. Then I saw who else "
        "they were burning, people like me, for the crime of being born on Earth. I scraped the red off and walked "
        "out, and some good people walked out with me.\n\nThe Scarlet Outriders and the Scarlet Field Chaplains "
        "patrol the north side of Andorhal now. That's who we kill. Don't touch the Forsaken. They're rude, and "
        "they're not mindless.",
        "That's the work, and some days I can live with it.\n\nI laid steel in Boston for twenty years. I'd still "
        "rather be doing that."),
    "pls_red_on_the_road": V(
        "Take a set of Scarlet Patrol Orders from a Scarlet Field Chaplain in Andorhal.",
        "The Crusade doesn't send chaplains this far south unless it's planning something. The Scarlet Field "
        "Chaplains in Andorhal carry their orders from Hearthglen, and I want to read them.\n\nBring me a set with "
        "the seal unbroken. I want to know whose seal is on them before I see what it says. I know most of the hands in "
        "Hearthglen. I used to take orders from them.\n\nThe chaplains work the north side of Andorhal and keep "
        "their orders in a satchel. Don't open it.",
        "That's Hearthglen's seal, and it's signed by Victor Hale himself.\n\nHe was a security contractor back "
        "home. I served beside him, God help me. If he's sending orders this far south, the Pale Watch needs to "
        "know."),
    "pls_hearthglens_road": V(
        "Carry the Crusade's orders to Watch Captain Lena Fischer at the Pale Watch, off the King's Road in North "
        "WPL.",
        "These orders say the Crusade's moving more patrols down the road from Hearthglen. We keep a town on that "
        "road. The Pale Watch, under Watch Captain Lena Fischer. It's close enough to Hearthglen that they can see "
        "each other's fires.\n\nI want this in Lena's hands before Hale's patrols are on her doorstep.\n\nGo out the "
        "east gate and north up the King's Road, through the gate at the top of the fields, and keep on toward "
        "Hearthglen. The Pale Watch's gate is off the road where it starts to climb. Lena will be the one shouting.",
        "That's Hale's seal, of course it is.\n\nI was a police officer in Hamburg, back home, and I know what a man "
        "looks like when he's getting ready to do something terrible. Stay a while. I could use you up here."),
    "pls_the_groundskeeper": V(
        "Kill the Groundskeeper and the Caer Darrow Ghouls on Caer Darrow.",
        "Across Darrowmere Lake there's an island, Caer Darrow, and Scholomance lies under it. The Cult teaches "
        "necromancy there to anyone who asks, and plenty ask.\n\nI want eyes on that island. Right now the "
        "Groundskeeper keeps it, a dead man with a spade, and the Caer Darrow Ghouls dig wherever he points.\n\n"
        "Caer Darrow's in the east of the lake. Cross the causeway. He walks the grounds and the ghouls dig for him, "
        "and he's strong, so take friends. When he's gone, the Order can sit on Scholomance's doorstep and watch who "
        "goes in.",
        "Then the island's watched, and the Cult knows it.\n\nScholomance can wait. We'll be ready for it when it's "
        "time."),

    # ---------------------------------------------------------------- Drillmaster Kofi Mensah, the Order's yard
    "pls_steel_for_sorrow_hill": V(
        "Take Rusted Andorhal Blades from the Andorhal Skeletons in Andorhal.",
        "I'm Kofi Mensah. I train the recruits, the ones who walked out of the Crusade and the ones who came through with nothing, and the recruits keep breaking their swords.\n\nThe Andorhal Skeletons "
        "carry the old Lordaeron infantry's blades. Rory says the steel under the rust is better than anything we "
        "can buy, and Rory knows steel. I'd rather my people swung a dead man's good sword than a live man's bad "
        "one.\n\nThe skeletons are all over Andorhal and most still carry a blade. Don't clean them. Bring them "
        "back rusted and Rory will make them good again.",
        "That's a month of drills that won't end with somebody holding half a sword.\n\nI taught PE in Kumasi, back "
        "home. This is the same job, mostly, with more swords.",
        title="Steel for the Order"),
    "pls_archers_on_the_wall": V(
        "Kill Andorhal Skeletal Archers on Andorhal's walls.",
        "I take the recruits into Andorhal to learn. It's the best classroom in the Plaguelands, and the worst. The "
        "Andorhal Skeletal Archers on the broken walls keep putting arrows into my students, and half of those students came through in the Integration and had never seen a bow before last spring.\n\nClear the walls "
        "before the next lesson. Close the distance fast, because they won't. When you're done, I'll bring the "
        "recruits and they can learn from somebody who isn't shooting at them.",
        "They came back with no arrows in them today. That's a first.\n\nThere's something bigger in the city, and "
        "I'd like it gone too."),
    "pls_the_abominations": V(
        "Kill Andorhal Abominations in Andorhal and cut out their Abomination Stitching.",
        "The Andorhal Abominations are the Scourge's stitched brutes, sewn together from whatever was lying "
        "around. My recruits see one and forget everything I've taught them.\n\nI want them dead, and I want their "
        "stitching. The thread that holds them together is tougher than wire, and our armourers can use it to bind "
        "plate.\n\nThey lumber round the middle of Andorhal. They're slow and they hit like a cart. Cut the thread "
        "out afterward, and wash your hands before you eat. Priya will check.",
        "That's some ugly thread. Thank you, I think.\n\nThe recruits can do the rest of Andorhal. You've earned a "
        "rest."),
    "pls_shades_of_caer_darrow": V(
        "Destroy the Caer Darrow Shades on Caer Darrow and the water round it.",
        "When Rory sent scouts toward Caer Darrow, the Caer Darrow Shades came off the island and over the water "
        "after them. I lost a recruit that night, a girl called Teodora. She was nineteen.\n\nI'd like them destroyed. I won't "
        "pretend it's for the Order.\n\nThe shades drift on the island in the east of the lake and on the water "
        "round it. They're cold to the touch, so wrap up warm, and don't let them get behind you.",
        "That's for Teodora. She'd only been here since the Integration, and she was braver than I was at her "
        "age.\n\nThank you. I'll tell the recruits who did it."),

    # ---------------------------------------------------------------- Chaplain Odile Marchand, the Order's chapel
    "pls_uthers_rest": V(
        "Visit Uther's Tomb, south of the old Sorrow Hill road in South WPL.",
        "I'm Odile Marchand. I keep the Order's chapel, and before that I kept Uther's Tomb.\n\nWe built our fort on "
        "Sorrow Hill because of the tomb. The Lightbringer is buried there. When the hill got too dead to hold, we "
        "came here, but the tomb didn't come with us, and somebody has to remember it.\n\nGo and stand at it before "
        "you do anything else for the Order. Take the road south from the crossroads, past the graves on the hill. "
        "The tomb's at the foot of the hill, with the statue. It's still the quietest place in the Plaguelands, and "
        "I think it's the only one.",
        "It's quiet there, isn't it? Even the dead keep away.\n\nI taught history in Lyon, back on Earth. I never "
        "thought I'd be keeping a legend's grave."),
    "pls_laid_to_rest": V(
        "Kill Dalson's Ghouls and Dalson's Skeletons on the Dalson farm.",
        "The Dalsons' farmhands never got a burial. They got up instead, and now Dalson's Ghouls and Dalson's "
        "Skeletons work that farm for the Scourge.\n\nI'd like them put down. And I'd like you to say a word for "
        "each of them, if you can manage it. It doesn't have to be a prayer. It doesn't have to be in any language "
        "they'd know.\n\nThe Dalson farm's north of the road, with the red barn. The ghouls work the yard and the "
        "skeletons walk the fields. Say whatever you like over them. It's the saying that matters.",
        "Thank you. I've added their names to the chapel's book, the ones we know.\n\nThere's somewhere worse than "
        "Dalson's, and I'd like you to see it."),
    "pls_the_haunts_banshees": V(
        "Kill Haunt Banshees and Writhing Crypt Fiends at the Writhing Haunt.",
        "On still nights on Sorrow Hill I could hear the Writhing Haunt. I can't hear it from here, behind the "
        "wall, and I'm ashamed of how glad I am.\n\nThe Haunt Banshees wail over that farm, and the Writhing Crypt "
        "Fiends dig under it. The sound gets into the stones, and into the people who live near them.\n\nIt's east "
        "of Dalson's, where the trees die. The banshees drift and the fiends come up out of the ground. Cover your "
        "ears if it helps. I want it quiet.",
        "Somebody rode in from the east today and said they could hear the wind out there.\n\nThank you. Rest here, "
        "if you like. The chapel's warm."),
    "pls_darrowmeres_drowned": V(
        "Kill Drowned Lakewalkers on the shores of Darrowmere Lake.",
        "I used to walk down to Darrowmere Lake in the evenings, and the Drowned Lakewalkers walked up out of it to "
        "meet me. They're the people of Caer Darrow, I think. They went into the water when the plague crossed the "
        "lake and they never came out.\n\nI'd like them laid to rest, and I'd like the shore safe for the Order's "
        "scouts.\n\nGo south and east, past the tomb to the lake. They come out of the shallows. Stay on the shore if "
        "you can, because they're stronger in the water.",
        "I'll say their names tonight, the ones Ser Aldren remembers.\n\nWe had a lake at home too, Lac d'Annecy. I "
        "swam in it every summer. I don't think I'll swim in this one."),

    # ---------------------------------------------------------------- Priya Raman, the Order's kitchen
    "pls_bear_stew": V(
        "Take Plague-Free Bear Flanks from the Diseased Black Bears along the King's Road.",
        "I'm Priya, and I cook for the Order, and the Order's eaten the last of the meat.\n\nThe Diseased Black Bears out "
        "there are sick, but not all the way through. I've found that a cut from the back of the leg comes out "
        "clean, if you're careful and you're quick. It's not the worst thing I've cooked here. It's not even the "
        "worst thing I've cooked this week.\n\nThe bears keep to the trees along the King's Road, east of the gate. "
        "Cut from the back of the leg, where it's still red. If it's grey, leave it.",
        "Oh, that's lovely, that's dinner for a week.\n\nI ran a guesthouse in Kochi, and my mother's curry was the "
        "reason people came back. It works on bear, it turns out. She'd laugh herself silly."),
    "pls_letters_home": V(
        "Carry the bundle of letters to Dr. Hannah Lindqvist at Sun Rock Retreat in Stonetalon.",
        "Nobody knows where anybody ended up after the Integration. We write letters anyway. Half of them are "
        "addressed to a name and a guess.\n\nI keep the Order's bundle. There's a geologist at Sun Rock Retreat in "
        "Stonetalon, Dr. Hannah Lindqvist, who keeps a list of every name she's heard from Kalimdor's camps. If "
        "anyone's going to match a letter to a person, it's her.\n\nGo back through Tirisfal, take the zeppelin to "
        "Orgrimmar and a wind rider to Sun Rock. Hannah's the one with the maps of the volcano. Please don't lose "
        "any of them. Some of them took people a month to write.",
        "So many of them. Let me see whose names I've got.\n\nThere's one here for a woman in Ratchet I wrote down "
        "last month. I'll make sure this gets to her. That's one, at least."),

    # ---------------------------------------------------------------- Anders Holm, the Order's hawks
    "pls_clear_skies": V(
        "Kill Plaguewing Vultures over South WPL's fields.",
        "I'm Anders, and these are the Order's hawks. They carry our letters now that we've given up flying people.\n\nThe "
        "Plaguewing Vultures have started going after them in the air. I've lost two birds this week, and one of "
        "them was carrying a letter I'd rather the Crusade didn't read.\n\nThe vultures circle over everything "
        "dead, which out here is most of the map. Shoot them down if you can. Don't let them settle anywhere near "
        "the wall.",
        "That's much better, and my birds will fly tomorrow.\n\nI kept pigeons in Bergen when I was a boy, back on "
        "Earth. Hawks are harder, and they're worth it."),
    "pls_jesses_for_the_hawks": V(
        "Take Clean Wolf Sinew from the Plague-Ridden Wolves in the fields.",
        "I tie the hawks with jesses, leather straps on their legs, and the plague rots leather in a week. Sinew "
        "doesn't rot the way leather does.\n\nThe Plague-Ridden Wolves in the fields carry good sinew under the "
        "rot, if you cut carefully. Not every wolf will have any worth taking.\n\nThey run the grass either side of "
        "the King's Road. Cut from the back legs, where the plague's slowest. Bring me enough to rig every bird I "
        "have.",
        "That's good sinew, and that's every bird tied properly.\n\nWe used gut string for the pigeons when I was a "
        "boy. It turns out it's the same knot."),

    # ---------------------------------------------------------------- Scout Agata Wrobel, the Order's stable
    "pls_eyes_on_andorhal": V(
        "Look over the middle of Andorhal and report back to Agata.",
        "I'm Agata Wrobel. I'm back on my feet after a week in a cell under the Scarlet Monastery, and I want to work. "
        "Rory says not alone yet, so you can be my eyes.\n\nRory wants to know where the Crusade's patrols cross "
        "the Scourge's in Andorhal. I want you to walk into the middle of the city, by the old town hall, and look "
        "round. Count the red and count the dead. Then get out.\n\nAndorhal's south of the crossroads. Don't stop to "
        "fight anything you don't have to. The point is to come back.",
        "So it's red to the north and dead to the south, and they meet in the square. That's useful to know.\n\nI "
        "was a mountain guide in the Tatras, back home. Getting people in and out of places is the only thing I was "
        "ever good at."),
    "pls_the_survey_map": V(
        "Take the Andorhal Survey Map from a Scarlet Outrider in Andorhal.",
        "The Crusade's Scarlet Outriders carry a surveyor's map of Andorhal. One of the guards at the Monastery "
        "bragged about it while I was in the cell, so I know it's real. Every Scourge strong point is on it, and "
        "every Forsaken one too.\n\nIf the Crusade knows where everyone is, so should we.\n\nThe outriders patrol "
        "the north side of Andorhal. One of them carries it rolled in a leather tube. Bring it back dry, and don't "
        "let them burn it. They burn things when they're losing.",
        "Look at this. They've marked the Bulwark's patrols to the hour.\n\nRory needs to see this, and then Venn "
        "does, whether she likes us or not."),
    "pls_under_the_haunt": V(
        "Kill Writhing Burrowers and Brood Guardians in the Writhing Deep, under the Writhing Haunt.",
        "I've been watching the Writhing Haunt for the Order. There's a hole behind it the crypt fiends keep "
        "crawling in and out of. I went down far enough to know it doesn't stop.\n\nIt's a web of tunnels, and they "
        "all lead back to the middle. The Writhing Burrowers come up out of the floor and the Brood Guardians stand "
        "over the passages like they're guarding a nursery, which I think they are.\n\nThe cave mouth is behind the "
        "Haunt, east of the road. Thin them out so we can see what's at the bottom, and keep your back to a wall.",
        "That's the outer burrows quiet, then.\n\nI used to take tourists down caves in the Tatras, and not one of "
        "them ever tried to eat me. There's a chamber in the middle that everything was guarding, and I think we "
        "both know what's in it."),
    "pls_the_broodlord": V(
        "Kill Broodlord Szarak and the Silken Bride in the Writhing Deep.",
        "In the middle of the Writhing Deep, where every tunnel meets, Broodlord Szarak sits on the brood. Off the "
        "north rim there's a pocket of web I won't go near, and something lives in it the fiends call The Silken "
        "Bride.\n\nI want them both dead before the brood hatches. If that nest opens, the Haunt will be the least "
        "of anyone's problems.\n\nThe broodlord's in the chamber in the middle. The bride's up in the north-east, "
        "at the end of a tunnel off the outer ring. Bring something for poison, because she bites and it doesn't "
        "wear off.",
        "Then that's the brood finished, and the Haunt's lost its nursery.\n\nI've been in a cell and I've been in "
        "a web now. I'm not sure which I liked less. Here, take this. You've earned it."),

    # ---------------------------------------------------------------- Ser Aldren Holt, the Order's keep
    "pls_the_fallen_of_andorhal": V(
        "Take Andorhal Company Rings from the Andorhal Skeletons in the west of Andorhal.",
        "Ser Aldren Holt. I held Andorhal for the King, and then I held it for the Crusade, and I walked out of "
        "both.\n\nWhen the plague came, my company held the west end of the city. My men are the Andorhal Skeletons "
        "now. Some of them still wear the company's iron rings.\n\nI'd like the rings back. I can't bury the men, so "
        "I'll bury those by Uther's Tomb. Not all of them will still have one. Bring me what you find, and forgive "
        "me for asking. I don't ask lightly.",
        "That's Corporal Brask's, and that's Hask's, and this one was little Tom Barrow's. He lied about his "
        "age.\n\nI'll bury them by the tomb in the morning. Thank you. I mean that more than you know."),
    "pls_the_necrolytes": V(
        "Kill Cauldron Necrolytes at the Dalson farm.",
        "I buried my company's rings by the tomb, and then I asked who raised my men in the first place. The "
        "answer's the Cauldron Necrolytes at the Dalson farm. They learned their trade in Andorhal, on my "
        "people.\n\nI want them dead. I won't dress it up, because it's personal.\n\nThey stir the cauldron in the Dalson "
        "yard, north of the road. They'll raise anything that falls near them, so draw them away from the ghouls "
        "before you start.",
        "That's some justice, at least. Not much, but some.\n\nThe Crusade told me this would feel like holiness. "
        "It feels like tidying up."),

    # ---------------------------------------------------------------- in from outside
    "pls_samples_for_the_bulwark": V(
        "Carry Marwen's reagent case to Apothecary Dorian Vesk at the Bulwark, on the road east from Tirisfal.",
        "I've read every report the Bulwark's sent back to the Undercity, and I don't believe half of them. Dorian "
        "Vesk says the plague in the western fields has changed. Dorian has said a great many things.\n\nSo I've "
        "packed him a case of clean reagents, enough for every test he'll need, and if he's right, he can prove "
        "it.\n\nGo up through the Ruins and east across Tirisfal to the wall at the end of the road. That's the "
        "Bulwark. He keeps the vats by the east gate. Don't open the case. I've counted every vial, and I'll know.",
        "Marwen's actually sent me clean reagents, and I didn't think she had any.\n\nShe thinks I'm wrong about the "
        "plague. She'll read my next report a lot more carefully once these tell her I'm right. Stay a while, "
        "because the fields need hands more than I need a courier."),
    "pls_hands_for_sorrow_hill": V(
        "Carry the Order's notice to Drillmaster Kofi Mensah in the Order's quarter of the Bulwark.",
        "You look like you can swing something heavy, which is what I need. I've a notice to send on, and I've been crying it twice "
        "a day for a month.\n\nThe Order of the Pale Flame wants fighters. They're camped inside the Bulwark now, at "
        "the end of the road east, and they don't care where anyone was born. I don't know much about them, and "
        "the Deathguard say less, but they pay and they feed you.\n\nTake this to their drillmaster, Kofi Mensah. "
        "Go east through Tirisfal to the wall. Their banners are on the south side of the street, and Kofi will be "
        "in the yard shouting at somebody.",
        "So Wexley sent you with the notice. He cries it twice a day in Brill, and nobody's told him to stop "
        "yet.\n\nI'm glad you came. Half my recruits walked out of the Crusade and the other half walked in off the "
        "road, so you'll fit in whatever you are. Go and see Rory when you've found a bunk.",
        title="Hands for the Order"),
    "pls_a_chaplains_letter": V(
        "Carry Chaplain Blackwood's letter to Chaplain Odile Marchand at the Order's chapel in the Bulwark.",
        "I still pray in Tarren Mill, most days to an empty chapel. I've heard there's another chaplain who still "
        "prays, a woman called Odile Marchand who kept Uther's Tomb for the Order of the Pale Flame.\n\nI've written her a "
        "letter. I've never met her, and I think that's the best reason to write.\n\nThe road north is shut, so go "
        "round through Tirisfal and east to the Bulwark. The Order keeps a chapel inside the wall, on the south "
        "side. I'd take it myself, but somebody's got to keep this door open.",
        "A letter from Tarren Mill, from a chaplain I've never met.\n\nHe asks whether I'm afraid the Light will "
        "stop answering. I'm not, and I'm going to write back and tell him so properly. Thank you for carrying it "
        "all this way."),
})

# =============================================================================================== NORTH WPL (53-56)
VOICE.update({
    # ---------------------------------------------------------------- Watch Captain Lena Fischer, the Pale Watch
    "pln_the_gate_of_hearthglen": V(
        "Walk up the King's Road and look at Hearthglen's gate, without starting a fight.",
        "I'm Lena Fischer, and I keep the Pale Watch. Welcome to the last town before Hearthglen.\n\nBefore I send "
        "anybody up that road, I want them to have seen it with their own eyes. People hear 'the Crusade' and think "
        "of a few zealots with torches. Go and look at the walls, and the towers, and the people on them.\n\nOut the "
        "gate and straight up the King's Road. You'll see the gate long before you reach it. Don't draw steel, and "
        "don't let them get a good look at your face. Then come back down and tell me what you saw.",
        "So now you've seen it. Walls, towers, and a lot of people who'd like to burn you.\n\nI was a police officer "
        "in Hamburg, back home. I've raided worse places, but never with a sword."),
    "pln_sentries_on_the_road": V(
        "Kill Scarlet Sentries on the road and in the fields below Hearthglen.",
        "Every Scarlet Sentry on the road below Hearthglen turns back anyone who isn't wearing red. That was "
        "fine while they stayed up there. Lately they've been coming down at night, closer every time, and last "
        "night one of them was close enough to read our gate.\n\nPush them back up the hill. They stand in pairs on "
        "the road and in the fields under the gate. They'll call for help if they can, so don't let one run. Keep "
        "it quick and keep it quiet.",
        "That'll keep them on their own side of the hill for a while.\n\nHale used to be a security contractor, back "
        "on Earth. He knows what an open flank looks like, and so do I."),
    "pln_crossbows_on_the_wall": V(
        "Kill the Scarlet Crossbowmen hiding in the hedges and ditches below Hearthglen.",
        "Hearthglen's answered us. With the sentries gone, they've put a Scarlet Crossbowman in every hedge along the "
        "road. One of Mateo's scouts took a bolt yesterday from a hedgerow he'd walked past a hundred times.\n\nI "
        "want them out of the fields. They hide in the hedges and the ditches below the walls. A crossbow takes a "
        "while to wind and they know you know it, so close the distance fast and don't stand still in the open.",
        "Mateo's scout is going to live, and the fields are ours to walk again.\n\nI've got something for Rory, if "
        "you're heading south."),
    "pln_word_from_the_watch": V(
        "Carry Lena's report to Flamekeeper Rory Callahan in the Order's quarter of the Bulwark.",
        "I've watched Hearthglen's gate for a month, and I've written down everything I've seen. Hale is pulling "
        "his people in behind the walls. Patrols, wagons, the lumber crews from Northridge. I don't think he's "
        "planning to sit behind those walls. I think he's getting ready to come out of them.\n\nRory needs this. "
        "He's at the Bulwark now, at the keep in the Order's quarter on the south side of the street. Fly if you "
        "can, the roostkeeper's by the south wall. Give it to Rory and wait while he reads it, because he'll have "
        "an answer.",
        "Lena's report, in her lovely tidy hand. She writes like she's filling out a form.\n\nHale's getting ready "
        "to march. I knew he would. Tell Lena to hold the Watch, and that I'm coming north."),
    "pln_a_letter_for_brill": V(
        "Carry Lena's letter to Flamewarden Teodor Novak in Brill.",
        "The Order keeps a man in Brill. Flamewarden Teodor Novak watches the Scarlet Monastery from a window over "
        "the inn, and he's very good at it.\n\nIf Hale marches out of Hearthglen, the Monastery marches with him. "
        "Teodor needs to know what I know, and he needs to know it from me.\n\nGo south to the Bulwark and out its "
        "west gate into Tirisfal, then on to Brill. Teodor lodges over the inn. He'll offer you a drink, and you "
        "should take it. It's the only good beer in Tirisfal.",
        "Lena's writing to me? Then it's bad.\n\nI was a firefighter in Brno, back home, and I know what it looks "
        "like when two fires are about to join up. Tell her I'll keep my eyes on the Monastery."),

    # ---------------------------------------------------------------- Scout Mateo Brandt, the Pale Watch
    "pln_worgs_on_the_road": V(
        "Kill Rotting Worgs on the roads round the Pale Watch.",
        "I'm Mateo, and I keep the Watch's roads open, and the Rotting Worgs have worked out that the road is where "
        "the food walks.\n\nThey run in packs and they don't let go once they've got you. I've had two runners "
        "come in with half a leg each this week.\n\nThey work the roads south and west of the gate, mostly at "
        "dusk. Break the packs up. Don't fight more than two at once, and keep moving, because they go for your "
        "legs.",
        "That's a road I can walk at dusk again.\n\nI taught kids to ride horses outside Rosario, back home. Out here "
        "the horses are dead and the dogs want to eat me."),
    "pln_skeletal_wanderers": V(
        "Kill Skeletal Wanderers on the roads of North WPL.",
        "The Skeletal Wanderers walk the roads with nowhere to go. I think they were travellers once, caught on "
        "the road when the plague came, and they've just kept walking ever since.\n\nThey're slow, but there are a "
        "lot of them, and they never stop. When they see you they turn round and follow, all of them, until you're "
        "backed against something.\n\nThey gather on the roads. Clear them off, and don't let them pin you against "
        "a wall.",
        "Thank you. I hated watching them walk.\n\nThey were going somewhere, once. I suppose we all were."),
    "pln_down_to_the_river": V(
        "Find a safe way down to the Thondroril's bank, east of the Pale Watch.",
        "We haul every barrel of water up from the Thondroril, the river on the east side of the fields, and it's "
        "a long way round to the only path we trust.\n\nI'd like a shorter one. Somewhere on the bank the dead "
        "don't use, where we can put a barrel at the bottom and a marker at the top.\n\nGo east from the gate, "
        "through the fields and down to the river. Find somewhere quiet and stand on it. You'll know it when you "
        "see it, because nothing will be trying to eat you.",
        "That's a good path. We'll put a marker on it and a barrel at the bottom.\n\nOona's down there most days, "
        "fishing. Say hello if you see her."),
    "pln_the_blighted_herd": V(
        "Kill Blighted Stags in the fields north and east of the Pale Watch.",
        "There's a herd of Blighted Stags in the fields north of the Watch. Most days they graze. When something "
        "spooks them they run, and they run straight at our walls, and twice now they've come through the gate "
        "before we could shut it.\n\nI'd like the herd thinned before the third time. They graze in the fields "
        "north and east of the town. Don't stand in front of them when they bolt. Pick off the ones on the edge of "
        "the herd and let the rest run.",
        "Our gate's still on its hinges this morning, which is a first this week.\n\nTake one of these. It's the "
        "least I can do."),
    "pln_travellers_keepsakes": V(
        "Take Traveller's Keepsakes from the Skeletal Wanderers on the roads.",
        "I can't stop thinking about the Skeletal Wanderers. If they were travellers, they had pockets, and some of "
        "them still have whatever was in them. A ring, a letter, a toy for somebody waiting at home.\n\nI'd like to "
        "write down what they were. Somebody might still be waiting for one of them, and the Order keeps a book of "
        "names at the Bulwark.\n\nThey walk the roads all round the Watch. Not every one of them has anything left. "
        "Bring me what you find and I'll write it all down.",
        "A pipe, a thimble, a child's wooden horse. Every one of these belonged to somebody.\n\nOdile at the Bulwark "
        "will want these for her book. I'll send them south."),

    # ---------------------------------------------------------------- Field Medic Noah Kowal, the Pale Watch
    "pln_riverbank_ghouls": V(
        "Kill Riverbank Ghouls in the reeds along the Thondroril.",
        "I'm Noah, and I patch up whoever makes it back through the gate. Lately that's been people who went down "
        "to the river.\n\nThe Riverbank Ghouls hide in the reeds along the Thondroril and drag people into the "
        "water. The ones who come back have bites I can't keep clean.\n\nThey lie on the banks east of the town and "
        "come at you out of the water. Stay on the high ground and let them climb to you.",
        "Nobody came in from the river with bites today. That's a good day.\n\nI was a nurse in Winnipeg, back "
        "home, and I've never been happier to have nothing to do."),
    "pln_sludge_samples": V(
        "Collect Cauldron Sludge Samples from the Cauldron Sludges at Gahrron's Withering.",
        "There's a cauldron at Gahrron's Withering, east of here. The Cauldron Sludge that crawls out of that cauldron is the plague at its purest, near enough, and that's exactly what I want.\n\nI think I can make a serum. "
        "Not a cure, nothing that good, but something that slows the sickness long enough to get somebody to a "
        "priest. I need to start with the real thing.\n\nThe sludges crawl round the cauldron at the Withering. Kill "
        "one and scoop what's left into a jar. Keep the lid on tight and don't breathe it in.",
        "This is horrible. Thank you.\n\nIf I can make something from this that stops the sickness, every medic on "
        "both sides of the sea will want it."),
    "pln_the_withering": V(
        "Kill Withering Ghouls and Withering Cultists at the cauldron in Gahrron's Withering.",
        "The cauldron at Gahrron's Withering is the Cult's. The Withering Cultists stir it, and the Withering Ghouls "
        "carry the plague out to the fields in buckets, like they're watering a crop.\n\nI want that cauldron "
        "left with nobody to stir it.\n\nIt's east of the Watch, past the dead orchard. The cultists stand at the "
        "cauldron and the ghouls work round it. Kill the cultists first. They'll heal the rest, and I'd rather not "
        "be patching you up afterward.",
        "The cauldron's cold. That's one less in the Plaguelands.\n\nThere's someone in charge out there, though, and "
        "he isn't going to stay dead on his own."),
    "pln_gahrron_the_withered": V(
        "Kill Gahrron the Withered at his farm.",
        "Gahrron owned the farm the Withering is named for. He died there, and the Cult raised him to guard their "
        "cauldron, and now Gahrron the Withered walks his own fields thinking they're still his.\n\nI'd like him "
        "put to rest, so we can burn the place clean. It won't heal while he's walking it.\n\nHe's near the "
        "cauldron. He's slow, but he's strong, and the sickness comes off him in waves. Take friends, and take "
        "something for the nausea. I'll have more of it here when you get back.",
        "Then the Withering's done. We'll burn it in the morning.\n\nHe was a farmer. I keep thinking about that. He "
        "just wanted to keep his farm."),
    "pln_a_serum_for_felwood": V(
        "Carry Noah's Serum to Dr. Nkechi Adeyemi at the Emerald Sanctuary in Felwood.",
        "I made it. It doesn't cure anything, I want to be honest about that, but it slows the plague down long "
        "enough to matter.\n\nThere's a doctor at the Emerald Sanctuary in Felwood, Dr. Nkechi Adeyemi, who's "
        "treating a sickness that sounds a lot like this one. She sent me the kit I've been using all month. I'd "
        "like to send her something back.\n\nTake the zeppelin from Tirisfal to Orgrimmar, then go north through "
        "Ashenvale to Felwood. The Sanctuary's the clean glade in the middle of it. Keep the vial out of the sun.",
        "A serum, from the Plaguelands? Let me see.\n\nThis is clever work. I was an emergency doctor in Lagos, back "
        "home, and I'd have been glad of this then. Tell him I'll try it on the felblight, and I'll write."),

    # ---------------------------------------------------------------- Sister Amalie Crane, the Pale Watch shrine
    "pln_the_inquisitors": V(
        "Kill Hearthglen Inquisitors in the fields below Hearthglen.",
        "I was a priestess in Hearthglen. When the Hearthglen Inquisitors started questioning the newcomers, I "
        "stood in the room while they did it. I held the candle. I didn't say a word.\n\nThen one day I walked "
        "out, and I kept walking until I reached this town. I think I'm still walking.\n\nThe inquisitors go down "
        "into the fields in pairs, looking for anyone to question. I want them stopped. They'll burn you if they can, so "
        "don't let them finish a prayer.",
        "I knew some of them. I prayed beside some of them.\n\nI won't pretend I'm not glad they're gone. That's "
        "something I'll have to make peace with."),
    "pln_the_confessions": V(
        "Take Signed Confessions from the Hearthglen Inquisitors.",
        "The inquisitors carry the confessions they've forced out of people, signed and sealed, so they can be "
        "read out before a burning. Every one of them has a name on it.\n\nI'd like those names remembered by "
        "somebody who isn't going to burn them.\n\nThe Hearthglen Inquisitors keep the confessions in their "
        "satchels. Not all of them will have one. Bring me whatever you find, and please don't read them. They "
        "aren't true, and the people who signed them knew it.",
        "Here's Agnieszka Nowak, and Tunde Bello, and Hyun-woo Park, and they didn't even spell them "
        "properly.\n\nThese people came here from nowhere and we burned them for it. I'll make sure they're "
        "remembered."),
    "pln_the_book_of_names": V(
        "Carry the Bundle of Confessions to Chaplain Odile Marchand at the Order's chapel in the Bulwark.",
        "Chaplain Odile Marchand keeps a book of names, everyone the Order knows of who died in the Plaguelands. "
        "She brought it down from Sorrow Hill when the Order moved into the Bulwark, and it's the only thing she "
        "carried herself.\n\nI'd like the people in these confessions to go into her book. Their names should be "
        "somewhere other than Hearthglen's ledgers.\n\nGo south to the Bulwark. The Order's chapel is on the south "
        "side of the street. Tell her they're from me, and that I'm sorry there are so many.",
        "These are from Amalie? She was in Hearthglen when these were taken.\n\nI'll write every name in the book "
        "tonight. Some of them were from Lyon, you know. I knew one of these streets."),
    "pln_high_inquisitor_faulk": V(
        "Kill High Inquisitor Faulk and the Hearthglen Inquisitors who walk with him.",
        "High Inquisitor Faulk runs the inquisition at Hearthglen. I served under him. He's the one who decided "
        "the newcomers were the Scourge's agents, and he decided it on a Tuesday, between breakfast and prayers.\n\n"
        "On feast days he walks the fields himself, with the Hearthglen Inquisitors at his back. Today's a feast "
        "day.\n\nHe'll be below the walls, close to the gate. He's got a temper and a lot of fire, and he heals "
        "himself when he's hurt. Bring friends, and bring someone who can stop his prayers.",
        "Then it's done, and the inquisition's got nobody to lead it.\n\nI keep waiting to feel something. I think "
        "maybe I feel lighter."),
    "pln_the_weeper": V(
        "Put the Weeper to rest at the pool at the end of the Weeping Cave.",
        "Oona told me about the water out of the Weeping Cave, and I know the story behind it. I wish I didn't.\n\n"
        "When Hearthglen took a family for questioning, the mother went looking for them. She went into the cave "
        "because somebody told her they'd been taken out that way. She went into the pool at the end of it, and "
        "she never came out. The Weeper is her. I'm nearly sure of it.\n\nThe pool's at the far end of the cave, "
        "past both galleries. She'll know you're coming, because she's been waiting for somebody for years. Be "
        "gentle if you can, and be quick if you can't.",
        "Thank you. I'll write her name in the chapel book, under the ones Hearthglen never wrote down.\n\nI kept "
        "quiet in that room for a long time. I'm trying to make up for it, one name at a time."),

    # ---------------------------------------------------------------- Woodwright Jonah Lind, the Pale Watch
    "pln_northridge": V(
        "Kill Scarlet Lumberjacks and Scarlet Sawyers at Northridge Lumber Camp.",
        "I'm Jonah, and I built every wall in this town, and I built them out of green wood because it's all I could "
        "get.\n\nThe Crusade runs a lumber camp at Northridge, in the west, and the Scarlet Lumberjacks and Scarlet "
        "Sawyers up there cut the best oak in the north. All of it goes up the hill to Hearthglen.\n\nI'd like the "
        "camp emptied. The lumberjacks are in the woods and the sawyers are at the mill. They're working men with "
        "axes, so don't underestimate them.",
        "That's the camp quiet, then. Now we can see about the wood.\n\nI built houses in Duluth, back home. Long "
        "winters, good timber. This place reminds me of it, except for the dead."),
    "pln_woodsman_archers": V(
        "Kill Scarlet Woodsman Archers in the trees round Northridge.",
        "With the lumberjacks gone, the Crusade's sent Scarlet Woodsman Archers into Northridge's trees to guard "
        "the timber. They're good shots, and they know those woods better than I do.\n\nI can't send wagons in "
        "while they're up there. They hide in the trees round the camp. Look up, because they like the high "
        "branches, and don't let them pin you down in the open.",
        "The woods are clear. My wagons go in tomorrow.\n\nI'll need someone to pick out the good planks before the "
        "rest of them burn the lot."),
    "pln_seasoned_oak": V(
        "Take Seasoned Planks from the Scarlet Sawyers at the Northridge mill.",
        "The wall round the Watch is green wood, and it's started to warp. Another winter and I'll be able to "
        "post letters through the gaps.\n\nThe Scarlet Sawyers at Northridge carry the camp's best seasoned planks "
        "to the carts. Seasoned oak won't warp. I want enough to rebuild the gate, at least.\n\nTake the planks off "
        "the sawyers before they reach the carts. Look for Hearthglen's stamp, because that's the good stuff.",
        "Feel the weight of that. That's proper oak.\n\nThe gate will be up by the end of the week. I'd like to meet "
        "the man who's been running that camp, though."),
    "pln_foreman_harrow": V(
        "Kill Foreman Harrow at the mill in Northridge.",
        "Foreman Harrow runs Northridge for the Crusade. He's the one who sent the archers out, and he came back "
        "to the camp yesterday with a fresh crew.\n\nAs long as he's there, the camp fills up again every time we "
        "empty it.\n\nHe's at the mill in the middle of Northridge. He's a big man with a big axe, and he doesn't "
        "like visitors. Take friends with you.",
        "That's the end of Northridge for the Crusade.\n\nThe camp's ours now. I'll put a crew in there next month "
        "and we'll cut our own timber."),
    "pln_saw_blades": V(
        "Take Hearthglen Saw Blades from the Scarlet Lumberjacks at Northridge.",
        "I can't cut timber without saws, and the Crusade took every saw in the Plaguelands up to Northridge. I've "
        "been shaping planks with a hatchet, and it shows.\n\nThe Scarlet Lumberjacks carry good steel blades, "
        "forged in Hearthglen. They carry them on their backs in the woods.\n\nBring me the blades and leave the "
        "handles. I'll make my own handles. I'm a carpenter, not a smith.",
        "These are beautiful blades. Hearthglen's smiths know their business, I'll give them that.\n\nWe'll have a "
        "proper sawpit at the Watch by the end of the week."),

    # ---------------------------------------------------------------- Oona Byrne, the Pale Watch's creek
    "pln_snapjaws_on_the_thondroril": V(
        "Kill Thondroril Snapjaws on the banks of the Thondroril.",
        "I'm Oona, and I catch the Watch's supper. I fish the Thondroril, mostly, and the Thondroril Snapjaws "
        "keep taking my catch, and my lines, and once my boot.\n\nThey're big and they're mean, and nothing in that "
        "river has ever told them no.\n\nThey sun themselves on the banks east of the town. Watch out for the bite, "
        "because they don't let go. Stay out of the water.",
        "My lines will last the day now.\n\nI fished out of Galway, back home. The fish here are different, but the "
        "patience is the same."),
    "pln_plague_bats": V(
        "Kill Plague Bats along the Thondroril.",
        "The Plague Bats come out over the Thondroril at dusk and dive at the water, and at me. I'm sure they "
        "carry the plague, and I'm tired of fighting them off with a fishing rod.\n\nThey roost in the trees "
        "along the river. They're fast, so don't chase them. Stand still on the bank and let them come to you, "
        "because they will.",
        "I can fish at dusk again. That's the best time for it.\n\nThank you. Take one of these, and I'll keep a "
        "fish back for you at supper."),
    "pln_antler_hooks": V(
        "Take Blighted Stag Antlers from the Blighted Stags in the fields.",
        "I've run out of hooks, and there's nowhere out here to buy them. I carve my own from antler, the way my "
        "grandfather taught me.\n\nThe Blighted Stags in the fields have antlers that are still sound under the grime, because I've checked.\n\nThey graze north and east of the town. Bring me the tines, not the whole rack. I "
        "don't need a rack, I need hooks.",
        "These will carve beautifully.\n\nMy grandfather taught me this on the beach at Salthill, back home. I never "
        "thought I'd need it."),
    "pln_old_thondroril": V(
        "Kill Old Thondroril and the Thondroril Snapjaws round his pool.",
        "There's one snapjaw in the Thondroril I've never been able to move. Old Thondroril is older than the "
        "plague and bigger than a cart, and the Thondroril Snapjaws follow him round like he's their king.\n\nHe "
        "sits on the deep pools, where the big fish are. I've been looking at those fish for months.\n\nHe keeps to "
        "the deepest pool and comes up when he's hungry. Kill the young ones while you wait. Stay on the bank, "
        "because he's stronger in the water.",
        "The deep pools are mine now. Look at the size of the fish down there.\n\nYou'll eat well at the Pale Watch "
        "tonight, and every night after."),
    "pln_the_water_under_the_hill": V(
        "Kill Cave Drowned and Seepwater Shades in the Weeping Cave, in the hill above the Thondroril.",
        "I've fished the Thondroril every day since the Watch went up, and the river's gone wrong. There's water "
        "running into it out of the hill, and it tastes of the grave. The fish won't go near it.\n\nIt's coming "
        "out of the Weeping Cave. Something in there keeps the water moving, the Cave Drowned and the Seepwater "
        "Shades, I'm told.\n\nThe cave's in the hill on the east side, up above the river. You'll hear it before you "
        "see it, because the water never stops running down the walls. Mind your feet in there. It's slick all the "
        "way down.",
        "The fish'll come back now, give it a week.\n\nThere's a cave like that on the coast near Galway, back home. "
        "The water ran out of it clean. I never thought I'd miss a cave."),

    # ---------------------------------------------------------------- Clerk Wendel Ashby, the Pale Watch hall
    "pln_the_patrol_roster": V(
        "Take the Hearthglen Patrol Roster from a Scarlet Sentry below Hearthglen.",
        "I'm Wendel, and I kept Hearthglen's books until I read what I was writing down, and then I left. I still "
        "keep books. It's an old habit.\n\nThe Scarlet Sentries carry the week's roster, which tells everyone "
        "where to stand on the walls. If I had a copy, the Watch would know those walls as well as I used to.\n\n"
        "The sentries on the road below the gate carry it in a leather case at the belt. Bring it back dry, "
        "please. The ink runs.",
        "This is in Brother Jessup's hand. I'd know his capitals anywhere.\n\nThe newcomers here always ask how I can "
        "read the walls from a page. It's just bookkeeping, really."),
    "pln_hearthglens_hounds": V(
        "Kill Scarlet War Hounds in the fields below Hearthglen.",
        "The roster says Hearthglen sends its Scarlet War Hounds out at night, to hunt anyone near the walls. I "
        "used to feed those dogs. They were good dogs, once. They'd sit for a crust.\n\nThey aren't good dogs any "
        "more. They're what Hearthglen made them.\n\nThey hunt the fields below the walls at night, in packs. Don't "
        "let them circle you. Back up against something and let them come.",
        "They were good dogs once. I used to give them the scraps from the kitchen.\n\nThat's done, then. Thank you. "
        "I'll write it down, because somebody should."),
    "pln_the_hermits_account": V(
        "Kill the Drowned Hermit in his cell in the roof of the Weeping Cave.",
        "I remember every name in Hearthglen's ledgers, and one of them belonged to a hermit who lived in the cave "
        "above the river. He paid his tithe in fish, every quarter, for eleven years.\n\nWhen the plague came, the "
        "Crusade stopped taking his fish, and he stopped coming down. I'm told The Drowned Hermit still keeps his "
        "cell in the roof of the Weeping Cave, and that he won't let anyone past.\n\nHis cell's up through the roof "
        "of the upper gallery, about halfway along. He'll have his oar, I expect. He never went anywhere without "
        "it. Close his account for me, would you?",
        "Tobias Fenn, paid in perch every quarter for eleven years. I'll mark him settled.\n\nIt's a small thing, "
        "closing an account properly. Somebody ought to do it for everyone Hearthglen forgot."),

    # ---------------------------------------------------------------- in from outside
    "pln_supplies_from_felwood": V(
        "Carry Dr. Adeyemi's Field Kit to Field Medic Noah Kowal at the Pale Watch in North WPL.",
        "I've heard from the Order of the Pale Flame that their field medic at the Pale Watch is stitching people "
        "up with thread he boils in a pot. I was an emergency doctor in Lagos. I know exactly what that "
        "means.\n\nSo I've packed everything the Sanctuary can spare. Sutures, dressings, a bottle of something "
        "strong.\n\nIt's a long way, I know. Get yourself to the Eastern Kingdoms, through Tirisfal to the Bulwark, "
        "and keep going north up the King's Road. The Pale Watch's gate is off the road where it starts to climb "
        "toward Hearthglen. Don't let anyone ration the sutures.",
        "Real sutures, clean dressings, and a bottle of something I haven't seen since Winnipeg.\n\nTell Dr. Adeyemi "
        "she's saved more people today than I've managed all month. Then come back, because I've got work for you."),
})

# =============================================================================================== WEST EPL (55-58)
# Crown Guard's people live in Light's Hope Chapel now (Kyle: "fold Crown Guard Camp into Lights Hope"), so the road
# west starts at the chapel's gate, runs past the empty tower and over the line into West EPL.
VOICE.update({
    # ---------------------------------------------------------------- Outrider Bram Tolliver, Light's Hope
    "plw_the_road_west": V(
        "Kill Plague Hounds and Frenzied Ghouls along the road through West EPL.",
        "Bram Tolliver, outrider. I used to ride out of Crown Guard. Now I ride out of here, and it's a longer "
        "ride, and I'm still the only one who does it.\n\nThe road west runs past the old tower and over into the "
        "western half of the Plaguelands, all the way to the river. The Plague Hounds hunt along it in packs, and "
        "the Frenzied Ghouls come up out of the ditches the moment they hear a horse.\n\nI'd like that road safe "
        "enough for somebody other than me. The hounds run the open ground and the ghouls wait in the ditches. "
        "Don't stop moving, because they'll swarm you if you do.",
        "That's a road a wagon could use again.\n\nThe newcomers here keep asking why I ride it alone. I tell them "
        "it's because nobody else is daft enough."),
    "plw_corins_crossing": V(
        "Kill Cult Plaguebringers and Cult Cart Drivers at Corin's Crossing.",
        "Corin's Crossing was a crossroads town when I was a boy. Fairs, horse sales, a pie shop I still think "
        "about. The Cult took it over, and now it's where the plague carts load.\n\nThe Cult Plaguebringers fill "
        "the barrels in the square, and the Cult Cart Drivers take them out to whatever farms are still alive. I've "
        "followed those carts. I've seen what's left after they leave.\n\nThe crossing's on the road west, where the "
        "roads cross. Kill the plaguebringers first, because they'll throw the barrels at you if you give them "
        "time.",
        "No carts left the crossing today. That's the first day in a year.\n\nOne of the drivers had papers on him, "
        "and I'd like you to see them."),
    "plw_the_manifest": V(
        "Take a Plague Cart Manifest from a Cult Cart Driver at Corin's Crossing.",
        "The drivers carry manifests. Every barrel, every farm, every day it's due. If I had one, the Dawn could "
        "warn those farms before the carts got there.\n\nFind a Cult Cart Driver at the crossing and take his "
        "manifest off him. It'll be in his coat, inside pocket, because they're tidy people, the Cult. Bring it "
        "back as fast as you can. Those carts don't wait for anybody.",
        "These are all farms in Lordaeron that are still alive, and some in the hills past it.\n\nI'll have riders "
        "out to every one of them by nightfall. You've saved lives today, whether you see them or not."),
    "plw_the_crossings_abominations": V(
        "Kill the Crossing Abominations in the square at Corin's Crossing.",
        "The Cult's noticed its drivers are dying, and it's brought in muscle. There are Crossing Abominations "
        "standing in the square now, round the carts, and they don't move unless something comes close.\n\nI'd "
        "like them brought down before the Cult finds another use for them.\n\nThey're slow and they hit like a "
        "falling barn. Pull them one at a time if you can, and keep the carts between you and the rest.",
        "That's the crossing's muscle gone.\n\nThere's only one man left running the carts, and I know exactly where "
        "he sleeps."),
    "plw_cartmaster_corin": V(
        "Kill Cartmaster Corin in the counting house at Corin's Crossing.",
        "Cartmaster Corin gave the crossing its name. He ran a carting business there before the plague, and now "
        "he runs it for the Cult, with the same ledgers and the same smile. I bought horses off him once. He gave "
        "me a fair price.\n\nI want him dead and his ledgers burned.\n\nHe's in the old counting house at the "
        "crossing. He doesn't fight fair and he'll call everything nearby to help him, so take friends with you.",
        "Then the carts stop for good. I'll burn the counting house myself tonight.\n\nHe gave me a fair price on "
        "those horses. I keep thinking about that."),

    # ---------------------------------------------------------------- Edda Marris, Light's Hope
    "plw_the_marris_stead": V(
        "Kill the Marris Farmhands and the Stead Crows at the Marris Stead.",
        "I'm Edda Marris. I married into the family two summers before the plague, and I was in town the day it "
        "reached the farm. I came home and they were all still working. Mother, my husband, his sister, the hands, every one of them still working.\n\nI came here so I didn't have to watch. I'm done not watching.\n\nThe Marris Stead is "
        "south of the road, toward Terrordale. The Marris Farmhands work the fields and the Stead Crows follow "
        "them, picking. They were good people. They'd want it quick.",
        "Thank you. I've wanted that done for a long time, and I couldn't do it myself.\n\nOne of them always wore a "
        "locket. I'd give anything to have it back."),
    "plw_the_marris_locket": V(
        "Find the Marris Locket on one of the Marris Farmhands at the stead.",
        "My husband's sister wore a brass locket with a painting of the whole family inside. She wore it every "
        "day, even in the fields. She's still wearing it, out there with the others.\n\nI'd like it back. I'd like "
        "something of theirs that isn't the farm.\n\nShe'll be one of the farmhands at the stead. It's a little "
        "brass locket on a chain. You'll know it when you see it.",
        "That's them, all of them. That's the summer before everything.\n\nI'm not in it. I hadn't married in yet. "
        "There's one more of them out there, though, and he's the worst to think about."),
    "plw_old_marris": V(
        "Put Old Marris to rest at the Marris Stead.",
        "Old Marris was the head of the family. He built that farm with his own hands and he never let anyone "
        "forget it. He still walks it, still giving orders to the dead.\n\nHe was hard on me, the first summer. By "
        "the second, he'd taught me to plough. I'd like him to rest with the others.\n\nHe's in the farmhouse, or "
        "in the barn behind it. He's strong, because he always was. Take friends if you can, and be kind to him if "
        "you can't.",
        "Then they're all at rest. The farm can go back to being a farm.\n\nI think I'll go back there in the spring "
        "and plant something. He'd have liked that."),
    "plw_the_family_crypt": V(
        "Kill Crypt Shamblers and Marris Ossuary Guards in the Marris Crypt, under the stead.",
        "There's a crypt under the stead where the family's always buried its own. I've heard the dead down there "
        "don't stay in their niches any more.\n\nThe Crypt Shamblers walk the passages and the Marris Ossuary "
        "Guards stand at the doors. The guards were the family's own men once, and they'll still try to stop "
        "you.\n\nThe stair down's at the stead, south of the farmhouse. It's laid out like a grid down there, so "
        "count your turns. I'd like the family back where they were put.",
        "Thank you. My husband's grandmother is down there somewhere, and I hope she's back where she "
        "belongs.\n\nThere's more, though. Something's still singing down there, and it isn't any hymn I know."),
    "plw_the_sexton": V(
        "Kill Sexton Hollowell and the Bone Choir in the Marris Crypt.",
        "The family's sexton buried every Marris for forty years, and he didn't stop when the plague came. Sexton "
        "Hollowell is still down there digging, and the dead he's buried sing for him. The Bone Choir, the hands "
        "called it, before they were in it.\n\nI'd like him put in the ground for good, and the singing stopped.\n\n"
        "His hall's in the middle of the crypt, and the choir sings from the chapel at the head of it. You'll hear "
        "them both. Don't listen to the words, because they'll tell you to lie down.",
        "It's gone quiet down there. I didn't know how loud it was until it stopped.\n\nI'll go down myself next "
        "week and say their names. Somebody in the family should, and I'm the only one of us left breathing."),

    # ---------------------------------------------------------------- Dr. Sun Li, Light's Hope
    "plw_the_fungal_vale": V(
        "Kill Vale Plague Slimes and Spore-Walkers in the Fungal Vale.",
        "I'm Dr. Sun Li. I studied fungi in Kunming for twenty years, back home, and the Fungal Vale is the most frightening "
        "thing I've ever seen.\n\nSomething is growing there, and it isn't one thing. The Vale Plague Slimes crawl "
        "along the ground spreading it, and the Spore-Walkers drift between the caps carrying it on their backs. "
        "Every week it's a little wider.\n\nThe vale's north of Corin's Crossing, on the road toward Stratholme. "
        "Thin them before it spreads further. Don't breathe the spores, and keep your mouth shut while you're in "
        "there. I mean that literally.",
        "That's slowed it down, I think. It's hard to tell with fungus.\n\nI need samples, if you'll go back, and I "
        "want them fresh."),
    "plw_spore_caps": V(
        "Cut Spore-Walker Caps from the Spore-Walkers in the Fungal Vale.",
        "The Spore-Walkers grow caps on their shoulders, and I think the caps are where the plague is changing. "
        "It's mixing with the fungus in there, and I need to see how. Nothing I learned on Earth covers this.\n\nCut the caps off the walkers in the "
        "vale. Put them in these sacks and tie them tight. If one starts to puff, drop it and don't look back. I "
        "can't stress that enough.",
        "These are breathing. They're actually breathing.\n\nIt's dozens of fungi growing together, and something at "
        "the middle of the vale is holding them together."),
    "plw_the_fungal_mass": V(
        "Kill the Fungal Mass at the heart of the Fungal Vale.",
        "At the heart of the vale there's something I can only call a mass. A fungus the size of a house, that "
        "moves when it wants to. Everything else in the vale is feeding it, or it's feeding them. I can't tell "
        "which and I don't think it matters.\n\nThe Fungal Mass. Kill it, and the rest will start dying back.\n\nIt "
        "sits in the middle of the vale and it'll come at you when you get close. It's huge and it's poisonous. "
        "Take friends and take antidotes.",
        "It's really dead? Then the vale will start dying back in a week.\n\nThat was the strangest organism I've "
        "ever studied, and I'm glad it's gone."),
    "plw_spores_for_the_sanctuary": V(
        "Carry the Sealed Spore Sample to Yuki Hashimoto at the Emerald Sanctuary in Felwood.",
        "I've sealed a sample of the vale's spores in wax. There's a botanist at the Emerald Sanctuary in Felwood, "
        "Yuki Hashimoto, who's cataloguing everything that grows back in corrupted ground. If anyone's seen "
        "something like this, it's her.\n\nI'd like her to compare it with what grows in Felwood.\n\nTake the "
        "zeppelin from Tirisfal to Orgrimmar, then go north through Ashenvale to Felwood. Yuki's at the Sanctuary, "
        "probably on her knees in a flowerbed. Don't break the wax.",
        "From Dr. Sun? I read her papers at university, back home.\n\nThe corruption here makes things grow back "
        "wrong, and these spores are doing the same thing. I'll write to her tonight."),

    # ---------------------------------------------------------------- Gravewarden Osric Vey, Light's Hope
    "plw_terrordale": V(
        "Kill Terrordale Ghouls and Terrordale Spirits in Terrordale.",
        "I'm Osric Vey, the Dawn's gravewarden. We bury our own here, and anyone else who needs it. Terrordale is "
        "full of people nobody buried.\n\nThe Terrordale Ghouls hunt the valley floor and the Terrordale Spirits "
        "wail along the hills above them. I'd like the valley quieter before I take a spade to it.\n\nTerrordale's "
        "in the south-west, past the Marris Stead. Stay out of the spirits' reach, because they'll drain you.",
        "I felt that from here. The valley's quieter tonight.\n\nThere's worse in Terrordale, though. The ones who "
        "raise the dead are still there."),
    "plw_the_skeletal_mages": V(
        "Destroy the Terrordale Skeletal Mages in Terrordale.",
        "Terrordale's dead don't stay down, because the Terrordale Skeletal Mages raise them again every night. "
        "They were Kirin Tor once, I think, sent to fight the plague and lost to it. They still wear the "
        "violet.\n\nI'd like them destroyed. Nobody can rest in that valley while they're standing.\n\nThey stand "
        "among the dead, raising them. Kill them quickly, because they'll raise anything you kill near them.",
        "No more risings in Terrordale. Thank the Light.\n\nThe thing that rules that valley is still there, though, "
        "and it's what made them."),
    "plw_the_terror_of_the_dale": V(
        "Kill the Terror of the Dale in the ruined chapel at Terrordale.",
        "Terrordale's named for what lives in it. The Terror of the Dale was a lich's apprentice who stayed behind "
        "when the lich went north, and it's held the valley ever since.\n\nI'd like it ended, so the valley can be "
        "buried properly. I've been putting off the digging for a year.\n\nIt holds the ruined chapel in the middle "
        "of Terrordale. It's a caster, and it'll freeze you if you let it. Take friends, and keep moving.",
        "Then Terrordale belongs to nobody, and it can rest.\n\nI'll write what happened there and send it west. "
        "There's someone across the sea who needs to read it."),
    "plw_word_for_sun_rock": V(
        "Carry Osric's Account to Spiritwalker Tohana at Sun Rock Retreat in Stonetalon.",
        "The Forsaken say the dead are rising in Mulgore, across the sea, with nobody calling them. There's a "
        "tauren spiritwalker at Sun Rock Retreat in Stonetalon, Tohana, trying to understand why.\n\nI've written "
        "down everything I know about Terrordale. How the dead rose, how they stayed up, what put them down. It "
        "might help her. It might not. It's what I have.\n\nTake the zeppelin from Tirisfal to Orgrimmar and a wind "
        "rider to Sun Rock. Tohana's the spiritwalker by the fire. Give it to her and nobody else.",
        "From the Plaguelands? From a gravewarden of the Dawn?\n\nThe spirits in Mulgore are restless the same way, "
        "like something's calling them and they don't know where from. This helps more than you know. Tell him the "
        "earth thanks him."),

    # ---------------------------------------------------------------- Greta Lowe, Light's Hope kitchen
    "plw_crow_pie": V(
        "Take Plump Stead Crows from the Stead Crows at the Marris Stead.",
        "I'm Greta, and I kept the beds at Crown Guard, and now I keep the chapel's kitchen, and the chapel eats "
        "better than it did, if I say so myself.\n\nMy grandmother made crow pie, and the Stead Crows at the Marris "
        "Stead are the fattest crows I've ever seen. They've been eating well. Don't think about what on.\n\nThey "
        "follow the farmhands at the stead, south of the road. Get the fat ones. And don't tell anyone what's in "
        "the pie until after they've had seconds.",
        "Look at the size of them! That's a pie for the whole chapel.\n\nThe newcomers will eat it and ask what it "
        "was. I'll tell them it's chicken, and they'll believe me."),

    # ---------------------------------------------------------------- Ser Roland Ashcombe, Light's Hope
    "plw_gargoyles_over_the_road": V(
        "Kill Stone-Winged Gargoyles over the road to Stratholme.",
        "Ser Roland Ashcombe. I keep the Dawn's watch on Stratholme, and the Stone-Winged Gargoyles keep watching "
        "me back.\n\nThey fly over the road out of the city and dive on anyone who looks at it too long. I've been "
        "looking at it too long for years.\n\nThey circle over the road north of Corin's Crossing, toward "
        "Stratholme. They'll turn to stone when they're hurt, so finish them quickly, and don't let them get above "
        "you.",
        "I can see the road again without a gargoyle in the way.\n\nThe gate's a different matter, and that's where "
        "the real work is."),
    "plw_the_gates_of_stratholme": V(
        "Kill Gate Death Knights and Gate Gargoyles at Stratholme's gate.",
        "Stratholme's gate is held by Gate Death Knights, with Gate Gargoyles perched over them. I was a knight of "
        "Lordaeron before the city fell. Some of those death knights were my brothers in arms. I know their "
        "shields.\n\nThin the gate, so the Dawn can get close enough to see inside.\n\nFollow the road north past "
        "the Fungal Vale and west through Plaguewood, and the gate's at the end of it. The death knights don't "
        "retreat, so pick them off one at a time.",
        "I knew some of those men. I'll pray for them, the ones I recognised.\n\nThere's one left at the gate who "
        "holds it, and he's the one I want."),
    "plw_gatekeeper_vorthas": V(
        "Kill Gatekeeper Vorthas at Stratholme's gate.",
        "Gatekeeper Vorthas was a captain of Stratholme's guard. He held the gate when the city fell, and he holds "
        "it still, for the Scourge now. I served under him. He taught me how to hold a shield.\n\nI'd like my old "
        "captain at rest. I can't do it myself. I've tried, and I couldn't lift my sword.\n\nHe stands at the gate, "
        "where he always stood. He's a death knight now, and he's strong. Take friends, and don't fight him alone.",
        "Then he's at rest. I hope he knows that I'm sorry.\n\nEvery one of us who served under him owes you for "
        "this."),
    "plw_sigils_of_the_fallen": V(
        "Take Knightly Sigils from the Gate Death Knights at Stratholme's gate.",
        "The Gate Death Knights still wear the sigils of the houses they served when they were alive. Barov, "
        "Mardenholde, a dozen others. The houses that are left don't know what became of their sons and "
        "daughters.\n\nI'd like the sigils back, so I can tell them.\n\nThe death knights wear them on their "
        "breastplates. Cut them off and bring them to me. I'll know every house by its colours.",
        "That's Barov, and that's Mardenholde, and this one's my own cousin's house.\n\nI'll write to every family "
        "that's left. It's the least they deserve, and it's more than most of them will get."),

    # ---------------------------------------------------------------- Huntress Kaia Lindgren, Light's Hope
    "plw_plaguewood": V(
        "Kill Plaguewood Spiders and Plaguewood Crypt Fiends in Plaguewood.",
        "I'm Kaia, and I herded reindeer outside Tromso before the Integration, and now I hunt for the chapel. "
        "Plaguewood is the worst hunting ground I've ever seen.\n\nThe Plaguewood Spiders spin webs across every "
        "path, and the Plaguewood Crypt Fiends dig under them and come up through the floor. Nothing lives in there "
        "that I'd want to eat.\n\nPlaguewood's north-west of Corin's Crossing, on the road to Stratholme. The "
        "spiders are in the trees and the fiends are underground. Watch where you step.",
        "That's some ugly hunting. Thank you for doing it with me.\n\nI never thought I'd miss the cold, and I miss "
        "it every day."),
    "plw_plaguewood_silk": V(
        "Take Plaguewood Silk from the Plaguewood Spiders.",
        "I make my own snares, and the Plaguewood Spiders spin silk that's stronger than any rope in the "
        "Plaguelands. I'd like enough to rig snares round the whole chapel. The dead don't cross holy ground, but "
        "the animals do.\n\nThe spiders carry it in their glands. Cut it out carefully, because it sticks to "
        "everything, and wear gloves if you've got them.",
        "This is beautiful silk. I'll have snares round the chapel by the weekend.\n\nThere's a big one in "
        "Plaguewood, the mother of all of them. I'd like to see her gone."),
    "plw_the_plaguewood_matriarch": V(
        "Kill the Plaguewood Matriarch in the heart of Plaguewood.",
        "Every spider in Plaguewood came out of the same nest, and the thing that laid them is still sitting on "
        "it. I call her the Plaguewood Matriarch. She's bigger than a horse.\n\nAs long as she's there, the wood "
        "fills up again as fast as we empty it.\n\nShe's in the deepest part of Plaguewood, where the webs are "
        "thickest. She's fast and she's poisonous. Take friends, and bring a knife for the webs.",
        "She's really dead? Then Plaguewood will empty out in a season.\n\nI'll make you a snare from her silk, if "
        "you like. It'd hold a dragon."),
    "plw_carrion_grubs": V(
        "Kill Carrion Grubs along the road through West EPL.",
        "The Carrion Grubs eat everything that dies on the road west, and then they eat everything that's alive "
        "and slow. I've lost every snare I set out there this month.\n\nThey swarm the road and the ditches beside "
        "it. They're slow and they're soft, but there are always more of them. Burn them if you can, because they "
        "don't like it.",
        "That's the road clear of them for a while, anyway.\n\nThank you. I'd rather hunt anything else in the world "
        "than those."),
    "plw_hound_fangs": V(
        "Take Plague Hound Fangs from the Plague Hounds on the road west.",
        "I've run out of arrowheads. The Plague Hounds on the road west have fangs as hard as flint, and I've "
        "been knapping them into points. They fly true, truer than the steel ones.\n\nThe hounds run in packs along "
        "the road, past the old tower. Pull the big canines, the ones at the front. I'll do the rest by the fire.",
        "These are perfect. I'll have a quiver full by tomorrow night.\n\nMy grandfather made fishhooks from bone, "
        "back home. I didn't think I'd ever need to know how."),

    # ---------------------------------------------------------------- Commander Eligor Dawnbringer, Light's Hope
    "plw_a_look_at_stratholme": V(
        "Walk to Stratholme's gate, look at it, and come back.",
        "I'm Eligor Dawnbringer, and I command the Argent Dawn here. I haven't seen Stratholme since it fell. I "
        "won't send the Dawn in until somebody I trust has looked at it and come back.\n\nI'm asking you to be that "
        "somebody. Walk to the city's gate and look at it, nothing more. Then come back and tell me.\n\nGo west along "
        "the road, north past the Fungal Vale, and west through Plaguewood. The gate's at the end of it. Don't go "
        "in, whatever you hear.",
        "Then it's as bad as we thought.\n\nThe newcomers say they've seen cities like that in their dreams, burned "
        "and empty. I wish they hadn't."),

    # ---------------------------------------------------------------- Gwen Pike, Light's Hope
    "plw_gargoyles_over_the_gates": V(
        "Kill Gate Gargoyles over Stratholme's walls and Stone-Winged Gargoyles on the open ground below.",
        "I'm Gwen, and I flew Crown Guard's bats, and now I nurse the ones that come in hurt, and lately that's a lot "
        "of them.\n\nThe Gate Gargoyles over Stratholme have started coming out to meet the Dawn's bats on the "
        "western road. I lost two this month. The Stone-Winged Gargoyles that hunt the ground under them finish off "
        "whatever falls.\n\nThe gate ones roost on Stratholme's walls at the top of the road, and the wild ones hunt "
        "the open country below. Bring them down where you can reach them, because they don't like to land.",
        "Aldous says the bats will fly the western road again. They're nervous animals and so am I, but we'll "
        "manage.\n\nThe gargoyles never used to come out this far. Something in that city's waking up."),

    # ---------------------------------------------------------------- in from outside
    "plw_what_grew_in_the_jar": V(
        "Carry Yuki's Jar to Dr. Sun Li at Light's Hope Chapel in the Eastern Plaguelands.",
        "I catalogue everything that grows back in Felwood, and somebody sent me a jar of spores from the "
        "Plaguelands' Fungal Vale. I put it on my bench a week ago. It's grown, and it's grown into something "
        "I've never seen.\n\nDr. Sun Li needs to see what her spores turn into. She's with the Argent Dawn at "
        "Light's Hope Chapel, at the far east end of the Eastern Plaguelands.\n\nIt's a long way, so wrap the jar "
        "in something and keep it upright. It's started tapping on the glass, and I'd rather it didn't get out.",
        "Oh, that's beautiful, and I hate it.\n\nI studied fungi in Kunming for twenty years, back home, and nothing "
        "ever moved on its own. Tell Yuki I owe her a very long letter, and come back when you've rested. The vale's "
        "worse than I thought."),
})

# =============================================================================================== EAST EPL (56-60)
# Light's Hope Chapel is its own map, its gate up a spur off the road between the old tower and Tyr's Hand; Crown
# Guard's people live inside it now. Everything below is "out the gate" from there.
VOICE.update({
    # ---------------------------------------------------------------- Captain Joss Varden, Light's Hope
    "ple_the_road_between": V(
        "Kill Blighted Warhorses and Plague-Rotted Bears along the road between Light's Hope and the old tower.",
        "I'm Joss Varden. I held Crown Guard's camp until the Dawn talked me into bringing everyone inside these walls, "
        "and I'll admit the beds are better. The road between here and Stratholme still needs holding, and it's "
        "only open while somebody keeps it open.\n\nThe Blighted Warhorses that used to pull the Crusade's wagons "
        "run wild along it now, and the Plague-Rotted Bears come down to the road to eat whatever the horses leave. "
        "Thin them both.\n\nOut the gate and west along the road toward the old tower. The horses run the road and "
        "the bears keep to the trees beside it. Don't let a horse get behind you, because they kick like they mean "
        "it.",
        "The road's open again, for a few days anyway.\n\nI'll take a few days. Out here a few days is a long time."),
    "ple_word_to_lights_hope": V(
        "Carry Varden's Report to Commander Eligor Dawnbringer on the chapel steps.",
        "I used to send this report up the road every week, and every week I wondered whether it would get there. "
        "Now it's a walk across the square, and I still can't make myself hand it over in person. Dawnbringer "
        "will want to ask questions, and I've got a road to watch.\n\nIt says the Crusade at Tyr's Hand is "
        "moving.\n\nTake it to Commander Eligor Dawnbringer. He stands on the chapel steps at the top of the town. "
        "Wait while he reads it, because he'll have something for you.",
        "Joss writes the way he fights, short and to the point.\n\nTyr's Hand is moving, then. I'll need people who "
        "can walk into it and walk back out. I think you'll do nicely.",
        title="Word to the Commander"),
    "ple_darrowshires_ghouls": V(
        "Kill Darrowshire Ghouls in the streets of Darrowshire.",
        "Darrowshire was a town in the south-west until the Scourge came for it. The town fought, and lost. The "
        "Darrowshire Ghouls that came out of that fight still walk its streets, and on bad nights they walk up the "
        "road toward the old tower.\n\nPut them down before the next bad night.\n\nDarrowshire's a long way west of "
        "here, south of the old tower, down the old road. The ghouls are in the streets and the yards. Mind the "
        "ghosts, because they're still fighting a battle that ended years ago.",
        "That'll keep them off my road for a while.\n\nThere's a ghost of a little girl in that town who talks to "
        "travellers. If you met her, I hope you were kind."),
    "ple_the_houndmasters": V(
        "Kill Tyr's Hand Houndmasters at the kennels in Tyr's Hand.",
        "The Crusade at Tyr's Hand sends its hounds up the road at night, and the Tyr's Hand Houndmasters who run "
        "them know exactly where my sentries stand. I lost two good people last week.\n\nI want the "
        "houndmasters dead, and I'd like their dogs to have nobody to come home to.\n\nTyr's Hand is on the coast, "
        "south of the chapel down the road. The houndmasters keep to the kennels at the north end. Kill the "
        "handlers and the hounds won't know what to do.",
        "Then nobody's sending dogs up my road tonight.\n\nThe Crusade calls you lot heretics, you know. I've heard "
        "worse said about better people."),
    "ple_arrows_on_the_road": V(
        "Kill Tyr's Hand Marksmen on the walls of Tyr's Hand.",
        "With the hounds gone, the Crusade's sent its archers instead. Every Tyr's Hand Marksman on the walls "
        "shoots at anything on the coast road, and my wagons can't get through that way.\n\nClear the walls. The "
        "marksmen stand on Tyr's Hand's walls and in its towers. Get close fast, because they won't come down to "
        "you, and don't stop in the open.",
        "My wagons got through this morning. The chapel's eating well tonight.\n\nYou've done more for this road "
        "than half my own people, and I'll say so to anyone."),

    # ---------------------------------------------------------------- Corporal Ines Duarte, Light's Hope well
    "ple_the_blackwood_shore": V(
        "Kill Blackwood Drowned on the shore of Blackwood Lake.",
        "I'm Ines, and I keep the water clean, which out here means I keep everyone alive. The chapel's well is "
        "good, but it isn't enough for everyone Crown Guard brought with it, so we haul the rest from Blackwood "
        "Lake.\n\nThe Blackwood Drowned walk out of that lake every night and foul the shore where I fill the "
        "barrels. I'd like to do my job without a sword in my other hand.\n\nThe lake's north-west of here, in the "
        "middle of the country. The drowned come up out of the shallows. Stay on the dry ground if you can, because "
        "they're stronger in the water and they'll try to pull you in.",
        "That's a clean shore, for now.\n\nI ran water treatment for the city of Lisbon, back home. I never thought "
        "I'd be doing it with a sword."),
    "ple_whats_in_the_water": V(
        "Take Snapjaw Gizzard Stones from the Blackwood Snapjaws at Blackwood Lake.",
        "I want to know how the plague gets into Blackwood Lake, and I think the Blackwood Snapjaws can tell me. "
        "They swallow stones to grind their food, and the stones soak up whatever's in the water. They're a "
        "record, if you know how to read them.\n\nThe snapjaws sun themselves on the shore. The stones are in the "
        "gizzard, which is exactly where it sounds like. I'm sorry, and thank you.",
        "Look at the green on these. It's in the silt, not the water.\n\nSo it's coming from something on the bottom, "
        "and I think I know what."),
    "ple_the_blackwood_drowner": V(
        "Kill the Blackwood Drowner and the Blackwood Snapjaws round its pool.",
        "Something sits on the bottom of Blackwood Lake and bleeds plague into the silt. The Drowned call it the "
        "Blackwood Drowner, and the Blackwood Snapjaws won't go near the deep water where it lies.\n\nDrag it out "
        "and end it, and the lake will start to clear on its own.\n\nIt comes up from the deep end when it's "
        "hungry. Thin the snapjaws on the shore while you wait. When it pulls you under, don't panic. Fight your "
        "way back to the shallows.",
        "The silt's clearing already. You can see the bottom by the reeds.\n\nI've got an idea, and it's bigger "
        "than one lake."),
    "ple_filters_for_felwood": V(
        "Carry Ines's Filter Drawings to Tomasz Wolny at the Emerald Sanctuary in Felwood.",
        "I've drawn up a filter, sand and charcoal and a bit of cleverness, that takes the plague out of "
        "Blackwood's water. I've heard there's a forest across the sea, Felwood, where the water's poisoned with "
        "something worse. They've got a carpenter at the Emerald Sanctuary, Tomasz Wolny, who builds whatever the "
        "druids need.\n\nI'd like him to build this.\n\nTake the zeppelin from Tirisfal to Orgrimmar, then north "
        "through Ashenvale to Felwood. The Sanctuary's the clean glade in the middle of it. Tomasz will be the one "
        "hammering something.",
        "These are good drawings. She's a proper engineer, this one.\n\nI built houses outside Krakow, back home. I "
        "can build these by the end of the week, and the Sentinels can drink from the stream again."),

    # ---------------------------------------------------------------- Greta Lowe, Light's Hope kitchen
    "ple_horse_for_the_pot": V(
        "Take Warhorse Flanks from the Blighted Warhorses on the road.",
        "The wagons come when they come, and the chapel's got a lot more mouths since Crown Guard moved in. I've "
        "found that the Blighted Warhorses on the road are sick on the outside and mostly fine on the inside, if "
        "you're careful.\n\nI want the meat, and I don't want to hear about it.\n\nThe horses run the road west of "
        "the gate. Cut from the flank, where the meat's thickest. Don't tell anyone what's in the stew, and I won't "
        "either.",
        "That's a week of stew, and nobody needs to know where it came from.\n\nThe newcomers eat anything, have you "
        "noticed? I like cooking for them."),
    "ple_a_barrel_for_sorrow_hill": V(
        "Carry the Barrel of Crown Guard Ale to Priya Raman in the Order's quarter of the Bulwark.",
        "I brew a dark ale out of whatever the wagons bring, and the woman who cooks for the Order of the Pale "
        "Flame, Priya Raman, wrote to say she'd trade me a recipe for a barrel. Nobody's ever offered me a recipe "
        "for ale before.\n\nI'd like the barrel taken west, and the recipe brought back in your head. Don't write "
        "it down. Recipes get stolen.\n\nThe Order's camped inside the Bulwark now, at the far west of the "
        "Plaguelands where the road comes in from Tirisfal. It's a long way, so fly if you can. And don't drink it "
        "on the way, because I'll know.",
        "Is this Greta's ale? Oh, she actually sent it.\n\nTell her the recipe's my mother's dal, and that it goes "
        "with dark beer better than anything I've ever tasted. I'll write it out for her.",
        title="A Barrel for the Order"),

    # ---------------------------------------------------------------- Gwen Pike, Light's Hope perch
    "ple_wild_bats": V(
        "Kill Carrion Bats in the dead trees round Light's Hope.",
        "The Dawn's riding bats are healthy, and Aldous and I mean to keep them that way. The Carrion Bats that "
        "roost in the dead trees round the chapel carry the plague, and they've started fighting ours for the "
        "perch.\n\nI want the wild ones gone.\n\nThey roost all round the chapel and they're out every evening. Ours "
        "have blue tags on their legs, so please don't hit those.",
        "My bats slept through the night for the first time in a month.\n\nI've got a young one who's ready for her "
        "own roost, if you'll carry her a very short way."),
    "ple_a_bat_for_lights_hope": V(
        "Carry the Covered Basket to Flight Master Aldous Grey at the chapel's perch.",
        "Aldous lost two bats to the Mossflayers this month, and I've got a young female who's ready to fly. I "
        "raised her at Crown Guard. She's the best one I've got.\n\nShe's in the covered basket. Take her across to "
        "Aldous at the perch on the east side of town, gently. It's not far, and I'd do it myself, but if she sees "
        "me hand her over she'll follow me home.\n\nKeep the cover on, because she'll try to fly back if she sees "
        "the sky.",
        "Oh, she's a lovely one. Look at her ears.\n\nTell Gwen I'll name her after her, and that she'll hate that.",
        title="A Bat for the Perch"),

    # ---------------------------------------------------------------- Commander Eligor Dawnbringer, the chapel steps
    "ple_tyrs_hand": V(
        "Kill Tyr's Hand Crusaders in the streets and on the walls of Tyr's Hand.",
        "The Scarlet Crusade holds Tyr's Hand, a walled town on the coast south of here. They think the Dawn are "
        "traitors for taking in anyone who'll fight, and they've said so, loudly, from the walls.\n\nI'd rather talk, and they won't, so I want the Tyr's Hand Crusaders on those walls thinned before they come north.\n\n"
        "Go out the gate and south down the road to the coast. The crusaders walk the streets and the walls. They'll "
        "fight to the last, so don't expect any of them to run.",
        "Good work, and grim work. I take no joy in killing the living.\n\nBut they'd burn half the people in this "
        "town for the crime of being newcomers, and I won't allow that."),
    "ple_the_abbots": V(
        "Kill Tyr's Hand Abbots in the chapels and cloister of Tyr's Hand.",
        "Tyr's Hand's crusaders fight because the Tyr's Hand Abbots tell them to. The abbots preach in the town's "
        "chapels every morning, and every morning the crusaders come out ready to die.\n\nStop the preaching, and "
        "the fighting will lose its heart.\n\nThe abbots keep to the chapels and the cloister in the middle of the "
        "town. They heal each other, so take them one at a time and don't let them gather.",
        "The bells didn't ring at Tyr's Hand this morning. I heard the silence from here.\n\nThere's one left who "
        "matters, and he's the worst of them."),
    "ple_abbot_varenne": V(
        "Kill Abbot Varenne in the great chapel of Tyr's Hand.",
        "Abbot Varenne rules Tyr's Hand. He was a priest of the Light in Lordaeron before the plague, and he's the "
        "one who decided that anyone who came from somewhere else was a servant of the dead.\n\nWe studied "
        "together at Northshire, a long time ago. He was kinder then. I'd like it finished, and I'd like it to be "
        "somebody who doesn't remember that.\n\nHe holds the great chapel at the heart of Tyr's Hand, and he doesn't "
        "fight alone. Go in with friends, and watch for the fire when he calls it down.",
        "Then Varenne's gone, and Tyr's Hand will be quieter for a while.\n\nI'll pray for the man he was."),
    "ple_a_word_with_the_order": V(
        "Carry Dawnbringer's Letter to Flamekeeper Rory Callahan in the Order's quarter of the Bulwark.",
        "I've heard about the Order of the Pale Flame. Scarlets who walked out of the Crusade, and kill only the "
        "mindless dead. Some of the Dawn don't trust them. I would like to.\n\nTheir Flamekeeper, Rory Callahan, "
        "knows the Crusade from the inside. I'd like to talk to him about Tyr's Hand, and about Hearthglen.\n\n"
        "They're camped inside the Bulwark now, at the far west of the Plaguelands. It's a long way, so fly. Give it "
        "to Rory and tell him I'd like an answer, not a sermon.",
        "The Argent Dawn wants to talk. Now there's something I didn't think I'd live to see.\n\nTell him yes. Tell "
        "him I'll ride to Light's Hope myself, and that I'm sorry it took the end of the world to get us in one "
        "room."),

    # ---------------------------------------------------------------- Archmage Lysander Hale, the chapel
    "ple_marrow_of_the_scar": V(
        "Take Scar Marrow from the Scar Bone Constructs in the Pestilent Scar.",
        "I break down the Scourgestones that come to the chapel, and lately I've found something new in them. It's "
        "coming from the Pestilent Scar, where the Scourge is building with bone.\n\nThe Scar Bone Constructs that "
        "walk there are full of a cold grey marrow. I'd like some of it, carefully.\n\nThe Scar's north-west of the "
        "chapel, a long gash in the ground full of bones. Cut the marrow from the big bones in their legs, and "
        "don't hold it any longer than you have to.",
        "It's cold, isn't it? It's colder than ice and it doesn't melt.\n\nSomething in the Scar is drinking the "
        "warmth out of everything, and now I know what's doing it."),
    "ple_the_bone_colossus": V(
        "Kill the Bone Colossus and the Scar Bone Constructs that guard it in the Pestilent Scar.",
        "At the bottom of the Pestilent Scar the Scourge is building a giant out of the bones of everyone who died "
        "in the east. I call it the Bone Colossus. That's what the marrow was for.\n\nThe Scar Bone Constructs "
        "guard it while it grows. I want it pulled down before it's finished.\n\nIt stands in the deepest part of "
        "the Scar. It's slow, and it's very, very strong. Kill the constructs first, then take it with every friend "
        "you can find.",
        "It's really down? Then the Scar is just a hole in the ground again.\n\nThe Dawn owes you, and so does "
        "everyone who'd have been built into it."),

    # ---------------------------------------------------------------- Lightwarden Ysolde Carrow, the chapel
    "ple_darrowshires_dead": V(
        "Set the Darrowshire Spirits free in Darrowshire.",
        "I'm Ysolde, and I keep the chapel's prayers for the dead, all of them, because nobody else in the east "
        "will.\n\nDarrowshire's dead never got any prayers. The Darrowshire Spirits are still fighting the battle "
        "that killed them, every night, over and over, and they don't know it's over.\n\nDarrowshire's far to the "
        "west, south of the old tower. The spirits fight in the town square and on the road in. They'll take you "
        "for the enemy, so be ready. Set them free.",
        "I felt them go. It's quieter in the chapel tonight.\n\nThe newcomers ask me why we pray for the dead here. "
        "I tell them it's because nobody else will."),
    "ple_the_pestilent_scar": V(
        "Look into the Pestilent Scar from its edge, and come straight back.",
        "I won't send anyone into a place I haven't heard described, and nobody's come back from the Pestilent "
        "Scar with a straight story. One man said fire, one said ice, one wouldn't say anything.\n\nWalk to its edge "
        "and look. Don't go down.\n\nIt's north-west of the chapel, past the lake. You'll smell it before you see it. "
        "Stand at the edge and look, and then come straight back here.",
        "Bones, all the way down? Light have mercy on them.\n\nI'll tell the Archmage. He's been waiting for someone "
        "to say it out loud."),
    "ple_the_shadowhunters": V(
        "Kill Mossflayer Shadowhunters at Zul'Mashar.",
        "Somebody's been hexing the chapel. I've found little bundles of feathers and teeth under the pews. The "
        "only ones in the east who'd do that are the Mossflayer Shadowhunters of Zul'Mashar.\n\nI'd like them dead "
        "before they get bolder. The dead don't cross this ground, but the living do.\n\nZul'Mashar's in the far "
        "north-east, past Quel'Lithien Lodge. The shadowhunters keep to the temple steps. Their hexes are nasty, so "
        "get a priest to look at you when you're back.",
        "There was nothing under the pews this morning. Thank the Light.\n\nI found something odd on one of the "
        "bundles, and I'd like a closer look."),
    "ple_hex_fetishes": V(
        "Take Mossflayer Hex Fetishes from the Mossflayer Shadowhunters at Zul'Mashar.",
        "The hex bundles under the pews were tied round scraps of the chapel's own laundry. Somebody inside these "
        "walls has been stealing from us for the Mossflayers.\n\nThe Mossflayer Shadowhunters still carry their "
        "fetishes. I want to see whose cloth is in them.\n\nThey carry them on their belts at Zul'Mashar. Bring "
        "them back unopened. I'll know the cloth when I see it.",
        "That's the infirmary's linen, every scrap.\n\nSomebody's been selling them our sheets. I'll find out who, "
        "and then we'll have a long talk."),
    "ple_the_bones_of_the_east": V(
        "Kill Bone Miners and Scourge Pit Guards in the Bone Mines, under the Pestilent Scar.",
        "I pray for every dead soul in the east, and I've found out where some of them went. The Scourge has dug "
        "a mine under the Pestilent Scar. The Bone Miners in it are digging up the east's dead to build its "
        "constructs, and the Scourge Pit Guards keep them at it.\n\nI want the digging stopped.\n\nThe mine's in the "
        "hill under the Scar. Every gallery's deeper than the last, so it's a long walk down. The pit guards will "
        "keep you out if they can.",
        "Those were people once, the bones they were digging up. Somebody's grandfather, somebody's child.\n\nI'll "
        "say the prayer for all of them at once. It's not enough, but it's what I've got. Faelis wants a word with "
        "you about whoever's running the place."),

    # ---------------------------------------------------------------- Sergeant Marisol Reyes, the infirmary
    "ple_troll_medicine": V(
        "Take Mossflayer Herb Pouches from the Mossflayer Scouts round Zul'Mashar.",
        "I'm Marisol, and I run the infirmary. I've got more patients than beds. If you're bleeding, sit down. If "
        "you're not, listen.\n\nThe Mossflayer trolls heal faster than anybody else in the Plaguelands. Their "
        "scouts carry herb pouches, and I want to know what's in them. I'm not too proud to learn from a troll.\n\n"
        "Zul'Mashar's in the far north-east. The Mossflayer Scouts range out from the temple in pairs. Bring me the "
        "pouches closed, because I want to see how they pack them.",
        "Kingsblood, and something I don't know, and a lot of salt.\n\nI was a paramedic in Monterrey, back home. "
        "Half of what I know I learned from grandmothers, so I'm not surprised the trolls know a thing or two."),
    "ple_mossflayer_raiders": V(
        "Kill Mossflayer Warriors and Mossflayer Scouts round Zul'Mashar.",
        "My wagons bring the wounded in from the road, and the Mossflayers have started raiding them. The "
        "Mossflayer Warriors hit the wagons from the trees, and the Mossflayer Scouts pick off whoever runs.\n\nI "
        "want the road safe for people who are already hurt.\n\nThey come down from Zul'Mashar to the north road. Go "
        "up there and hit them at home. They're fast and they're angry, so don't fight more than you can handle.",
        "No raids yesterday, and none today. My wounded came in alive.\n\nThere's one more of them I'd like to see "
        "gone, and he's the one giving the orders."),
    "ple_zulmashar_the_last": V(
        "Kill Zul'Mashar the Last at the top of the temple at Zul'Mashar.",
        "The Mossflayers follow a warlord who named himself after their city. Zul'Mashar the Last says he's the "
        "last of the old Amani blood, and he's sworn to drive everyone out of the east who isn't a troll.\n\nThe "
        "raids won't stop while he's giving the orders.\n\nHe holds the top of the temple at Zul'Mashar. He's big, "
        "and he hits like a falling tree. Take friends, and bring bandages, because you'll need them.",
        "Then it's over. My wagons can run every day now.\n\nI took an oath to look after the sick and the hurt. I "
        "never thought I'd be sending people to kill a warlord to do it."),
    "ple_the_medics_network": V(
        "Carry Marisol's Notes to Marcus Oyelaran at Talonbranch Glade in North Felwood.",
        "The medics who came through keep in touch across the sea as best we can. Letters, mostly, carried by "
        "whoever's going that way.\n\nI've written up what the Mossflayer herbs do. There's a paramedic at "
        "Talonbranch Glade in Felwood, Marcus Oyelaran, treating burns up there that sound exactly like the ones "
        "I'm treating here.\n\nTake the zeppelin from Tirisfal to Orgrimmar, then go north through Ashenvale to "
        "Felwood and up to Talonbranch at the top. Marcus will be the one with his sleeves rolled up. Don't let the "
        "notes get wet.",
        "Marisol from Monterrey? We trained on the same course, years ago, back home in a hotel conference room in "
        "Houston.\n\nThis is going to save people up here. Tell her I owe her a coffee, if anyone ever finds coffee "
        "again."),

    # ---------------------------------------------------------------- Ranger Faelis Dawnreach, the chapel
    "ple_the_restless_lodge": V(
        "Lay the Restless Lodge Rangers to rest at Quel'Lithien Lodge.",
        "I'm Faelis, and I served at Quel'Lithien Lodge, in the north, where my people kept watch on Lordaeron's "
        "border. The lodge fell with everything else. Everyone I served with is still there, and none of them are "
        "resting.\n\nThe Restless Lodge Rangers still walk their posts. I knew every one of them. I'm asking you to "
        "let them rest.\n\nThe lodge is in the north, past the lake. They'll be on the walls and in the trees, where "
        "they always stood. They still shoot straight, so keep moving.",
        "They're resting now, all of them. I could hear them stop.\n\nThey each carried a token, a silver leaf. I'd "
        "like them back, if you'd go once more."),
    "ple_the_silver_leaves": V(
        "Take Quel'Lithien Ranger's Tokens from the Restless Lodge Rangers.",
        "Every ranger of Quel'Lithien carried a silver leaf on a green cord, a token from Quel'Thalas. I'd like to "
        "send them home, so that somebody there knows their names.\n\nThe Restless Lodge Rangers still wear them "
        "round their necks. Bring back what you find. Not every one of them will still have theirs, and I'm sorry "
        "for that.",
        "That's Seren's, and Calanor's, and this one was Ilyeth's, who always sang off key.\n\nI'll send these "
        "north. The lodge's lord is still out there, though, and he won't rest until someone makes him."),
    "ple_ranger_lord_saelith": V(
        "Kill Ranger-Lord Saelith at the inner gate of Quel'Lithien Lodge.",
        "Ranger-Lord Saelith commanded Quel'Lithien Lodge. He was my captain and my friend, and he died holding "
        "the gate. He still holds it, and he still kills anyone who comes through.\n\nI can't do it myself. I've "
        "stood at that gate with an arrow on the string and I couldn't loose it. I'm asking you.\n\nHe stands at the "
        "lodge's inner gate, where he fell. He's fast and he doesn't miss. Go with friends, and close the distance "
        "quickly.",
        "Then the lodge is quiet, and he's free.\n\nHe taught me to shoot. He taught half the lodge. Thank you for "
        "doing what I couldn't."),
    "ple_the_overseer": V(
        "Kill Overseer Marrowgrim in the marrow pit at the bottom of the Bone Mines.",
        "I watched the Bone Mines from the ridge for three nights, and I've seen who runs them. Overseer "
        "Marrowgrim sits in the pit at the bottom with a meat hook and a cart, and nothing leaves that mine that "
        "he hasn't weighed.\n\nI want him dead before the Scourge has bone enough for another colossus.\n\nHe's in "
        "the marrow pit at the end of the deepest gallery. He's big and he's slow until he isn't, so don't stand "
        "where that hook can reach you. And watch out for the cart.",
        "The Scar's quieter already, and the bats have stopped circling it.\n\nAt the lodge we used to say you "
        "don't kill the wolf, you kill whoever keeps it fed. Somebody's still keeping him fed, though."),
    "ple_the_ossifier": V(
        "Kill the Ossifier in his workshop off the middle gallery of the Bone Mines.",
        "I've found a workshop off the middle of the Bone Mines, and Marrowgrim's tallies say everything the mine "
        "digs up goes there first. The Ossifier is a necromancer, and he's the one who turns the east's dead into "
        "the Scourge's constructs.\n\nClose his workshop.\n\nIt's off the middle gallery, up a short passage. He'll "
        "be wearing bone armour, and it's thick, so be patient with it. Break that first, then break him.",
        "That's the end of the Bone Mines, and the end of the constructs coming out of them.\n\nI couldn't save "
        "anyone at the lodge. I'm glad I could do something for the ones who were already gone."),

    # ---------------------------------------------------------------- Innkeeper Jessa Moonfield, the hospital
    "ple_lamp_oil": V(
        "Take Rendered Bear Fat from the Plague-Rotted Bears in the woods round Light's Hope.",
        "I'm Jessa, and I keep the beds and the lamps. The lamps stay lit all night, because the dead don't like "
        "the light, and since Crown Guard moved in I've twice as many lamps and the same amount of oil.\n\nThe "
        "Plague-Rotted Bears carry fat under the rot that renders down clean. I've tried it.\n\nThey wander the "
        "woods all round the chapel. Cut the fat from the back, where the rot's thinnest. It won't smell nice, and "
        "I'm sorry about that.",
        "That'll keep the lamps burning for a fortnight.\n\nThe newcomers say they're used to lights that never go "
        "out. I'd love to see that, one day."),

    # ---------------------------------------------------------------- Pamela Redpath, Darrowshire (a ghost, and a child)
    "ple_pamelas_doll": V(
        "Find Pamela's Doll on the Darrowshire Ghouls in Darrowshire.",
        "Hello, are you here to see Daddy? He's out at the fight, but he'll be back soon.\n\nI'm Pamela, and I've lost Dolly, and I've looked everywhere. The Darrowshire Ghouls took her, they did! I saw one carry her off. "
        "They're all over the town and they won't give her back.\n\nShe's got a blue dress and one button eye. "
        "Will you find her for me, please?",
        "That's Dolly, you found her! She's all muddy, but that's all right.\n\nDaddy's going to be so happy when he "
        "gets home. He's been gone ever so long."),
    "ple_a_letter_for_auntie": V(
        "Carry Pamela's Letter to Chaplain Odile Marchand at the Order's chapel in the Bulwark.",
        "I wrote a letter to Auntie Marlene! She lives out west, near the big town. I haven't heard from her in "
        "ever so long.\n\nA man came through and said there are kind people in the west who keep a book with "
        "everybody's names in it. If anyone knows where Auntie is, it's them.\n\nThe lady with the book is in the "
        "big wall at the end of the road, where the road goes out of the Plaguelands. You'll be ever so careful "
        "with it, won't you?",
        "Oh, this is from a child. Darrowshire, she says.\n\nMarlene Redpath's in my book. She died in Andorhal, with "
        "everyone else. I'll write back to Pamela, and I'll tell her that her auntie loved her. That part's true."),
    "ple_where_daddy_is": V(
        "Set Captain Redpath's Shade free on the battlefield south of Darrowshire.",
        "Daddy's at the big fight, south of the houses. He's been there ever so long. I can see the flags from the "
        "end of the road, but I'm not allowed to go.\n\nHe's Captain Joseph Redpath, and he's very brave. Everybody "
        "says so.\n\nWill you go and find him? Tell him I've been good, and that I've got Dolly back, and that I'm "
        "waiting. Tell him he can come home now.",
        "You saw him? Is he coming?\n\nHe's here, I can see him, and he's smiling. Thank you, thank you. We're going "
        "home now."),

    # ---------------------------------------------------------------- in from outside
    "ple_hammerfalls_answer": V(
        "Carry Gath'rok's Answer to Commander Eligor Dawnbringer at Light's Hope Chapel.",
        "Everything that crosses Arathi crosses in front of me. Lately that's been the Argent Dawn's carts heading "
        "east, and the Dawn has asked Hammerfall for steel.\n\nI've written my answer. I want it carried by "
        "somebody who'll fight their way there, because a messenger who can't won't arrive.\n\nGo north to the "
        "Plaguelands and take the road east as far as it runs. Light's Hope is at the end of it, behind its own "
        "gate. Tell the commander Hammerfall keeps its word, and don't stop to fight anything you can walk past.",
        "Hammerfall's answer, and it's yes. The Overlord doesn't waste words, does he?\n\nWe don't ask the newcomers "
        "where they came from here, and we don't ask anyone else either. We ask whether they'll stand on the wall "
        "tonight, so will you?"),
})
