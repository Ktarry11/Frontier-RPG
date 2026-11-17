"""Brill and the Tirisfal Glades in the plain voice (17 Nov 2026). Here D is the speech and A is the short parting
line. The old text leaned on one-word lines, dashes, capitals for stress and bracketed stage directions. The people
and their stories stay; they just talk plainly now. Same directions. Built up in parts below."""

VOICE = {
    "brl_wolves": (
        "You'll forgive me if I don't stand. I'm Deathguard Rennick, and this gate is mine from dusk until whenever somebody remembers to relieve me.\n\nThe Bleak Worgs have been coming up the Deathknell road after dark. They aren't at us yet. They're at the edges, the way a thing goes when it's working out whether we're worth the trouble. Nobody in Brill has been bitten. The living would call that luck. I've stood at a gate long enough to call it a question being asked.\n\nGo down into Nightmare Vale and answer it. Thin the pack, and leave enough of a mess that the rest of them draw the right conclusion.",
        None,
        "That's the answer I wanted them to have.\n\nBrill sleeps lighter than it admits, friend. Take something out of the crate, because nobody's using what's in it.",
    ),
    "brl_nightmare": (
        "One more thing, since you came back with your arms attached.\n\nNobody has walked the lower road through Nightmare Vale since the worgs settled in. I've got three patrol rosters on this post and every one of them says the same word about what's down there, and the word is something. You can't set a watch against something. You can't tell a frightened farmer anything useful about something.\n\nWalk it for me, end to end, the whole length, and look properly at the bottom of it. Then come back and give me a noun.",
        "Go south-west of the Cold Hearth road, past the Deathknell gate, where the road goes into the trees. Don't take your time about it.",
        "So it's quiet, and you're certain.\n\nI like quiet less than you'd think. Quiet is what a place sounds like when whatever lives there has already seen you and decided there's no hurry.",
    ),
    "brl_glades": (
        "Stop there, and look. Do you see that, out past the posts, drifting about in the long grass?\n\nThose are Wretched Zombies out of the western glades. They're slow, they're stupid, and I'll say it plain because the Deathguard won't: they mean nothing by it. There's no malice left in one of those. They just wander, and lately they've been wandering at my gate.\n\nI've got a quota of corpses I'm willing to step over on my way to this post, and it's been exceeded. Go and put them down properly, which is more mercy than they'd get from anyone else on this road.",
        None,
        None,
    ),
    "brl_news_landing": (
        "I'm Wexley, town crier for Brill, and the first man in this town to know anything. I hold that position by effort, not by luck.\n\nWhich is why it galls me to be standing here repeating a rumour I can't confirm. They're saying the zeppelin tower east of here, out at the Landing, is open and taking passengers. Goblins, ropes, the whole swaying business of it. If that's true, it's the biggest thing to happen to this town since the Dark Lady took the Undercity, and I won't be the last man in Brill to say so out loud.\n\nGo east and look at it with your own eyes. I won't cry a thing I haven't had confirmed.",
        None,
        "So it's real, and open for custom!\n\nI'll cry it from the steps within the hour, and I'll mention that I had it confirmed before anyone. Thank you, I mean it. A crier is only ever as good as the man he sent to check.",
    ),
    "brl_news_ruins": (
        "The Landing is a story about commerce. This one is a story about us, and I'd rather have it right.\n\nSouth of the tower are the Ruins of Lordaeron, the old capital, what's left of it, and the gate down into the Undercity. Every week somebody comes up that road with a tale: that the throne room's been cleared, that there are lights in the upper halls, that something's moved in where the Menethil line used to sit.\n\nI need the approach walked by someone who'll tell me what they actually saw rather than what makes a better evening at the inn. Go and see who's still home.",
        "Go south of the Landing, along the road the Dark Lady took. Don't linger, because the ghosts up there remember being important.",
        "That matches two of the four versions I've been told, which is about as close to truth as this town gets.\n\nI'll cry the careful version. People think a crier's job is noise. It's mostly deciding what not to say.",
    ),
    "brl_grael_pumpkins": (
        "Keep your voice down. The Apothecary's just through there, and he doesn't like to be interrupted by errands he considers beneath the work.\n\nI'm Grael, the assistant, which in this building means I fetch. What I need fetched are the pumpkins out of the Solliden fields, swollen things, grey-green, gone soft at the shoulder. They ferment into the finest reagent base we have, and nothing else in Tirisfal does it half as well.\n\nThe Grain Threshers are growing them, and the Grain Threshers hit back, which is precisely why I'm standing here asking you instead of walking out there myself. Bring them uncracked, please. I'm very particular about cracks.",
        "Go out the west gate to the Solliden Farmstead in the western glades. The threshers in the fields carry them. Bring them uncracked, because I'll know.",
        "Oh, those are lovely. There isn't a split in them.\n\nDon't tell the Apothecary how pleased I am. He thinks enthusiasm is a symptom.",
    ),
    "brl_grael_pearls": (
        "Here's another one, if you've got the stomach for the smell of the bay.\n\nThe Vile Fin murlocs out on the Whispering Shore wear little salt-pearls. The oracles do, specifically, the ones that stand at the back and make the noise. Ground fine, they settle a plague draught that would otherwise take the lining out of a person. We use a great deal of it.\n\nI've no idea what the murlocs want them for. I asked once, in the way you ask a murloc things, and I came away wet and no wiser. Whatever it means to them, they can spare some.",
        "Go north-west, where the bay meets the dead marsh, and find the little oracles. Don't scratch the pearls.",
        "These are perfect. Look at the lustre on that, and you can see why they bother.\n\nI do sometimes wonder whether we're taking something from them that matters. Then I grind it up, and the wondering passes.",
    ),
    "brl_grael_iceshard": (
        "This is the last errand, and the cold one, so I've saved it for someone who looked like they could take a walk in bad weather.\n\nBrightwater Lake sheds shards of black ice all year. Summer or winter makes no difference, which should tell you something about that water. The shades along the shore pick them up and carry them about like keepsakes. I've watched one hold a shard for an hour and do nothing with it at all.\n\nWe use them for cold-fixing, which keeps a reagent from turning while it sits. Bring me what the shades and the drowned are carrying. And wear gloves. I'm not being delicate, that ice takes fingers.",
        "Go to Brightwater Lake in eastern Tirisfal. The shades and the drowned carry fragments. Wear your gloves.",
        "They're still cold. They always are, hours later, no matter what you wrap them in.\n\nThank you. Go and stand near the fire a while, because you've gone the colour of the lake.",
    ),
    "brl_hollis_robbers": (
        "Thirty years I've dug in this ground. I dug for the living when it was the living we buried, and I dig for whatever we are now, and I'll tell you the one thing both have in common: a grave is a promise. You put a person in the earth and the earth keeps them.\n\nSomebody's been breaking that promise up at Garren's Haunt. Rot Hide gnolls are working the old plots as graverobbers, and doing it badly. They take what's valuable and leave the rest lying out in the wrong arrangement. It isn't scattered, it's arranged, and I don't like that at all.\n\nAnd here's the part that has me in a temper: they're using my shovels, stolen out of this very yard. Put them in the ground with them.",
        "They're up at Garren's Haunt. They use shovels, and I recognise the shovels, because they're mine.",
        "And I've got my shovels back, chipped, but back.\n\nYou'd think a man in my condition would have made his peace with bodies being moved about. It turns out that's precisely why I haven't.",
    ),
    "brl_hollis_relics": (
        "Now the other half of it, and this is the half that actually matters to me.\n\nWhatever those gnolls lifted is still out there, and the crypt wights in the Agamand vault have been at the same work for longer. Rings, seals, little carved things an Agamand was buried holding, because somebody who loved them thought they ought to have it.\n\nI don't want it sold and I don't want it kept. I want it back in the ground. I've dug for this family since before the plague, and I'd like the ledger to balance before I stop. Bring me what you find, and bring all of it. I'll know the shape of a gap.",
        None,
        "That's every piece, then. I did wonder.\n\nI'll put these back tonight, properly, with the right names over them. It won't matter to the Agamands. It matters to the ground, and it matters to me, and that'll do.",
    ),
    "brl_meryl_orders": (
        "You aren't from the Deathguard, which is what I needed. I'll say this once and quietly.\n\nMy name is Meryl Ashdown, and my brother is in the Scarlet Crusade. He marched off while he was still breathing, and I stopped being able to follow it after that. I don't know if he's alive. I don't know if he's still himself. You hear what the Crusade does to a man's thinking, and he was never the steadiest of us.\n\nThe recruits at the Crusader Outpost carry their orders on them: convert rosters, postings, names. Somewhere in that paper is whether he's still listed. I'm not going to ask how you get them, and I'd rather you didn't tell me. But if you meet a thin man with our mother's jaw, please spare him.",
        "Go to the Crusader Outpost, west of the Solliden farms. Please, don't hurt him if you meet him.",
        "She reads each sheet twice before she sets it down.\n\nHe isn't here. He isn't listed, he isn't struck off, he isn't anywhere in this. That means nothing, and I'll be honest with you, nothing is better than what I was braced for.\n\nThank you. You're the first person in three years to come back to me with an answer instead of a kindness.",
    ),
    "brl_nettles_crows": (
        "Do you see them bats, out over the glades, the big grey ones?\n\nThey're the crows. They're the same crows that took my barley every autumn for forty years, and don't you start. I know what people in town say about Old Nettles and his crows. I know what they turned into, and I know what I turned into, and I notice nobody wants to discuss the second one.\n\nNothing grows in that field now. Nothing has grown there since before the plague, and I'm aware of that. But a man either keeps the pact he made with his land or he doesn't, and I'm not having the principle of the thing decided by a bat. Go and see them off.",
        "They're out in the glades west of town, the big grey ones. The Deathguard calls them mangy duskbats. They've had my crop and my patience.",
        "Hah, that's them told!\n\nThe field's still dead, and I'm still dead. But that's a proper field with a proper crop of nothing in it, and it's mine, and the birds can keep off it.",
    ),
    "brl_pruit_straw": (
        "Careful of the posts. I've only just got that one standing straight.\n\nI tend the scarecrows on Brill's plots. I've done it since there were crops worth guarding, and I've kept at it since there weren't. Somebody has to. If a field has a scarecrow, somebody still means something by it.\n\nThe Rotting Dead come in off the glades and knock them flat, and that I could live with. What I can't live with is what they do after. They lean on the posts, and they stay there. When you come out in the morning there's a shape up on the frame that isn't straw and isn't mine, and I've got to take it down and decide what to do with it. I'd like that to stop.",
        "They're out in the plots. Don't bring them back here, because I'll make do with straw.",
        None,
    ),
    "brl_ohmsted_toll": (
        "The bell goes once a day, at dusk. It's one stroke, for everyone Brightwater Lake has kept.\n\nIt isn't a ceremony, and the Apothecary has told me more than once that it isn't useful, and he's right. It's a habit I had when I was breathing and I've still got it now, and I've lost enough else that I'd rather not examine that one too closely.\n\nHere's the trouble. For the last month or so, when I ring it, the lake rings back. The Drowned Wretches come up out of the shallows and make a sound that isn't an echo, and they keep making it after I've stopped. I'd like them quiet. I'd like to be able to ring for them without them answering.",
        None,
        "He listens for a long moment, head tilted toward the water.\n\nThere's nothing now, just the bell, and then the bell stopping.\n\nI'll ring for them tomorrow as well. It's only right. But I'd rather do the remembering on my own.",
    ),
    "brl_ohmsted_shades": (
        "The wretches in the water were one thing. The shades along the shore are another, and I've been putting off asking.\n\nWhen the bell goes, they weep. It isn't an echo of it, it's their own sound, starting after mine and going on long after. I've heard a great many terrible things since I stopped breathing, and that's the worst of them, because it's almost grief and it isn't quite.\n\nI don't know what's left in a shade. Perhaps nothing, and it's only the shape of mourning with no one inside it. Either way I'd like them stilled. If anyone's in there, then they've been standing on a cold shore crying at a bell for years, and that's reason enough on its own.",
        "It's the same lake. Look along the shore, not in it. They're rather high-handed about it.",
        "They're all still now.\n\nI'll keep ringing. Somebody has to, and now the only thing that answers is the water, which is how it ought to be.",
    ),
    "brl_joss_home": (
        "You'll have to be patient with me. I'm new to this, the waking up, I mean. It's weeks, not years, and most of it won't sit still in my head.\n\nHere's what I have. A stable with a bad door. A paddock gone over with thistle. A farmhouse, and a woman in it who made bread on a Thursday, and I can smell that more clearly than I can remember her face, which seems a poor trade.\n\nBalnir, I think it was called, south of the east road. I can't go. I've tried twice and turned back both times, and I'd rather not explain why. Walk the place for me and tell me what's still standing. I'd like to know whether I'm remembering a home or inventing one.",
        None,
        "The stable door. You're sure about the stable door, hanging off the one hinge, the bottom one?\n\nThen it was real. I wasn't sure, and nobody could tell me, and now I am.\n\nI'm not going to go and look. I want to leave it where you put it, standing, with the door wrong. Thank you for that.",
    ),
    "brl_ilvessa_cargo": (
        "Finally, somebody competent-looking. I'm Ilvessa, and I keep the stall at the end, the one with the good lacquer and no customers.\n\nMy shipment came down from the Undercity on the zeppelin and never reached this square. Scavengers took it on the road, picked the crates open, and scattered what they didn't fancy. That much is only irritating. What's dangerous is that they got away with it, because the next shipment comes in on the same schedule down the same road, and scavengers can count.\n\nGet my crates back. I don't particularly need what's in them. I need it to have cost somebody something, before the whole road decides my stall is a seasonal harvest.",
        "Go out the east gate and north, to the coast of the eastern glades. That's where the ragged scavengers den with what they take off the road. They steal anything that glints.",
        "Half the lacquerware is cracked and one of the bolts of cloth has been used as bedding, which is lovely.\n\nBut it came back, and they know it came back. That's the part the next shipment is paying for. Take your cut.",
    ),
    "wtv_wolves": (
        "I'm Corvin Ashe. I walk the Vale's edge for the Deathguard, which means I'm the line between whatever is in those trees and the road up to Brill. I'm in Deathknell for supplies and for help, and you look like help.\n\nThe Bleak Worgs are getting bold. A year ago they kept to the deep Vale, and you'd hear them and that was all. Now they come to the treeline at dusk and stand there, looking up the road, working out the slope.\n\nThat's what worries me, the measuring more than the hunger. Thin the pack while the road is still too much trouble for them. Aim for the grey ones, because the grey ones are doing the thinking.",
        "They hunt at dusk. Aim for the grey ones, because they lead.",
        "There were grey ones among them? That's a season's worth of learning gone out of that pack.\n\nThey'll breed it back. They always do. But not before the frost, and I'll take the winter.",
    ),
    "wtv_crawlers": (
        "When you get out to the Vale, mind where you put your feet. I mean it. Stand still a moment out there and listen to the loam.\n\nThat sound is nightcrawlers. They burrow all through the near end of the Vale and come up under whatever walks over them, which is a perfectly good way to live if you're a worm and an appalling one if you're a ranger.\n\nI've lost two boots to them. I'd like it known that I've lost considerably more dignity than boots, because losing a boot in soft ground isn't a quiet or graceful event. Clear the young ones out of the loam before they're big enough to take the leg that's in the boot.",
        "They're under the roots. You'll feel them before you see them, so get them before they grow.",
        "That's much better. I'll walk this stretch without doing the little hop I've been doing.\n\nDon't tell the Brill garrison about the hop.",
    ),
    "wtv_needler": (
        "There's a duskbat above the Vale road that the locals have named, and things only get named around here when killing them has become a topic.\n\nHe's Ressan the Needler, a big old brute with teeth like his name, and he comes in low along the road at head height, which for a bat is a decision rather than an accident. He's got a flock that moves when he moves. I've watched him put three travellers on the ground in a month, and he didn't feed on one of them.\n\nClear the flock off him first, or they'll peel you while you're busy. Then put the Needler down. I'll be back at the treeline by the time you're there, with my boots on.",
        None,
        "I heard it stop. The whole Vale heard it stop.\n\nThe road's walkable at dusk again. That's the first sentence of that kind I've been able to say this year.",
    ),
    "wt_manor_reapers": (
        "I'm Watcher Pell. I've kept the Cold Hearth gate for a year, and they've called me back to Brill to tell them what I've seen there. In that year the reapers haven't stopped once.\n\nThey come up out of the manor cellars with scythes. They don't shamble, they work. They come up in a line, they spread along the hedge, and they cut, and there's been nothing growing in that garden to cut since before I was posted there. Then they go back down, and then they come up again.\n\nI've stopped asking what they think they're harvesting. Clear the ones at the door, and mind the blades. Somebody has kept those sharp, and it isn't the gardener.",
        None,
        "It's quiet at the hedge. That's an hour of quiet, maybe two.\n\nYou'll think me grim for saying it, but an hour is a great deal when you've had none.",
    ),
    "wt_manor_dead": (
        "Now that you've seen the hedge, look past it at the grounds, because the reapers aren't the half of it.\n\nZombies come in off the glades and the rotted ones come up through the lawn, and they all go the same way, toward the hall. They don't come toward me or toward the road. They go toward the house, every time, as if the place were calling the staff in.\n\nI've a horrible suspicion it is. Clear the gardens for me. I want to see how fast they fill up again, because the answer tells me what I'm actually guarding.",
        "Clear the gardens, the zombies and the rotting dead both.",
        "It's empty, for now.\n\nI'll time it. If it's hours, the manor's drawing them. If it's days, it's just the glades. I'd rather know which before I've got to write it in a report somebody acts on.",
    ),
    "wt_aldous": (
        "Now for the hall itself, and the thing at the hearth in it.\n\nHis name is Reaper-Lord Aldous. He's taller than the rest, with a scythe for an arm these days, and the others answer to him. I've watched the line along the hedge dress itself when he came to the door. He thinks the manor is his and he thinks the staff are still his, and in the most literal sense available he's correct, which is the problem.\n\nHis reapers will put themselves between you and him. They always do. Take them off him first, then take the hall back, and then I'll have guarded this gate for a year and have something to show for it.",
        "He's inside the hall, at the hearth. His reapers will guard him, so take them first.",
        "Pell looks at the manor door for a while before she answers.\n\nI stood at that gate a whole year.\n\nI'll go back out to the gate a while longer, because the cellars want watching yet. But the hall is a house now instead of a household, and I'll take that.",
    ),
    "wts_puddlejumpers": (
        "Don't laugh at me. I can see you building up to it, and I'd ask you to hold it in until I've finished.\n\nI'm Quillon, a fisher on the Whispering Shore. The Vile Fins have my boat. They've also got my nets, which they're wearing, on their heads. The small ones patrol the strand in my nets like a procession of the very worst magistrates you've ever seen.\n\nHere's why it isn't funny. The strand is how this village eats. While they hold it we don't fish, and the inn starts asking the Apothecary what's edible, and you don't want to be downwind of the answer. Clear the little ones off the sand.",
        "The strand is just south-east of my door, and you can smell it from here. Go after the little ones, and bring back my dignity if you find it.",
        "The sand's clear, and I can get a line out tomorrow.\n\nAnd no, you can't have a net back as a souvenir. Those are going back on a pole where they belong.",
    ),
    "wts_pearls": (
        "The little ones were the front rank. The ones at the back, the ones that stand still and make the noise, those are the oracles, and they're the reason any of this is organised.\n\nThey wear salt-pearls, strung at the throat, and they use them to talk to the tide. I've fished this shore for thirty years, and I'm telling you the tide answers them. For the last few months what it's been saying has been wrong: wrong hours, wrong height, a slack water that turns when it shouldn't.\n\nTake the pearls off them. Either I'm an old fool and nothing changes, or I'm right and the water goes back to keeping time.",
        None,
        "He turns one over, holding it up against the light off the water.\n\nThe tide turned at the right hour this morning, for the first time since the spring.\n\nI'd rather have been the old fool, if I'm honest. An old fool's shore is a safer place to work.",
    ),
    "wts_gillrot": (
        "Old Gillrot is the one with my boat.\n\nHe sits up on the big rock at the north end with a staff he's made out of a mast, and I know whose mast it was, and so does everyone who drinks in Brill. The other oracles keep him standing. I've seen him take a harpoon and I've seen them put him back together, so if you go at him straight you'll be there till the tide comes in.\n\nThin the oracles first, and then go for Gillrot. And listen, I want the boat, but I'll be straight with you, I want the mast more. A man ought to be buried with his own ship, not have it waved about by a murloc.",
        "Go back to the strand, south-east of my door. He sits on the biggest rock, at its far end. His oracles heal him, so thin them first, then go for Gillrot.",
        "That's Harl's mast. Twenty years he had that boat, and he went down with it in a squall, and his widow is still in Brill, and she's had to look at that rock every day since.\n\nI'll take it to her this evening. The boat can wait. Thank you, truly.",
    ),
    "wto_converts": (
        "Get down behind the thorns, and don't look over the top of them. Look through them.\n\nI'm Dessa Vane, scouting for the Deathguard. That's the Crusader Outpost, and those are this week's converts. New ones come up that road every week. They arrive wide-eyed and badly armed and absolutely certain, and that last part is what makes them dangerous rather than sad.\n\nI know what you're about to feel when you get close enough to see their faces. Feel it afterwards. A convert who's been here a month is an Initiate, and an Initiate marches on Brill. Thin them while they're still the easier problem.",
        None,
        None,
    ),
    "wto_initiates": (
        "Now the rank behind them, and I'll be plain: this part is harder, and you should treat it that way.\n\nThe Initiates are trained, properly armed, and devout in the settled way rather than the shouting way. They carry the banners, they hold the outpost's shape, and when the Crusade decides Brill is a problem worth solving, these are the ones who'll be told to solve it.\n\nDon't take more than two at once. I'm not being careful with your feelings. I've watched a Deathguard try three, and I had to go back at dusk for what was left of him.",
        None,
        "The banners are down, which is what I wanted.\n\nThat outpost's shape comes from those men. Without them it's a camp of frightened recruits with a view of our road, and a frightened recruit is a much slower thing to worry about.",
    ),
    "wto_korgal": (
        "And there he is, in the centre of the camp under the standard. That's Meven Korgal.\n\nHe's a veteran. He was a veteran before he was a zealot, which is the dangerous order to do it in. He can hold a line, he can site a camp, and he prays like a man reading a map. Everything in that outpost that works, works because he's standing in it.\n\nHis recruits will rally to him. They adore him, and you'll have to go through that first. But I've watched this camp for a season, and I'll tell you what I've concluded: take Korgal and the rest is tents.",
        None,
        "Dessa watches the camp through the thorns for a long moment.\n\nThey're arguing, three of them by the standard, and nobody's stopped it.\n\nThat's it, then. That's an outpost becoming a crowd. I'll have my report up to Brill by dark.",
    ),
    "wtf_farmhands": (
        "Let me say this properly, because the Deathguard sent a lad last month who didn't let me finish.\n\nMy name is Marren. Solliden was my husband's farm, and the dead out in its fields are his hands. I've taken a room in Brill, because I couldn't sleep with them in the yard. They stayed on after he died, which was good of them. Then they stayed on after they died. Nobody prepared any of us for that.\n\nThey still work it, at all hours, with rusted tools, no crop and no direction, up and down rows that haven't held anything in years. They aren't dangerous. They just aren't stopping, and I can't watch it from this window any longer.\n\nGo gently with them. They were good men, and they worked hard for a man who didn't always deserve it.",
        None,
        "She's quiet a while.\n\nThank you. I'll see them buried at the top of the north field. It's the only part he never managed to drain, so nothing will ever be planted over them.\n\nThey'd have appreciated that. It was their favourite complaint.",
    ),
    "wtf_threshers": (
        "The other thing in my fields isn't dead. That's what I can't get anyone in Brill to understand.\n\nThe grain threshers still run. Nobody feeds them, nobody winds them, nobody has touched one since my husband was upright, and they go up and down those rows at all hours taking in whatever's in front of them. The blight got into the works somewhere, and now they don't stop at the headland the way they're built to. They just turn and come back.\n\nThey've had the last of the harvest. There's nothing out there now but stubble and each other, and a machine that's run out of crop starts looking at the fence. Break them for me. I'd rather lose the iron than find out what they settle on next.",
        None,
        "It's quiet out there, properly quiet. I'd forgotten the fields had a sound of their own under all that clattering.\n\nTake the scrap money. I've no use for iron and less for the memory of it.",
    ),
    "wtf_goodman": (
        "She doesn't look up from the window.\n\nHe's out by the far hedge. You'll know him, because he's the only one out there carrying a pitchfork instead of a hoe, and he's the only one smiling.\n\nThat's my husband, Goodman Solliden. He worked that ground for thirty years, and he was hard on the hands and harder on himself, and whatever is walking it now has his face and his stride and his grin, and the grin is wrong. I can carry the grief. It's the grin I can't carry any more.\n\nSome of the hands keep to him. You'll have to take them off him first. Then let him lie down.\n\nI'll walk home and sit at my own window while you do it. I won't watch, but I'd like to be there.",
        "He's by the far hedge at Solliden Farmstead, the one with the pitchfork. Some of the hands keep to him.",
        "There's a long silence.\n\nThe field's empty.\n\nThank you. I'll have him in beside the hands at the top of the north field, and that's the whole family seen to, and I can shut this window at last.",
    ),
    "wtp_lurkers": (
        "Don't come past the stones. I'm not warning you off. There's silt there, it's deeper than it looks, and I'd have to come and get you.\n\nI'm Oswin, and I live at Stillwater because nobody else wants to, which suits me. I'd ask you not to improve on that arrangement.\n\nThe lurkers in the silt are the neighbours. They're crab-looking things, mostly harmless, and I'd got to where I could walk the margin without bother. That's over now. Something's put them up. They come at the ankles now, in numbers, and they've stopped minding the lamp. I can't fish the margin and I can't cross it, which between them is most of what I do.\n\nThin them for me. I'd rather they stayed, mind, just fewer, and politer.",
        None,
        "I walked the whole margin this morning, both ways.\n\nThere are still some out in the deep silt, and that's good. An empty pond is just a hole full of water.",
    ),
    "wtp_dead": (
        "Now, the other lot, and I'll want you to hear me out, because it sounds daft said plainly.\n\nThe Rotting Dead come up out of Stillwater. They don't come off the bank, they come straight up out of the water, at all hours, and they sing. It's the same tune every time. It's a hymn, I'm fairly sure, and I was a churchgoing man a long time ago, and I can't place it, and it's driving me to distraction.\n\nI've tried asking them. I've tried singing it back. The second one was a mistake, and we'll leave it there.\n\nI came out here for the quiet. Give me the quiet back.",
        "They come out of the pond at all hours, singing. You'll hear them before you see them.",
        "He listens for a while.\n\nThere's nothing but the water.\n\nI'll tell you the strange part. I've been trying to place that tune for two years, and now it's gone I expect I never will. I can't say I mind. I'd rather have it stopped than solved.",
    ),
    "wtp_murk": (
        "Right, the last of it, and the reason I asked about the others first.\n\nThere's something at the bottom of my pond. I call it Murk. I've never had a proper look at it and I don't intend to. What I know is what the water does. It bloats up. Every drowned thing that goes in, it takes, and it swells, and then it brings them up again on my shore. They don't come up whole, they come up arranged.\n\nThat's where the lurkers have been getting their nerve from, I reckon. Whatever's feeding them is down there, and it's grown.\n\nTake the lurkers off the margin first, because they'll come when it moves. Then go in after it. And here's my advice, free: don't let it get behind you in the deep silt.",
        "It's at the bottom of the pond. The lurkers will come when it moves, so take them first.",
        "He's standing at the water's edge when you come back, which he never does.\n\nIt's gone down flat, the whole surface. I can see the stones on the bottom for the first time since I came here.\n\nI'm going to sit out here a while. You go on.",
    ),
    "wta_servants": (
        "I'm Envoy Sorren, speaking for Brill. I've just come back from the Agamand mill.\n\nThat mill belonged to the Agamands, and the staff are still in it. I don't mean the family. I mean the servants, the ones who cooked and swept and carried, and they're still cooking and sweeping and carrying in a house with no one left to do it for.\n\nBrill needs the grain stores. That's the entire substance of my posting. And the moment anyone goes near the stores, those servants stop being tragic and start being murderers, because somebody once told them the grain was the family's, and nobody has ever told them otherwise.\n\nClear the ones at the stores. I take no pleasure in it, and I'd thank you not to describe it to me afterwards.",
        None,
        "The stores are ours. I'll have carts up from Brill within the week.\n\nI've written that the household was dispersed in my report. It's a coward's sentence, and I'm going to leave it in.",
    ),
    "wta_keys": (
        "There's something under the mill I haven't put in a report yet.\n\nThe cellars are holding farmers, living ones, taken off the Solliden road and the western plots, shackled to the posts in the cellar and left. They haven't been eaten or turned. They've been left, the way you leave a thing you've been told to keep and haven't been told what for.\n\nThe servants carry the keys on them. They won't give them up and they won't use them. They just carry them, the way they carry everything else in that house, because it's theirs to carry.\n\nGet me the keys. Whatever else we are, we aren't going to be the people who knew about that cellar and did the paperwork instead.",
        None,
        "Every post is unlocked, which is what I needed.\n\nSome of them wouldn't come up. Years in the dark will do that, and I'm not going to drag a man into Brill to be grateful at him. We'll leave food at the stair and the door open and let them decide.\n\nIt's more choice than the Agamands gave them.",
    ),
    "wta_thurman": (
        "The mill-house itself, then, and the miller in it.\n\nThurman Agamand was the miller before he was the lord, which the family never liked mentioned. The lordship came late and came by plague, when everybody above him in the line stopped being available. He's in the house now with what's left of them, and they're very much a family still. They eat together, they sit in the right chairs, they keep to the rooms they always kept to.\n\nI've stood at that door and listened to a dead man ask a dead woman to pass something. I'd like that house back, and I'd like to stop hearing it.\n\nThe family will come at you together. They always do. That's rather the point of them.",
        None,
        "It's a building again, and that's all I wanted it to be.\n\nBrill gets its grain, the cellars are open, and the Agamands are finally as finished as everyone has been pretending they were for years. I'll sleep properly tonight, for the first time in a month.",
    ),
    "wtc_wights": (
        "I'm Keeper Halvard. The Agamand crypt gate is mine, and I haven't been through it in a long time, and I'd like to stop having to say that sentence.\n\nThe crypt is Agamand ground, vaults and name-stones, the whole dynasty laid out in order down there. My post is to keep it. Then the wights woke up in it, and a man with one lantern and a ring of keys doesn't clear a vault full of wights. So my post became standing at a door being very reliable about it, until they sent me here to ask for help.\n\nThey hold the vaults now. They've been moving things. I can hear stone going over stone at night, and I've a horrible idea they're tidying.\n\nGo down and clear them out. I'll hold the gate. I'm very good at the gate.",
        None,
        "Is it quiet down there? I can hear the lantern hissing, and that's all.\n\nI'll go down myself tomorrow and see what they moved. Tomorrow, mind you. A man should be allowed one more night of being good at the gate.",
    ),
    "wtc_dargol": (
        "There's one more down there, and he isn't like the others.\n\nCaptain Dargol commanded the Agamand guard. The wights wander, but Dargol patrols. He keeps the same route, the same turns, the same pauses at the same vault mouths, and he's been walking it for years to protect a family that's dust in boxes behind him.\n\nI'll be honest with you, because it's been bothering me and there's nobody at that gate to say it to. I don't think he's wrong, exactly. He was given a thing to keep and he's keeping it. I've a great deal of sympathy for that, standing where I've stood.\n\nIt doesn't change what needs doing. He'll have wights with him, he always does. Take them, then him, and do it cleanly.",
        None,
        "Halvard is quiet for a moment.\n\nThen the vaults are kept by me again, which is how it's written, and I'm going to try to feel like that's an improvement.\n\nGive me a day. I'll get there.",
    ),
    "wth_mongrels": (
        "I'm Warden Brask. I hold the line at Garren's Haunt, and I'm in Brill for one night to find people who'll be useful out there.\n\nThe Rot Hides keep mongrels, as stock, not pets. They run them loose through the old fields ahead of the pack to turn up anything worth digging, and the fields have been a kennel for about two seasons now. You can smell it from the line when the wind's wrong.\n\nThe gnolls are the problem, I know that, and we'll get to the gnolls. But I'm not walking anyone into that camp with a hundred mongrels loose behind us. Clear the fields first. Front door before the house.",
        None,
        "The fields are walkable, so that's the approach open.\n\nNow we can talk about the camp like people with options instead of people with a plan.",
    ),
    "wth_gnolls": (
        "Now the camp, and I want you going in knowing what these are, because the word gnoll makes people picture something stupid.\n\nThe Rot Hides wear stitched hide, carry clubs about the length of your arm, and they dig. That's their whole industry out there. They open graves, they take what's in them, and they take their time about it. There's a pit at the back of that camp that I've been told about and have decided not to look at.\n\nThey aren't stupid. They're organised, and they've been left alone long enough to get comfortable, and comfortable is the thing I'm actually out there to spoil. Get in among them.",
        None,
        "That's what I wanted. They'll be moving the pit tonight, which means they're reacting to us instead of the other way about.\n\nThat's the first time that's been true since I took this line.",
    ),
    "wth_maggot": (
        "This is the last piece, the one they follow.\n\nMaggot Eye is scarred to pieces, rotted halfway through, and bigger than anything else in that camp, and before you ask, no, the rot doesn't slow him. I've watched him take a crossbow bolt through the shoulder and finish what he was doing first.\n\nHe leads for the simplest reason there is. He bites harder than they do, and every one of them has found that out personally. That means it works the other way too. Take him in front of them, and that camp doesn't appoint a successor, it scatters.\n\nHe'll have his own close to him. Clear those, then finish it.",
        None,
        "Brask watches the smoke over the fields.\n\nThey're going east. They aren't regrouping, they're going, carrying what they can and leaving the pit.\n\nI've held this line for a year and a half. I'd quite like to go and stand somewhere else for a bit.",
    ),
    "etl_dusk": (
        "I'm Deathguard Linnea. I keep order at the Landing, which on paper is a serious posting and in practice is largely bats.\n\nThey roost in the mooring ropes, all day, upside down, perfectly content. Then a zeppelin comes in, the ropes go taut, and the entire roost drops on whoever is standing under them with their luggage.\n\nI've had two passengers refuse to disembark. I've had a goblin quote me a surcharge. The tower only works if people are willing to stand beneath it, and at present they aren't. Clear the ropes.",
        None,
        "The ropes are clear, and the midday arrival got off without anyone screaming.\n\nIt isn't glorious work, but it's the work. The Dark Lady's shipping line doesn't care whether I find it dignified.",
    ),
    "etl_dead": (
        "Next problem, and this one is costing real money.\n\nThe road between Brill and the Landing is full of wandering zombies. They don't attack the carts and they don't rob them. They stand in the road, and when a carter shouts at them they look at him, and then they carry on standing in the road.\n\nA cart that can't get through is a cart that doesn't come back, and we're three years into convincing the living trade routes that a Forsaken port is worth the detour. I won't lose that to a crowd that can't be reasoned with and can't be insulted. Clear the road.",
        None,
        "The carts are running. The afternoon run came through without stopping once.\n\nWrite that down somewhere, would you? Somebody in the Undercity thinks this post guards itself.",
    ),
    "etl_remnants": (
        "South of here is the thing this posting is actually about, whatever the duty roster says about bats.\n\nThat's the Ruins of Lordaeron, the old capital, the gate down to the Undercity, and the remnants, what's left of the men who were in it when it fell. They don't leave. They can't, as far as anyone has worked out. They walk the approach and snap at whoever passes, and what makes it hard is that some of them are still in formation.\n\nI've been told to keep the approach passable, and I've been told not to make a ceremony of it, so I won't. Clear the approach, and if any of them are wearing Menethil colours, don't tell me about it.",
        None,
        "The approach is clear.\n\nThey'll be back. They're always back. Something about that ground puts them on their feet again, and nobody above me is interested in finding out what.\n\nThat's a question for people with better titles than mine.",
    ),
    "etl_signets": (
        "There's one more thing from the approach, and this one isn't on any roster.\n\nThe remnants wear signet rings, court signets of the old Lordaeron houses, the ones that had business in that building when it fell. Most of them are worthless metal with a crest on, and I want them anyway.\n\nSome of those houses have people left, living ones, scattered west and south, who've spent years not knowing whether their father died in the throne room or walked out of it. A ring with a crest and a place it was found isn't much of an answer, but it's one, and nobody else is collecting them because nobody else thinks it's worth the trouble.\n\nBring me what you find. I'll do the rest of it myself.",
        "Take them off the remnants on the approach. They're court signets, and you'll know the crests.",
        "She lays them out in a row on the rail and doesn't pick any of them up.\n\nTwo of these I recognise. One I've been hoping not to see for a long while.\n\nThank you. I'll write the letters tonight. It's the only part of this posting I'd call worth doing.",
    ),
    "etm_restless": (
        "If you go up to Faol's Rest, mind the rows. The soil's loose, and it's loose for a reason.\n\nI'm Morvyn, gravekeeper of Faol's Rest, and I've walked down to Brill because I can't keep it alone any more. It's pilgrims' ground, most of it, people who walked a long way to be buried near a good man and got their wish about a week before the plague made it meaningless.\n\nThey won't stay down. They come up through the rows and then they stand there, in the lines, between the stones, facing the same way they were laid. They don't wander. They stand in formation, in a graveyard. I've never seen anything behave like that.\n\nPut them back. And be careful of the rows while you do it, because I'd rather not have to re-dig what I've already dug.",
        None,
        "The rows are empty, and I've tamped them back down.\n\nThey'll rise again. Something up there keeps lifting them, and I haven't found it. But they'll rise into tidy ground, and that's the part I can control.",
    ),
    "etm_seals": (
        "Now I'll tell you why they keep getting up, because I think I've worked it out and I don't like it.\n\nFaol's own grave is sealed. It isn't a slab. It's a ring of carved stone set into the ground around it, and the carving is the seal, and the ring is what keeps the whole yard quiet. It's been there as long as the pilgrims have.\n\nThe restless have been taking the fragments. They lift them out and carry them off into the rows, one at a time, and every one that goes makes the next night worse. I can't tell whether they're being driven to it or whether they just want it gone.\n\nGet the fragments back to me. If that ring fails completely, I don't think I'll be writing anybody a report about it.",
        None,
        "She fits each one back into the ring by hand, turning it until it sits.\n\nThat's the circuit closed. You can feel the difference in the ground. Go on, stand there a moment.\n\nIt's quieter, and that's all I want out of a graveyard.",
    ),
    "etm_melrache": (
        "And then there's the living problem, which is somehow the one that offends me most.\n\nThere's a Scarlet captain called Melrache camped in my yard. He's got men digging, opening graves, going through them, and calling it a crusade because the word makes a shovel into a sacrament.\n\nI want to be clear about my objection. I don't mind that he's Scarlet. I mind that these are pilgrims. They walked all that way. They chose this ground. Whatever they thought they were doing with their lives, they finished it by coming to lie near a man they believed was good, and that officer is pulling them out of the earth in handfuls to see if they're carrying anything.\n\nThe restless will be up around him when you go in. Then have a word with the captain.",
        None,
        "The shovels are down, which is what I wanted.\n\nI'll fill in what he opened myself, slowly and properly, with the right stone back over each one. It'll take me the better part of a month.\n\nI'm looking forward to it, if I'm honest.",
    ),
    "etg_wretches": (
        "I'm Gunther Lorn. I watch Brightwater Lake, which sounds like a soft posting and isn't. They've called me down to the Undercity to report on it, and you're the first one who's listened.\n\nThe Drowned Wretches come out of Brightwater at dusk. They come up the shingle, onto the bank, and they moan, and here's the part the duty roster leaves out, because I've tried to put it in twice. They moan names. They're the names of people the lake took, and some of them I know, because I was posted there when it took them.\n\nI'm not a superstitious man, and I don't want to discuss what that means. I want them back in the water, and I want to do my shift without being read a list.",
        None,
        "It's a quiet bank tonight.\n\nI won't pretend that's permanent. But I got through a shift without hearing my sergeant's name, and I'll take the night.",
    ),
    "etg_ice": (
        "There's something else about that water, and you can test this yourself while you're out there.\n\nIt's cold, the wrong kind of cold. It's colder than the air above it, in every season, and it has been since before I took the post. Lake water doesn't do that.\n\nThe shades along the shore hoard shards of black ice. They carry them about, they don't use them for anything, and wherever a shade has been standing a while the ground is hard. I've a theory that the shards are the cause rather than the symptom, and I'd like to be proved right or wrong before another winter.\n\nStrip the shards off them and bring them back to me. If I'm wrong I'll say so.",
        None,
        "They're still freezing. They've been hours out of the water and the bucket's rimed up.\n\nSo I'm half right. They aren't the only cause, but they aren't innocent either. That's more than I knew yesterday, and the shore was walkable this morning for the first time since autumn.",
    ),
    "etg_bethor": (
        "Right, now the middle of the lake, and the reason none of the rest of it has worked.\n\nBethor Iceshard is a shade, or he was. He's got too cold to finish dying, and I can't explain that to you any better than that. He stands out there at the centre and pulls the warmth out of whatever comes near. Birds go down over that water. I've seen it.\n\nThe weeping ones keep close to him, and they'll come for you first. They always do. Take them off him, then put him out.\n\nAnd listen, don't stand still out there. Whatever he does, he does it to things that stop moving.",
        None,
        "Lorn has his hand flat on the surface of the water.\n\nIt's cold, just ordinary lake cold.\n\nThat's the first ordinary thing this water has done since I was posted there. I'm going to go and write a report that nobody will understand the significance of.",
    ),
    "eth_converts": (
        "I'm Hallam, scouting. Get down a bit, that's it.\n\nThat's the Crusader's Outpost, and that lot by the fire are this season's recruits. Listen to them for a minute.\n\nThey're loud, aren't they? Young, loud, and about as prepared for a fight as a sack of apples. Hold onto that impression for exactly as long as it takes to remember they came here on purpose, to a place everyone told them was full of us, because a man in a tabard told them it would mean something.\n\nA month of drill and they're Initiates. Then they're a column, and the column comes up our road. Do it now, while it's still the easier job.",
        None,
        "That was clean. And you went in and came out without the whole camp standing to, which is the bit I actually care about.\n\nMore will come up that road. There's always more. But that's this season's column that won't be walking it.",
    ),
    "eth_initiates": (
        "Now the gate itself, and the men on it are a different proposition.\n\nThe Initiates have been drilled, they're properly armed, and they've got past the shouting stage into the quiet kind of certainty, which is worse. They hold the gate, they hold the watch rotation, and they hold whatever that outpost doesn't want seen. There's a tent at the back that nobody but Initiates goes into, and I've been watching for a season.\n\nI'd dearly love to know what's in it. Failing that, I'd settle for the gate being thin enough that somebody can go and look.",
        "They're on the gate and the watch rotation. They're drilled, so treat them like it.",
        "The gate's thin, and I had a clear look at the back of the camp for the first time.\n\nThe tent's a map table, just a map table, with our road on it and a lot of marks around Brill.\n\nI'd have preferred something sinister. Sinister is usually slower.",
    ),
    "eth_brennic": (
        "Crusader Brennic commands the outpost, and he's the reason it works.\n\nI'll give him this much: he's good. He's strong, he keeps his men fed, and he's merciless in the specific way that doesn't come from temper. He's never once lost control up there, which makes him much harder to fight and much harder to wait out.\n\nHis recruits will throw themselves at you for him, and they'll mean it. Get through them and finish it with Brennic himself. That garrison is one man's discipline in the shape of a camp, and when he goes it'll go with him.",
        None,
        "Hallam watches through the thorns a long time before he lowers the glass.\n\nThey've struck the map tent. There were no orders given that I saw. Somebody just started doing it, and the rest joined in.\n\nThat's a garrison turning back into people. The road's ours for a season at least. That was good work.",
    ),
    "etr_skitterers": (
        "When you go into the Vale, don't wander. The webbing starts a few paces in, and you won't see it until you're in it.\n\nMy name's Ravel, and I hunt the Vale, which at the moment means I hunt spiders, because there isn't room in there for anything else any more. I'm in the Undercity to sell venom and find help, in that order.\n\nThe skitterers breed faster than I can work. I clear a stretch, I come back in a fortnight, and it's thicker than when I started. And their bite doesn't kill, it stops you. That's the part that keeps me careful. Nothing in Venomweb has to hurt you. It only has to make you stand still for a while.\n\nThin them with me. I've been doing this alone for a long time.",
        None,
        "That's a proper dent. I haven't had one of those in months.\n\nI'll take the east stretch tomorrow while it's thin. Don't look so pleased, though. We're still losing, just more slowly.",
    ),
    "etr_sacs": (
        "While you're in there, there's a thing worth cutting out of them.\n\nIt's the venom sacs. The Apothecaries in the Undercity pay a frankly indecent amount for Venomweb venom. It does something to a plague draught that nothing else does, and they've stopped pretending they can get it anywhere else.\n\nSo some goes to the Undercity, because the coin keeps me in bolts, and I'd rather not starve in a wood full of spiders. Some goes to the war, because they'll have it off me either way, and it's better to be the one selling.\n\nAnd some is for me. You can want a reason for that one. You aren't getting it.",
        "Cut them out of the skitterers in Venomweb Vale. Be careful with the sacs, because they're thin.",
        None,
    ),
    "etr_mother": (
        "Now the one that matters. Every spider in that Vale came out of her.\n\nMother Venomweb is venom-fat, old, and clever in a way I've stopped being comfortable about. She doesn't rush, she doesn't panic, and twice now she's moved her brood before I got to where they were. She's doing arithmetic in there.\n\nHer skitterers will come at you in a wave when she feels you coming, so break those first, or you'll be stood still when she arrives, and standing still is the whole trick of that wood.\n\nI've been working up to this for a long time. I'd rather not do it alone.",
        None,
        "Ravel sits down on a root, which you haven't seen her do.\n\nThat's the work of years, finished.\n\nThe Vale will fill up again. Something always does. But it'll be a wood with spiders in it instead of a spider with a wood around it, and I can hunt a wood.\n\nTake the venom, all of it. I'm done counting it out.",
    ),
    "etb_worgs": (
        "You're the one Joss sent? Then you've seen the state of Balnir.\n\nI'm Edric, the stablehand. I still am, apparently, though there's been nothing to tend in the stable for years. I keep what's left of Balnir standing because somebody ought to, and I've come into Brill because I can't do the rest alone.\n\nThe Bleak Worgs have the paddock. They've denned in it, and anything that wanders in through the broken rail doesn't wander back out. It's a good paddock. Good posts, good drainage, and my master's father laid that fence and it's still square.\n\nI'd like it to be a paddock again and not a larder. Clear them out of it.",
        None,
        None,
    ),
    "etb_stableboys": (
        "Now the hard half, and I'd ask you to let me finish before you go out.\n\nThe stableboys are still there. They never left, not when the plague came through, not after. They're out in the paddock with pitchforks doing the evening round, and they've been doing the evening round for years, and the horses have been gone for every one of them.\n\nI knew them. I was one of them, in the sense that mattered. I just happened to be in the far field on the wrong week and came out of it differently.\n\nThey're waiting for a master who isn't coming and horses that aren't there. Let them stop. Go gently, and don't take the forks off them. They were proud of those.",
        "They're out in the paddock on the evening round. Go gently with them, and leave them their forks.",
        "He's a long time answering.\n\nThat's the round finished. It's the first time it's been finished since I came back.\n\nI'll bury them along the rail where they used to sit and argue about nothing. Then I'll do the evening round myself, properly, the once, and then I'll stop too.",
    ),
    "etb_vachon": (
        "There's somebody else out there, and he was never a stablehand.\n\nCaptain Vachon led the Balnir militia. It was farm lads with billhooks, mostly, and him with an actual commission from an actual lord, and he drilled them in the Balnir yard every week like it was a proper garrison. We laughed about it. He knew we laughed about it, and he drilled us anyway.\n\nHe's still holding the farm. That's what he's doing out there, and he's doing it well, which is the trouble. He's got the dead organised in a way they aren't organised anywhere else in this valley.\n\nHis lads will stand with him. Of course they will. He was the only one who ever treated them like soldiers.",
        None,
        "Edric looks out over the empty yard for a while.\n\nHe held it longer than anyone had any right to ask, three years after there was nothing left to hold.\n\nI'll put him at the gate end, facing the road. He'd have wanted the view of the approach, and I'd like somebody out there still watching it, even if it's only in the arrangement of the stones.",
    ),
    "etd_acolytes": (
        "I'm Warden Ysolde Grave. When you go up to the Cult's farm, keep the barn between you and the farmhouse.\n\nThe Cult of the Damned has the farm. They aren't raiders or a warband, they're a congregation, and they work it like a farm. That unsettles people who go up there expecting something theatrical.\n\nThe acolytes are the ones doing the calling. They stand in the yard at the hours they've been told to stand in it and reach for things that ought not to be reachable, and every time they do it the ground up there gets a little worse. The Undercity wants them silent. I want them silent for reasons that are mine.\n\nStart in the yard. They don't post a watch. They genuinely don't expect to be interrupted.",
        None,
        "The yard's clear, and nothing answered them this evening.\n\nThat hill's had its first quiet dusk since I was posted there. Don't get comfortable, though. The cellar's still full.",
    ),
    "etd_ledger": (
        "They keep books. I want you to sit with that for a moment, because everybody's first reaction is to laugh, and the laugh is wrong.\n\nThere are names, and tallies, and debts: who owes what, and to whom, and what's been accepted as payment. A cult that keeps a ledger is an institution and not a mob of lunatics, and an institution has a structure and a catchment and a list of people who've already said yes.\n\nThe pages are on the bodies. Each of them carries their own section. They don't trust one another much.\n\nGet me the pages. The Undercity will want the names, and I want to know how far down that hill the list goes.",
        None,
        "She reads with her jaw set.\n\nThere are Brill names in this, living and otherwise.\n\nI won't act on it tonight, and I won't hand it up until I've read every line. Half of being right about something like this is being slow about it.",
    ),
    "etd_thaddeus": (
        "The cellar, then, and the man issuing the orders from it.\n\nOverseer Thaddeus hasn't come up into the yard once in the time I've watched this farm. He sits at the bottom and the instructions come up, and the acolytes carry them out to the hour. The fanatics stay close to him, and they're a different animal from what you've fought in the yard. The acolytes believe. The fanatics have stopped needing to.\n\nTake the fanatics off him first. Then finish it.\n\nAnd when you're down there, look at how the cellar's dug. That's what I actually want to know about, and I'd rather you saw it with your own eyes before I put ideas in your head.",
        None,
        "You saw it, then, the dug part, and the way it keeps going.\n\nI know about it. I've been looking at the spoil heaps for a season trying to work out where all that earth came from and telling myself it was a root cellar.\n\nThere's a Boneward named Calder who needs to hear about this today.",
    ),
    "ets_bowmen": (
        "My name's Hollowmere, and I'm back from the north coast for a day, so let me tell you about the Watch Post while I've got you.\n\nThe Scarlet Watch Post sits above the north coast road, and their bowmen walk it. They aren't patrolling in the sense of looking for trouble. They walk it to shoot whatever comes along it, and they're good, and the road is the only flat way along this coast.\n\nI've watched them take a carter. He wasn't Forsaken, he was a living carter out of Brill on the Hillsbrad run, and they shot him off the seat and left the horse standing there for most of a day.\n\nGet the bowmen off that road. Everything else can wait for afterwards.",
        None,
        "The road's walkable. I watched a cart go the whole length of it this morning and nothing happened, which shouldn't feel like news.\n\nStay low going back up the slope. The post has noticed.",
    ),
    "ets_zealots": (
        "The post itself now, and you'll hear it before you're in range of it.\n\nThe zealots preach while they fight, mid-swing, properly preaching, a full sermon, and they don't stop when they're losing. I've taken one down a slope with an arrow in him, and he was still going at the bottom.\n\nI've listened to a great deal of it from this slope, and I'll tell you what's in it, since you're going anyway. It's about cleansing, and it's about us, and it's extremely specific about Brill.\n\nSo it isn't just noise, and I'd rather it stopped being said out loud where recruits can hear it.",
        None,
        "It's quieter up there.\n\nI've been on this slope four months listening to what they intend to do to my town. You've no idea what an hour of nothing sounds like.",
    ),
    "ets_preachers": (
        "Now the ones at the back, and I want you taking these seriously, because I didn't, once.\n\nThe preachers don't carry much, and that's the mistake. You look at a man in robes behind two ranks of zealots and you make a judgement about which of them is the problem.\n\nThey call fire down. I don't mean a torch or a flask. I mean fire, out of nothing, onto whoever they've decided is faithless, and they decide fast. I've got the scars under this sleeve from the day I learned to pick them out of a line first.\n\nPick them out of the line first. That's the whole of the advice, and it's all I've got.",
        None,
        "That's done it. You can see the difference in how the post moves now. They're bunching, because nobody's covering them.\n\nThat's what those robes were worth. Everybody up there knew it except the people we keep sending up the slope.",
    ),
    "ets_vishas": (
        "And the cells. I've left this one until last on purpose, and I won't dress it up.\n\nInterrogator Vishas runs the Watch Post's cells. He's patient, he's methodical, and he keeps proper hours. He stops for the evening, which is somehow the detail that's stayed with me.\n\nThere are people in there. Some of them are living, taken off the coast road. Some of them are ours, which the Crusade considers a different category of question and asks differently. Nobody has come out of those cells, in either direction, in the four months I've been on this slope.\n\nHis zealots hold the stair. Go through them, and empty the cells, and don't leave that man upright behind you.",
        None,
        "Hollowmere doesn't ask about the cells for a while.\n\nHow many came out walking?\n\nThat's more than I'd braced for. Get them down the slope before dark and I'll take the report to Brill myself. I want to be the one who says it out loud.",
    ),
    "brl_dispatch": (
        "You're going east, I hear. Then do something useful on the way.\n\nThis is for Gravekeeper Morvyn at Faol's Rest. It's sealed, and it stays sealed, and I'll know.\n\nI could send a messenger. I've sent four. One of them arrived, two came back having thought better of the hills, and the fourth is a subject I'd rather not open before noon. Morvyn's reports to me have been equally reliable in the other direction, which means the two of us have been running a graveyard and a garrison on either side of a gap neither of us can cross.\n\nPut it in her hand. Don't leave it on a stone or under a lantern. Put it in her hand.",
        "Go over the hills east, to Gravekeeper Morvyn at Faol's Rest, and put it in her hand.",
        "Morvyn breaks the seal with her thumb and reads it twice.\n\nHe wants to know whether my ground is quiet. Rennick, asking after my ground.\n\nI'll write back. Tell him it's quiet, and tell him I said it in those words. He'll know what I mean by it, which is more than I can say for most people I've had to explain this yard to.",
    ),
    "brl_guard_smelt": (
        "Before you go anywhere, do you know what that building by the east market is? Nobody does, so don't feel bad.\n\nIt's a forge. Brill has a forge, brand new, paid for out of the Undercity, and it's been standing cold since the day they finished it, because not one person in this town will admit they don't know how to light it.\n\nI'm not having my kit fall apart while a perfectly good forge sits there being decorative. There's copper ore in these hills. Take it to the forge, smelt it into bars, and bring them to me so I can see with my own eyes that the thing works.\n\nThen I'll tell you what they're for.",
        None,
        "He turns a bar over, twice.\n\nIt works, so the forge works.\n\nRight, now I'll tell you the rest of it, and you're going to need those bars back.",
    ),
    "brl_guard_bracers": (
        "Here's the rest of it, then.\n\nBars are a start, but bars aren't armour. What I want to know, and what the garrison wants to know, though they'd rather I framed it as my idea, is whether anything that comes off that forge is worth wearing.\n\nSo I want bracers, copper, made by you at the Brill forge. Not bought, not found on something, not traded off a goblin at the Landing, but made.\n\nIf a stranger can walk in off the road and come out with a pair that hold together, then this town can arm itself, and we stop waiting on a cart from the Undercity every time somebody's strap goes.",
        "Make them at the Brill forge, from your own bars. I want them made, not bought.",
        "He puts one on, flexes, and puts the other on.\n\nThese'll do, and more than do.\n\nI'm going to walk past the barracks wearing them and say nothing, and I'm going to enjoy the next hour enormously.",
    ),
    "brl_locket": (
        "The locket came off one of the wandering dead. It's the sort of thing you stop noticing you've picked up until it's in your hand at the end of a long walk.\n\nIt's tarnished almost black. The portrait inside has gone, and there's a shape where a face was and nothing you could swear to. The inscription on the back has held up better than the rest of it, because it was cut deep by somebody who wanted it to last:\n\nFor Marren, from Aldric.\n\nThere's a Widow Marren at the Solliden Farmstead, west of Brill.",
        None,
        "She doesn't take it straight away.\n\nAldric was my husband's brother. He went east with the levy and we never heard, and my husband would never say the word dead about him. He'd say not back yet, right up until he stopped saying anything at all.\n\nSo he was out there, all this time, out on the glades, not back yet.\n\nThank you. I'll put it with the two of them at the top of the north field. That's the whole family, now.",
    ),
    "ets_bowman_orders": (
        "These were torn out of a bowman's quiver, stiff with what's dried on them.\n\nIt's a set of orders, and it's a good deal more organised than a watch post has any business being. There are troop positions along the north coast, patrol times written out by the hour, and a map, a proper drawn map of the coast road, with the Brill approaches marked on it in a careful hand.\n\nThis isn't a garrison defending a hill. This is somebody planning a route.\n\nDeathguard Rennick holds the Brill gate, and he'll want to see this today rather than tomorrow.",
        "Take them to Deathguard Rennick at the Brill gate, and do it today.",
        "Rennick reads it standing up, which he doesn't normally bother to do.\n\nThey've timed our patrols. Look, there, and there. That's my rotation, written in somebody else's hand.\n\nI'm changing it tonight. And then I'm going to find out which of the carters on that road has been counting for them.",
    ),
    "etd_ledger_courier": (
        "I've bound the pages. Now I need somebody who can read them, and that isn't me, and it isn't anyone in this city I'd trust with a list of Brill names.\n\nHalf this ledger is in a cipher. It isn't a good one. It's the kind of cipher you use when you're keeping secrets from your own congregation rather than from an enemy.\n\nThe man I want is Keeper Oswin, at Raven Hill Cemetery in Silverpine, through the pass north-west of Brill. He kept records for the old church, he has a head for exactly this sort of thing, and he owes me.\n\nTake the bundle. Don't read it on the road, and not for secrecy. Do it for your own evening.",
        None,
        "Oswin weighs the bundle without opening it.\n\nYsolde Grave, now there's a name I haven't had to think about in a while.\n\nShe's right, I can read it. I can read half of it today and the rest when you've done me a service, because there's a reason the other half won't open, and it isn't the cipher.",
    ),
    "sp_ledger_cipher": (
        "Here's the trouble, and it isn't the hand it's written in.\n\nThe cult keyed the second half of this ledger to the Agamand family seals. They didn't use them as a code, they used them as a lock. The marks only resolve against the real seals, and the only person who can match them is somebody who's stood in the Agamand mansion and seen them cut into the stone. You have, and I haven't, and I'm not about to.\n\nSo I can do this work, but I can't do it here, and I can't do it while the ground behind this cemetery is behaving the way it is.\n\nThe husks come up out of the back plots and come to the window, every night, while I'm reading. Thin them out, and I'll give you my full attention and the second half of this thing.",
        None,
        "He hasn't moved from the desk, but the shutters are open for the first time.\n\nThat's better, a great deal better.\n\nNow sit down and tell me about the seals in the mansion, and I'll tell you what the back half of this ledger is actually counting. You aren't going to care for it.",
    ),
    "etc_descend": (
        "I'm Boneward Calder, and that title used to be a joke. Ysolde sent word, so you know roughly what's under the cult's farm.\n\nI'll say it plainly anyway. They dug their cellar into a body. It's a Scourge Abomination, dead a long while, and so large that its spine is a corridor. You can walk the length of it upright. The ribs are the side chambers. The skull is at the far end, and I've never been to the far end.\n\nBefore anybody commits men to this, and the Undercity will want to commit men, somebody has to walk it and come back with a length. I don't want an impression. I want a length, and what's in it.\n\nGo down the spine, and come back up it.",
        None,
        "It goes that far, and you're certain?\n\nI'd written a cellar in two reports. I'm going to have to go back and amend both, and explain why the amendment is the size it is.",
    ),
    "etc_runes": (
        "Here's the part I've been building to, and it's the reason I'm a Boneward and not a gravedigger.\n\nThe Scourge necromancers cut their wards into shards of black stone, and they're all through the bones. They aren't decoration. The same wards are what's holding the Abomination's skeleton in the shape of a skeleton. That thing has been dead for years and it hasn't fallen in on itself, and the shards are why.\n\nI want a handful. I don't want them broken in place, because that would drop a corridor on us. I want to learn how they're cut, so that when we do break them we break them in an order somebody chose.\n\nTake them off the necromancers. They'll be carrying spares.",
        None,
        "He lays them out and turns each one to the lamp.\n\nThey're sequenced, look. This edge continues that one. They didn't repeat one ward, they wrote one, and it runs the length of the body.\n\nThat means there's a last one. And a last one can be first, if you walk it backwards.",
    ),
    "etc_abomination": (
        "The skull, then, and what's wired into it.\n\nThe Abomination is at the head of the spine, and the cult has run their rune stones straight into it. That's what the whole farm has been doing up there, all those calling hours in the yard. They weren't summoning anything. They were feeding something that was already here.\n\nTake the necromancers off it first. They're the ones keeping the wards lit, and while the wards are lit you'll be hitting a thing that can't be allowed to fall over.\n\nThen put it down, and the cellar goes back to being a cellar, and this hill goes back to being a hill with an unfortunate history instead of one with a future.",
        None,
        "The lamp flames are standing straight up for the first time since he lit them.\n\nIt's just bone now, a very large amount of ordinary bone.\n\nI'm going to spend the rest of my career telling people that was a cellar, and every one of them is going to believe me, and that'll be the correct outcome.",
    ),
    "etc_orvyn": (
        "East of the ribs, in the side chamber with the light coming out of it, is the laboratory.\n\nPlaguemaster Orvyn runs it. The vats in there are where the blight on the Solliden fields comes from, and the Balnir paddock, and every field between here and Brill that won't take a crop. It isn't old plague lingering. It's being made, down here, to a recipe, on a schedule.\n\nHis acolytes work the vats, and they'll defend them before they defend him. That's what he's taught them to value.\n\nI want the vats cold, and I want the man who wrote the recipe to stop being available for consultation.",
        None,
        "The vats are cold.\n\nI'll get word to the farms. It won't fix their fields. Three years of that going into the soil doesn't lift because we turned a tap off. But it stops getting worse, and I haven't been able to offer anybody up there a sentence like that one.",
    ),
    "etc_formula": (
        "It's a sheaf of stained notes, pulled off the Plaguemaster's belt and still smelling of the vat room.\n\nIt's a working document rather than a treatise: dosages scratched out and rewritten, ingredient lists with suppliers against them, timings for the pour. There's a diagram on the last sheet showing how the delivery vats feed up into the field channels above, drawn by somebody who understood plumbing better than theology.\n\nSomeone who knows reagents could learn a great deal from this, about what went into those fields, and whether anything undoes it.\n\nAssistant Grael, at the Brill Apothecary, would know what he was looking at.",
        None,
        "Grael goes very quiet, which for him is remarkable.\n\nThis is a recipe, with suppliers on it. Half of these reagents came through Brill, and two of them came through this building.\n\nI'm going to have to tell the Apothecary something, and I'm going to have to decide tonight how much of it. Thank you, I think. Ask me again in a week.",
    ),
}
