"""Moonwell Hollow, the Howling Barrows, Grom's Rest and Blackfathom in the plain voice, gently (17 Nov 2026). These
briefings were built out of one-line paragraphs and one-word sentences, with dashes and capitals; they're joined up
into speech now, keeping each speaker's argument and turns of phrase. One briefing used an old name for Sentinel
Shalasyr, and one accept text repeated a sentence. Same stories, same directions."""

VOICE = {
    "moonwell_blighted_roots": (
        "I'm Grove Warden Pennarin. Come to the rail and look down at the water before we talk.\n\n"
        "The Moonwell's roots are coming up black at the edges. Only the edges, and that's what's kept me awake, "
        "because a thing that dies all at once has been killed, and a thing that goes black at the edges is being fed "
        "something.\n\n"
        "I need samples, and I need them off the Rootbinders rather than out of the ground. Anything I pull up myself "
        "has already been in that soil, and I can't tell you what it picked up on the way. What they carry is what "
        "they're putting in.\n\n"
        "They sing to the roots, and the roots sing back, which is ordinary and lovely and the reason I took this post. "
        "The song is wrong. Bring me what they're carrying, before this reaches the Grove proper.",
        None,
        "It's black at the core, and warm. That isn't sap.\n\n"
        "Thank you. Now at least we know how deep it goes, which is worse than not knowing and better than guessing.",
    ),
    "moonwell_gloomcap_sacs": (
        "I'm Sentinel Shalasyr. I'll keep this short, because you've a long way down.\n\n"
        "There's a question the healers can't answer from up here, and it decides everything we do next. Can the "
        "spread be burned out, or must it be cut out? Those aren't similar answers. Burning is three nights and some "
        "unhappy druids. Cutting is a season, a cordon, and telling Astranaar its Moonwell is closed. I'd very much "
        "like to know which before I write to anybody.\n\n"
        "So I want spore sacs, off the sporelings below the Moonwell. Take them gently. They burst, and if one goes "
        "you'll smell it for a week, and so will everyone standing near you. Bring them unbroken, because a burst sac "
        "tells the healers nothing except that it burst.",
        "Go to Moonwell Hollow. The way down is at the Moonwell itself, north of Astranaar past the lake. Take them off "
        "the sporelings, and bring them unbroken.",
        "They're all unbroken.\n\n"
        "I'm impressed, and I'd expected to be writing a different note this evening. The healers will want to know "
        "what these have been feeding on.",
    ),
    "moonwell_hollow_cull": (
        "The things beneath the Moonwell are growing bolder, and I can date it to the week. There are Rotlashers and "
        "corrupted Moon Guards crowding the way down, and the Rootbinders working behind them.\n\n"
        "I sent a party in eleven days ago. They were braver than they were wise, and I let them go, because they were "
        "certain and I was tired, and I've had eleven days to think about which of those did the deciding.\n\n"
        "Thin the Hollow so the next party can reach the grove at the bottom. I don't need it cleared, I need it "
        "reached. Nobody has stood in that grove since this started, and every judgement we've made has been from the "
        "stair.\n\n"
        "Go down in company. The Hollow was never meant to be walked alone, even before, and it isn't what it was.",
        None,
        "You came back, which is more than the last party managed.\n\n"
        "Sit down and eat something. I'll want the rest of it in a moment, and not before.",
    ),
    "moonwell_mosshide": (
        "There's an old gloomcap at the heart of the spread, the size of a house, and the Sentinels call it Mosshide. "
        "Here's what I need you to hold on to before you go down.\n\n"
        "Mosshide isn't the corruption. It was there before, longer than the Moonwell's lamps, longer than the "
        "Sentinels, and I've found it on a chart drawn before anyone in Astranaar was born. It's the anchor. Whatever "
        "came into this Hollow needed something already rooted and already old to hang itself on, and it found the "
        "oldest thing down there and used it.\n\n"
        "Cut it down, and the rot loses its hold. I've argued with myself about this for a fortnight, and I've lost "
        "every round of it.\n\n"
        "It won't go quietly. It has no reason to, and nothing was ever asked of it.",
        None,
        "Then the spread has a hole in it, which is what I needed.\n\n"
        "Rest properly, because Maelwyn is next, and she'll be harder for reasons that have nothing to do with the fight.",
    ),
    "moonwell_maelwyn": (
        "Pennarin takes a long time to start.\n\n"
        "Maelwyn Blightbloom was a Moonwell keeper. She held this post before me. She taught me the lamps, and most of what I know about that water.\n\n"
        "Now she's the Blight's flower. That's the Sentinels' phrase, and I haven't been able to improve on it. She's at "
        "the Moonwell itself, at the bottom of the Hollow, and as long as she stands in that water it won't run clean. "
        "End her there.\n\n"
        "She still has the face I remember. I want you to have been told that rather than discover it. People have gone "
        "down not knowing and come back up unable to say why they hesitated. Don't let it slow your hand. Do it for "
        "her. I've thought about that phrasing a long while, and I mean it exactly.",
        "Go to the well at the very bottom of Moonwell Hollow. You know the way down by now, from the Moonwell, north "
        "of Astranaar.",
        "Thank you.\n\n"
        "I'll tell the others the water is clear. I won't tell them how it looked, and I'd ask the same of you.",
    ),
    "barrows_hunters_horns": (
        "I'm Grunt Bloodfang. You'll be the one Vashj keeps talking about. Here's a job.\n\n"
        "The huntsmen buried in the Barrows still carry their horns, in the ground, after however long it's been, and nobody at this post can tell me how long.\n\n"
        "I want them gone, and my reason isn't complicated. Those horns call the dead out of the hill. The night elves "
        "don't need to tell me that. I've stood on this wall and heard it happen, twice, both times an hour before "
        "something came down the road at us. Stop the calling and I'm happy.\n\n"
        "And some of that horn-bone might ring true for a Horde signal. I wouldn't lead with that, but I won't pretend "
        "it hasn't occurred to me. I don't care whose horns they were, and neither will you, once you've heard one.",
        None,
        "It still howls when the wind touches it. That gives me the chills, and I don't get those.\n\n"
        "That was good work.",
    ),
    "barrows_rimebone_cull": (
        "My name's Veyra. I scout the Barrows for the post, and I want them quiet, and I mean that literally.\n\n"
        "That hill sings. It isn't loud. You have to be on the north wall at the right hour, and once you've heard it "
        "you hear it every night after, which is its own problem and not one I'll trouble you with.\n\n"
        "It's the Hunt's old song, and it keeps being sung because the Hunt-King's road is still being kept. The "
        "rimebone hounds keep it, and the wights keep it. They walk a route that hasn't changed in centuries, and the "
        "walking is what holds the song together. Break the route, and the song has nothing carrying it.\n\n"
        "They're dead things in a cold hole, and it isn't complicated. Go in with friends, and come out with the job "
        "done.",
        "Go into the Howling Barrows, along the Hunt-King's road, and take the rimebone dead, the wights and the "
        "howling wraiths.",
        "The howling's thinner, but it isn't gone yet.\n\n"
        "That's your next job, and I'd rather you heard that now than at the end of a drink.",
    ),
    "barrows_wintermaw": (
        "There's a hound chained in the Houndkeepers' Crypt the size of a warhorse.\n\n"
        "It's chained, and that's worth sitting with. Somebody put it there on purpose, and somebody wanted it to stay, "
        "and whoever that was has been dust for a very long time. The chains are old. The grudge is older, and I don't "
        "use that word loosely. I've tracked a lot of things, and I know a beast that's angry from a beast that's been "
        "waiting.\n\n"
        "It won't come to you. Everything else in that hill ranges. The hounds run the road, the wights walk it. This "
        "one stays where it was put and makes you come into the room. So you'll go to it.\n\n"
        "Take a healer. And take a good reason, because you'll want one about halfway down the stair.",
        None,
        "That howl has stopped.\n\n"
        "I didn't know how much of the wind it had been until it stopped, and now the wind sounds wrong to me, which I "
        "suppose is fair.",
    ),
    "barrows_hunt_king": (
        "I've been watching that hill since the hounds went quiet.\n\n"
        "At the end of the Barrows lies Hunt-King Valorin, and he's still hunting, in his sleep. I've written that "
        "sentence in three reports now and had it queried every time.\n\n"
        "Here's what it means in practice. The Wild Hunt never ended. It went underground, the whole apparatus of it, "
        "the king, the road, the hounds, the horns, and it's been running down there without a break for as long as "
        "that hill has stood. And a hunt ranges. That's what a hunt is. It doesn't stay within a boundary because the "
        "boundary is new and the hunt isn't.\n\n"
        "I won't have a dead king's hunt ranging over Horde land because nobody wanted to go into the hill. Let's make "
        "sure it stays underground.",
        None,
        None,
    ),
    "groms_garrison_cull": (
        "Grom's Rest has become a demon barracks, and I want you to take that word literally. It isn't an "
        "infestation.\n\n"
        "There are satyrs, imps and fel-touched hounds crowding the hall beyond the gate, and they're billeted. "
        "There's an order to where they sleep. I've had eyes on that gate for three weeks, and the same ones come out "
        "at the same hours. Things that crawl out of a tear in the world don't keep a roster. So somebody is running "
        "it, and whatever he's running it for is behind that hall rather than in it.\n\n"
        "Thin the garrison so a real party can push through to find out. This is a dungeon, not a stroll, so bring a "
        "full party and your potions. Then bring me proof the hall is clearer, because I won't tell Splintertree a "
        "thing I haven't been handed.",
        "Go to the hall beyond the gate at Grom's Rest. Kill the dread imps and corrupted felhounds until it's quiet.",
        "That's what I needed. The gate is no longer a wall of bodies.\n\n"
        "Now find out what they're guarding, because I promise you it isn't the hall.",
    ),
    "groms_legion_brands": (
        "There's something I want off the Felguard Legionnaires, and it isn't a trophy.\n\n"
        "They wear a fel-iron plate stamped with the Legion's mark. It was stamped in a foundry, by a process, with a "
        "die that somebody cut, which means there's a supply line, and a supply line has a beginning, and the "
        "beginning is somewhere a person could walk to.\n\n"
        "That's what I actually do here. Most of what I've ever learned, I've learned off equipment, not prisoners. So bring me a handful, and I'll trace where the Legion's gold is coming "
        "from.\n\n"
        "Take them off the dead, not the living. I know that sounds like a joke, and it isn't. A legionnaire will let "
        "you get a hand on that plate, and the three seconds it takes to work it loose are the three seconds he's "
        "waiting for.",
        None,
        "These are stamped in a Legion foundry I know. I know the die, and I know the hand that cut it.\n\n"
        "Someone is shipping weapons through Ashenvale. And I know exactly who to ask about it, which I didn't this "
        "morning.",
    ),
    "groms_satyr_warlord": (
        "The Satyr Warlord rules the western hall.\n\n"
        "I'll be straight with you, because you'd work it out anyway and resent me for it. He's a detour. The road to "
        "the throne doesn't go through him, and nothing behind him matters. You could skip him, and I know it.\n\n"
        "Do it anyway, and here's the argument. A warlord left alive is a warlord that recruits. I've watched it happen "
        "in this forest twice. We push through, we take the throne, we declare it finished, and eighteen months later "
        "the hall has a new garrison in it, built around the one loud thing nobody bothered to kill.\n\n"
        "His head sends a message to the satyrs who'd be doing the rebuilding. That's worth a detour, and I've stopped "
        "apologising for asking.",
        None,
        "That's done it.\n\n"
        "That kind of loud ends in a very particular silence, and the ones who were listening to him will have heard "
        "it.",
    ),
    "groms_void_handmaiden": (
        "There's a Void Handmaiden in the eastern gathering, and she's binding satyrs to something that wasn't made to "
        "be bound.\n\n"
        "People hear demon dungeon and bring the wrong preparation. "
        "Void magic isn't like fel. Fel burns, hostile and loud, and it tells you what it's doing to you while it "
        "does it, and every fel ward we own was built around that.\n\n"
        "Void makes you forget, and it doesn't hurt in a way you'll notice. It takes things out of the room, a name, a "
        "direction, the fact that somebody was standing to your left, and it does it so quietly that the party "
        "doesn't realise it's down a member until the fight is over.\n\n"
        "So take someone who remembers you. That's the actual instruction. I mean someone who'll notice if you stop being there.",
        None,
        "I feel lighter.\n\n"
        "I think it's lighter. I've been standing in the same tent for a month, and something has changed in it, and I "
        "can't tell you what.",
    ),
    "groms_doomguard": (
        "The only road to the throne runs north from the hub, and there's a Doomguard Sentinel standing in it.\n\n"
        "It's never once left its post. I keep coming back to that, because everything else in that place moves. The satyrs patrol, the hounds range, the imps go where imps go. "
        "This thing stands in a corridor. It doesn't tire, it doesn't sleep, and it doesn't move, not to pursue, not to "
        "flank, not even when you were clearing the hall behind it a week ago. That tells you what it's actually "
        "for.\n\n"
        "It isn't guarding the road. It's a door, and somebody shut it. So you'll have to persuade it, forcefully, and "
        "with everything, because a thing that's stood in one place for years has nothing to spend its strength on but "
        "you.",
        None,
        "That's one down. There are three rooms behind it, and the throne beyond that.\n\n"
        "Press on while the road's open. A door like that may not be the only one they had.",
    ),
    "groms_corrupted_ancient": (
        "Deeper in there's an Ancient, and it's been bent into a demon's horror.\n\n"
        "It was a grove warden. I'm not being sentimental about a tree. It had a post, and a stretch of forest, and it "
        "did the same work Pennarin does at the Moonwell for longer than the night elves have had a word for the job. "
        "Now it's a thing that rots, and it rots outward, and everything in that chamber is what it's done to the room "
        "around it.\n\n"
        "Remember it was a protector when your hand slows. It will slow. I've watched it happen to people considerably "
        "harder than either of us, and the ones who weren't told beforehand are the ones it killed.\n\n"
        "And then remember that it can't be saved. Remember both of those, in that order. I haven't found a way to "
        "give you one without the other.",
        None,
        "I'll tell the druids it fell fighting.\n\n"
        "That's as close to the truth as they can bear, and closer than I'd manage if they asked twice.",
    ),
    "groms_felguard_overseer": (
        "The Bone Hall is the last gate before the Inner Sanctum, and a Felguard Overseer holds it. Here's why he's "
        "mine rather than Grimtotem's.\n\n"
        "An overseer answers to somebody. That's the entire function. He isn't there to fight. He's there so that "
        "whatever's in the Sanctum doesn't have to speak to a garrison. And a thing that answers to somebody wears "
        "proof of it.\n\n"
        "Bring me his collar. If the Legion has a hand in Ashenvale, its fingerprints are on that collar: the make, the marks, who had the authority to put it on him.\n\n"
        "I've been building this case off stamped plate and shipping routes for a year. A collar finishes it. That's "
        "one object between me and being able to name the hand, and I've waited a long time to be this close to the "
        "end of a sentence.",
        None,
        "It's a Legion collar, as I thought, and I'd half hoped not.\n\n"
        "Now we know who's been sending the demons. And they don't know we know, which is worth more than everything "
        "else you've brought me.",
    ),
    "groms_lord_nightmare": (
        "The throne is at the heart of Grom's Rest, and all of this has been feeding the thing that sits on it.\n\n"
        "That's the shape of the whole place, and it took me the full year to see it. The satyrs, the imps, the "
        "hounds, the bindings in the eastern hall, none of that was a garrison defending a position. It was a household "
        "keeping something alive. Call it an eldritch horror, because the precise words would take an hour.\n\n"
        "Kill it, and the throne is empty, and Ashenvale stops paying for it.\n\n"
        "I've got no better advice than this, and I've thought hard about whether to give it at all. Don't look at it "
        "directly. And don't die, which I'm aware isn't advice. I've got nothing else, and I'd rather say so than "
        "invent something.",
        None,
        "The silence is unbelievable.\n\n"
        "I've had a map on this table for a year, and I don't know what to do with the table.\n\n"
        "Rest now, hero. You earned the quiet, and so did this forest.",
    ),
    "bfd_garrison": (
        "I'm Lookout Taelanor. Come up here, where I can watch the water while we talk.\n\n"
        "There's a flooded temple under the cliffs, and the naga have been going in and out of it for weeks. It's a "
        "garrison, not a raid, and that distinction is the whole of my report,  A raid comes, takes, and goes. A garrison arrives and stays and gets reinforced, and you only know which "
        "you're looking at by counting.\n\n"
        "So I've been counting. I've counted them going in. I haven't counted them coming out. That's the part that "
        "frightens me, and I've had three weeks to find a better explanation, and I haven't got one.\n\n"
        "Thin the warriors before it empties onto the Strand. Go down in company. Whatever's holding that many naga in "
        "one hole won't be a pleasant surprise.",
        None,
        "They'll replace them, though not tonight.\n\n"
        "I wrote the number down. I'm glad it isn't higher, and I'm aware that's a strange thing to be glad about.",
    ),
    "bfd_ghamoo_ra": (
        "There's a turtle in the outer caverns the naga revere as a god. I'd find that almost sweet if it weren't the "
        "size of a boat and hungry.\n\n"
        "I want to be careful here, because I've watched people treat they worship it as a reason to be gentle, and it isn't. Ghamoo-ra is a beast. The worship is theirs, not its. It has no idea it's a god, "
        "and it won't fight like one. It'll fight like something very large that's never had to learn.\n\n"
        "What it does is block the way inward. That's its actual role, whatever they say at the altar. Nothing gets "
        "deeper into those caverns past it, and that includes us, and that's why it's been left alive and fed.\n\n"
        "Break it, and take the way. I wouldn't ask if there were another road. I've looked for one for three weeks.",
        None,
        "A god, they said, and it died as easily as a turtle.\n\n"
        "I'll remember that the next time I hear the naga pray, and I hear them most nights.",
    ),
    "bfd_lady_sarevess": (
        "Lady Sarevess commands the naga of the upper halls, and she's the reason the garrison works. Here's the evidence.\n\n"
        "They don't fight each other, and naga always do. Every naga band I've ever watched on this coast has spent "
        "half its strength on internal argument. This one doesn't, and that doesn't happen without somebody holding "
        "the chair hard. If she falls, they'll fight over the chair for a month, and that's a month the Strand sleeps. "
        "\n\n"
        "She'll offer you terms. I wouldn't read them. I know you'll want to, and I'm telling you anyway, because the "
        "last Sentinel who read them is still in Astranaar and still not right.\n\n"
        "Cut her down, and spare me the sound of her voice in my dreams.",
        None,
        None,
    ),
    "bfd_gelihast": (
        "Right, you're the one who's been going down there. Good, because nobody else will listen to this.\n\n"
        "My name's Illyen. I build boats, which in Zoram'gar means I mostly rebuild boats.\n\n"
        "Gelihast has gathered the Deeps' murlocs under one banner. That's the official half of it, and the Lookout "
        "will tell you it matters, and she's right, and I don't care.\n\n"
        "He wears my net as a crown. It's my net, off my boat, the one I lost in spring, that I knotted myself, that "
        "took a week and cost me a thumbnail. And he wears it on his head, on purpose.\n\n"
        "Bring it back. It's patched, it stinks, and it's worth nothing to any person alive, including me. I want it "
        "anyway. And scatter the rest of them while you're in there, since you'll be down that way regardless.",
        None,
        "That's my knot! Look at that, he left the knot in. He's a fool.\n\n"
        "Thank you. I'll sink another boat in his honour, which at my rate will be a fortnight.",
    ),
    "bfd_hydra_fangs": (
        "Here's the second thing, and this one's actually professional.\n\n"
        "The murloc hydras down in the Deeps shed their fangs, and a hydra fang will cut a rope under tension and "
        "never go dull. Every boatwright on this coast has heard the claim, and about half of them think it's a "
        "story.\n\n"
        "It isn't a story. I've had one for two years. I've cut standing rigging with it, under load, at sea, and it's "
        "exactly as sharp now as the day I took it off the thing. I don't know why. I've asked a druid and I've asked "
        "a goblin and got two confident answers that disagreed.\n\n"
        "Bring me a handful for the rack. Then I'll have a tool rack worth showing off, and I'll sharpen nothing for a "
        "year, and that's the whole of my ambition this season.",
        None,
        "And there isn't a chip on any of them.\n\n"
        "These are going straight in the rack. I'll sharpen nothing for a year, and I'll be insufferable about it.",
    ),
    "bfd_tide_callers": (
        "Two of the deeper masters hold the inner temple, and they aren't a pair.\n\n"
        "Lorgus Jett commands the tide. Old Serra'kis commands what the tide has swallowed. Those are different "
        "offices, and it took me a long while to understand that the temple has two of them on purpose. One brings the "
        "water in. The other keeps whatever comes with it. A garrison isn't arranged that way. A temple is, and it's "
        "been running that way since long before the naga we're fighting were born.\n\n"
        "You'll have to go through both. There's no route that takes one and leaves the other.\n\n"
        "It isn't a job for fewer than a full party. I wouldn't go down there with less, and I've been watching that "
        "water for three weeks.",
        "Go to the inner temple of the Deeps, and take both of them.",
        "That's both of them.\n\n"
        "I felt the water settle. I actually felt it, from up here on the wall. I'd have missed it entirely if I'd been "
        "looking at the sea instead of at you.",
    ),
    "bfd_kelris": (
        "Twilight Lord Kelris is at the temple's heart, and he's the reason any of this is happening. The naga were "
        "here first, and the murlocs have always been here. Neither of them built this.\n\n"
        "He puts the Twilight's Hammer's work in the mouths of dying men. I'd like you to have that plainly. I've "
        "pulled three people off this shore in three weeks who should have been past speaking and weren't, and all "
        "three said the same thing, and none of them had ever met each other. I wrote it down the first time. I didn't "
        "the second.\n\n"
        "I want him silent. He works in whispers. That's the whole of his method, and it's why nobody's stopped him. "
        "Don't listen to him. Just cut him down.",
        None,
        "He's silent now.\n\n"
        "I'd forgotten silence could be so loud. There's one more below him, and then it ends.",
    ),
    "bfd_aku_mai": (
        "At the bottom of Blackfathom, under all of it, Aku'mai sleeps.\n\n"
        "The naga call it the Devourer, and they don't call it a god. They call the turtle a god, and nothing so small for this one.\n\n"
        "Everything you've done down there has been about this: the garrison, the tide-callers, Kelris in the heart "
        "whispering into dying men. None of that was a war on the Strand. It was an apparatus around a sleeping thing, "
        "and I've never been able to decide whether they were keeping it asleep or getting it ready. If it wakes, the "
        "Strand is the least of the world's worries.\n\n"
        "It's the last thing in the Deeps. Kill it while it sleeps, or don't go at all. There's no third version of "
        "this where somebody has a look first. I'll be on the wall, watching the water.",
        None,
        "Then it's over.\n\n"
        "I'll sleep tonight. Three weeks on that wall, and I'll sleep tonight. You earned that, and the Strand's "
        "gratitude. Take the pearl, if it still glows.",
    ),
}
