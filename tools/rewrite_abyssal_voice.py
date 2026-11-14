#!/usr/bin/env python3
"""The Abyssal Sands, rewritten in plain speech. Words only: no objective, reward or chain changes.

    PYTHONPATH=. python3 tools/rewrite_abyssal_voice.py

Kyle, 13 Nov 2026: "Don't use weird AI tics", then "Fix up quests first." The Sands' 32 quests and
Fourth Peg's eight greetings were written before that rule: no contractions, capitals for stress,
dashes, "which is a different job with a different answer", and counts spoken beside objectives.

WHY A PATCH AND NOT THE BUILDER. tools/build_abyssal_quests.py regenerates the whole file and would
drop the four Dry Deep quests and the overhaul's fixes. This tool only replaces text on quests that
already exist, by quest_id, and can be run any number of times.

WHAT CHANGED IN THE FACTS, because the old text was wrong about them:
  * Everything is dated from the Integration, THREE years ago (the old text said four in places).
  * The Throats are in the SOUTHWEST and Underlight in the SOUTHEAST. The old text put both "east".
    The thread still runs east: the water under the field drains toward the Glittervein.
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: quest_id -> (description, accept_text, turn_in_text[, title])
QUESTS = {
    "ab_fourth_peg": (
        "Find out from Peska Vane why the survey camp is called Fourth Peg, and what it's for.",
        "You came in by the north gate, so you've walked nine miles of this and seen there's no "
        "road. There used to be one. It fell into a pit three years ago, with the first of the "
        "collapses.\n\nThe port at Steamwheedle pays me to find out if a new road can be built "
        "across the Abyssal Sands. I haven't got an answer yet.\n\nGo and stand by the peg in the "
        "middle of camp, then ask me about it. We measure everything from that stake.",
        "That peg's stood seven months, which is longer than the other three managed.\n\nIf "
        "you're going out there anyway, I've got work for you. Most of what I need is readings "
        "from places I don't like sending Hask alone."),
    "ab_the_level_run": (
        "Walk Hask's survey line west from Fourth Peg to Cartfall and the First Hole, and kill "
        "the Pit Shrikes nesting along it.",
        "I need the ground levelled in a straight line west of here, from the peg to Cartfall and "
        "on to the First Hole at the far west end. A straight line means walking it, so you can't "
        "go round the bad stretches.\n\nPit Shrikes nest along that line where the ground's thin, "
        "and they'll come at anyone who walks past. Kill the ones you meet so I can follow you "
        "with the staff.",
        "Those are good numbers. They're dull, and dull's what I want out here. Three years ago "
        "nobody had any numbers for this ground, because nobody thought it needed measuring.\n\n"
        "There's one thing I can't get into the book. The hardpan sounds different when there's a "
        "hollow under it, and it's louder when it's cold. I've tried to write that down for two "
        "years and it still reads like guessing."),
    "ab_reading_the_pan": (
        "Kill Limestone Crawlers at the Wide Sink and bring Hask their shell-plates, so he can "
        "test what he hears in the ground.",
        "I think I can test what I hear, and you won't enjoy it. Limestone Crawlers come up where "
        "the ground's thin. If I'm right about the sound, there'll be more of them where the "
        "hardpan sounds wrong to me.\n\nI've marked a stretch by the Wide Sink, southwest of "
        "camp. Kill the crawlers that come up there and bring me their plates, so I can count "
        "them against Peska's rod readings.",
        "That's a lot of plates for a stretch that short. Peska's rod says the roof there is the "
        "thinnest we've measured, and I called it thin before she put the rod in.\n\nOne match "
        "doesn't prove anything. It's the first time my ear and her rod have agreed on paper, "
        "though, and I'll take it."),
    "ab_wait_and_read": (
        "Take Peska's second set of readings at the Wide Sink and Cartfall, and kill the "
        "Hollowing Oozes eating the Wide Sink's rim.",
        "One reading tells me where the ground is. It takes a second reading at the same stake, a "
        "few days later, to tell me if it's moving. I took the first set four days ago.\n\nTake "
        "the second set for me at the Wide Sink, southwest of here, and at Cartfall to the west. "
        "While you're at the Wide Sink, kill the Hollowing Oozes on the rim. They eat limestone, "
        "and I'd like fewer of them eating that one.",
        "The Wide Sink's rim has moved eleven inches in four days. You wouldn't see that standing "
        "on it, but it's a big number in my book.\n\nThat pit opened three years ago and the "
        "whole camp treats it as finished. It's still going."),
    "ab_second_peg": (
        "Take the snapped survey stake head to Chief Surveyor Vane at Fourth Peg.",
        "This is the top few inches of a survey stake, broken off clean. There's a number burned "
        "into the wood. The surveyor at Fourth Peg, in the northeast corner of the Abyssal Sands, "
        "will know which stake it came from.",
        "That's a two, so it's off Second Peg. Second Peg's on the lip of the Wide Sink, marking "
        "ground that fell in.\n\nThe ground didn't do this. The break's too clean, so somebody "
        "snapped it off by hand. I don't know who'd walk out there to break a survey stake, and "
        "I'd like to."),
    "ab_is_it_possible": (
        "Kill Saltbone Revenants around the Long Collapse, bring Peska residue from Hollowing "
        "Oozes, then ask her for her answer about the road.",
        "I've got two years of readings and I'm nearly ready to give the port an answer. I want "
        "one more set from the south first.\n\nSaltbone Revenants walk the ground around the Long "
        "Collapse, southwest of here, and I can't put a rod in while they're there. Kill them, "
        "and bring me residue from the Hollowing Oozes while you're out. Then ask me for the "
        "answer. You'll hear it before the port does.",
        "You can tell Rullo Tack at Steamwheedle I said this.\n\nA road can be built. Nobody will "
        "pay for it, because lenders want twenty years of safe ground and four of my eleven pits "
        "are still moving.\n\nSo my answer is to ask again in ten years. I expect the port will "
        "end my contract over it."),
    "ab_on_the_box": (
        "Hear Odd Varrow's story of Nineteen Mile, and kill the Cartfall Scavengers picking over "
        "the wrecks at Cartfall.",
        "I was driving the second cart at Nineteen Mile when the road fell in. The lead pair were "
        "six lengths ahead of me. The cart went down, I fell off the back, and the ground I "
        "landed on held. I didn't do anything clever.\n\nCartfall Scavengers pick through the "
        "wrecks at Cartfall, west of here, every day. There are still people down in those pits. "
        "Kill the scavengers and get them off the rim.",
        "Thank you. I don't blame them much. They came through three years ago with everything "
        "else and found a desert full of carts nobody was guarding. I'd probably loot them too."
        "\n\nI just don't want them doing it on top of my friends."),
    "ab_the_lead_pair": (
        "Put down the Pitfall Kodo around Cartfall and bring Odd the harness straps off them.",
        "Some of the kodo that went into the pits climbed back out, and they came out wrong. "
        "You'll see Pitfall Kodo around Cartfall, west of camp, still wearing their harness.\n\n"
        "They can't be led and they charge the camp's animals, so they have to be put down. Cut "
        "the harness off the ones you kill and bring it to me. Every strap has a house mark, and "
        "the owners should be told.",
        "Let me look through them. This one's Tarrow's mark. So is this one. I don't know this "
        "last one.\n\nI'll write to Steamwheedle about them. It's three years late, but those "
        "houses still don't know where their teams went."),
    "ab_drovers_in_the_sand": (
        "Put down the Sunken Drovers at Cartfall and the First Hole, and bring Marda their tags.",
        "I cooked for caravans for eleven years before I came here, so I knew a lot of drovers. "
        "They don't stop for weather or raiders or a broken axle.\n\nThe ones who went into the "
        "pits haven't stopped either. Sunken Drovers still walk the old route at Cartfall and the "
        "First Hole, west of camp. Put them down and bring me their tags. Nobody's ever told "
        "their families.",
        "I knew two of these names. I didn't know them well, but I knew how they took their tea."
        "\n\nPeska will write them in her book as numbers. I'm going to send the tags home with "
        "the next cart to Steamwheedle."),
    "ab_never_arrived": (
        "Take the sealed waybill to Quartermaster Lund at Fourth Peg.",
        "It's a cargo manifest with the wax seal still whole. The cart it belonged to went into a "
        "pit. The quartermaster at Fourth Peg, in the northeast corner of the Abyssal Sands, "
        "keeps the camp's freight records and might want it.",
        "Let me break the seal. It's seed grain, forty bushels, bound for Gadgetzan and dated the "
        "spring the wells failed.\n\nSo somebody in that city ordered next year's seed while the "
        "water was dropping. They still thought there'd be a next year.\n\nI'll keep this with "
        "the camp ledgers. It ought to be on record somewhere."),
    "ab_what_the_birds_know": (
        "Kill Pit Shrikes around the Wide Sink and bring Hask their crops, to see what they've "
        "been eating down in the pits.",
        "Every rodman knows this trick. If you want to know what lives somewhere you can't reach, "
        "open a bird that hunts there.\n\nPit Shrikes hunt the rims and down inside the pits, and "
        "they eat anything they can carry. Kill the ones around the Wide Sink, southwest of camp, "
        "and bring me their crops. Vizzi says there's water at the bottom of those pits. I'd like "
        "to check before I argue with her.",
        "Most of these had something in them that lives in water. There hasn't been standing "
        "water in the Abyssal Sands in anyone's lifetime.\n\nSo Vizzi's right, and she's been "
        "saying it for a year. She's going to be unbearable about it."),
    "ab_the_long_collapse": (
        "Walk the north rim of the Long Collapse for Peska, kill the Sinkhole Lurkers denning "
        "there and bring back their spurs.",
        "The Long Collapse opened eleven months ago. It took four hours and it swallowed a long "
        "stretch of the old road. It's the only pit any of us watched open.\n\nIt's southwest of "
        "camp. I've walked the north rim nine times and I've stopped noticing things, so I want "
        "somebody else to walk it. Sinkhole Lurkers den under the lip there. Kill them and bring "
        "me their spurs, so I know how many have moved in.",
        "You can walk the whole length of it and never be more than a step from the edge. Three "
        "years ago that was road, and I'd have driven a cart down it.\n\nI've written that in the "
        "book in those words. I don't usually write that way, but the measurements alone didn't "
        "cover it."),
    "ab_nine_have_floors": (
        "Ask Vizzi Trask about going down the pits on a rope, and kill the Limestone Crawlers "
        "around the Wide Sink before her next descent.",
        "Somebody has to go down the pits on a rope and see if there's a floor. I've been doing "
        "it with only Hask on the line.\n\nLimestone Crawlers come up the walls while I'm hanging "
        "there, and Hask can't hold a rope and fight. Kill the crawlers round the Wide Sink, "
        "southwest of camp, before my next descent. Ask me about the rope first, if you want to "
        "know what you're guarding.",
        "Nine of the eleven pits have floors and two don't. Peska writes those two up as 'no "
        "bottom observed'. I'd write 'don't go down', because the next person who reads her book "
        "might try.\n\nNone of these pits were here three years ago. People out here forget that "
        "quickly."),
    "ab_up_through_the_floor": (
        "Kill the Limestone Crawlers and Hollowing Oozes coming up at the Wide Sink.",
        "Everyone here talks about what fell into the pits. Carts, kodo, the road. I've been down "
        "nine of them and I'm more worried about what's climbing out.\n\nLimestone Crawlers and "
        "Hollowing Oozes are cave animals. This desert couldn't feed them three years ago. Now "
        "they come up at the Wide Sink, southwest of camp, and every month they get closer to our "
        "tents. Kill both kinds along that rim.",
        "That'll keep them off the camp for a week or so. It won't be two.\n\nBefore the change, "
        "nothing lived under this desert that wanted to come up. Now I thin them out, they come "
        "back, and I do it again. I don't see that ending while the pits are open."),
    "ab_what_the_salt_cured": (
        "Kill Saltbone Revenants at the Long Collapse and bring Sepp their knucklebones, so he "
        "can test where the salt came from.",
        "I'm a brewer, so I know what brine does to bone. The Saltbone Revenants that come up out "
        "of the Long Collapse, southwest of camp, have been cured in brine.\n\nThe nearest brine "
        "I know of is the Shimmering Flats, four days northwest. So either somebody's hauling "
        "salt out here, or there's brine under our feet. Kill the revenants and bring me their "
        "knucklebones, and I'll test the salt against what I've got from the Flats.",
        "It's the same salt as the Flats. So it's under us, and it's been coming this way for "
        "three years.\n\nEveryone on the Flats will tell you their water went underground and "
        "headed east. We're east of them. I don't think anybody asked what it passed through on "
        "the way."),
    "ab_the_throats": (
        "Walk the rim of the Throats in the far southwest, kill the Deepwater Horrors there and "
        "bring Vizzi their scales.",
        "The Throats are the pair of pits in the far southwest corner, and they've got no floor I "
        "can find. I won't go below forty feet in them.\n\nDeepwater Horrors climb out of them, "
        "and they come out wet. Walk the rim, kill the horrors you find and bring me scales off "
        "them. I want to show Peska that something down there lives in water.",
        "This scale's been in a bag in the desert for a day and it's still wet.\n\nSo there's "
        "water down there, and enough of it to keep an animal that size alive. This camp's been "
        "walking over it for two years."),
    "ab_feeding_from_below": (
        "Kill Hollowing Oozes at the Wide Sink for their residue, and the Pit Shrikes feeding on "
        "them, so Sepp can show where these animals came from.",
        "Look at what lives out here. Crawlers and oozes are cave animals. The horrors in the "
        "Throats live in water. The revenants are cured in brine. The only desert animal on the "
        "list is the Pit Shrike, and it's here to eat the others.\n\nI think they all came up "
        "after the water under the desert drained away. Kill Hollowing Oozes at the Wide Sink, "
        "southwest of camp, and bring me their residue. Kill the shrikes feeding there too, or "
        "they'll have the residue before you do.",
        "That's enough residue to measure, and it's all dissolved limestone from deep down.\n\nSo "
        "these are cave animals, and they're up here because their cave drained and lost its roof "
        "three years ago. I can put that in front of Peska with a number on it."),
    "ab_managed_not_solved": (
        "Kill the Sinkhole Lurkers along the Long Collapse and the Limestone Crawlers between "
        "there and camp, and bring Vizzi the lurkers' spurs.",
        "Peska wants readings, Hask wants his method and Odd wants the scavengers gone. I'd like "
        "the camp to still be standing next month.\n\nSinkhole Lurkers have started denning along "
        "the Long Collapse, southwest of here, and Limestone Crawlers are coming up between there "
        "and the tents. Kill both. Bring me the lurkers' spurs, so I can show Tobbit how many "
        "there were.",
        "That's bought us some quiet. They'll be back, and I'll ask somebody to do this again."
        "\n\nI've been here two years and it's gone like that the whole time. Thanks for taking a "
        "turn."),
    "ab_the_fused_face": (
        "Go and look at the Glasswall, south of Fourth Peg, and kill the Glasswall Elementals on "
        "its rim.",
        "There's a pit south of camp called the Glasswall. About sixty feet of its south face has "
        "melted into glass. You can see your reflection in it in the afternoon.\n\nSand needs a "
        "furnace's heat to do that. Nothing in this desert burns that hot, and lightning doesn't "
        "melt sixty feet in a straight line. Go and look at it for me. Glasswall Elementals "
        "wander the rim, so you'll have to kill those to get close.",
        "Did you see how smooth it is? Three years of blowing sand should've scratched it dull."
        "\n\nSo it melted after the pit opened, and not long ago. I still don't know what did "
        "it."),
    "ab_annealed": (
        "Kill Glasswall Elementals at the Glasswall and bring Sepp their fused shards.",
        "I've had a shard from the Glasswall on my bench for a month and it's still warm. It's "
        "warm at midnight, when the rest of the desert's freezing.\n\nThe Glasswall Elementals at "
        "that pit, south of camp, are made of the same glass. Kill them and bring me their "
        "shards. I want to find out if the heat's in the stone or in something inside the stone.",
        "The stone's ordinary. I crushed one shard, dissolved one and left one in the dark for a "
        "week. The one in the dark's the warmest.\n\nNothing's heating that glass from outside. "
        "Something inside the glass makes its own heat, and I don't know what."),
    "ab_the_south_facing": (
        "Kill the Glasswall Elementals coming up the slope from the Glasswall, then ask Marda "
        "what the camp thinks of it.",
        "Twice a year the sun hits the Glasswall at the right angle and it throws the light back "
        "at the camp. For forty minutes we're the brightest place in Tanaris. Tobbit says it's a "
        "hazard and Hask says it's beautiful.\n\nI like to stand on the rise and watch it, and "
        "lately Glasswall Elementals have been coming up the slope at me from the pit, south of "
        "here. Kill them. Then ask me about the glass, and you'll hear what the rest of the camp "
        "thinks.",
        "Good. Now I can watch it without keeping one eye on the slope.\n\nIt's the only thing "
        "out here that keeps a schedule, and I look forward to it."),
    "ab_nothing_is_hot_enough": (
        "Kill Glasswall Elementals at the Glasswall, bring Peska their fused shards, and ask her "
        "how she'll write the place up.",
        "I've got to write up the Glasswall and I've put it off for seven months. I don't know what "
        "melted it, so the entry has to say 'cause unknown'. I've never written that under my "
        "name.\n\nIf I must write it, I want samples and a date beside it. Kill the Glasswall "
        "Elementals at the pit, south of camp, and bring me their fused shards. Ask me about the "
        "glass after, and I'll tell you how the entry's going to read.",
        "Here's the entry. 'Cause unknown. Sixty feet, south face, melted after the collapse, "
        "samples taken, no heat source found.'\n\nIt's in the book now. I hate it, but it's true, "
        "and the samples make it a finding."),
    "ab_the_wrong_direction": (
        "Stand on the rim of Underlight, in the far southeast, and kill the Deepwater Horrors "
        "climbing out of it.",
        "The pit in the far southeast corner is called Underlight. There's light coming up out of "
        "it. You can't see it at noon, but after dark you can read by it on the rim.\n\nGo down "
        "the east side of the Sands and stand on that rim. Everybody in camp has done it once. "
        "Deepwater Horrors climb out of that pit, so kill the ones you find before you turn your "
        "back on the edge.",
        "Everybody who looks into Underlight wants to climb down. Nobody in camp says so, and I "
        "felt it too.\n\nThat light wasn't there before the change. I asked the old caravan hands "
        "and none of them ever saw it."),
    "ab_lit_from_below": (
        "Kill the Glasswall Elementals and Hollowing Oozes on the rim of Underlight, and bring "
        "Hask wet scales from the Deepwater Horrors there.",
        "The light in Underlight doesn't flicker, so it's no fire. It's the wrong colour for the "
        "Glasswall's glass. I've measured it getting a little brighter every season.\n\nBefore I "
        "tell Peska that, I want samples of what lives next to it. Go to Underlight, in the far "
        "southeast corner. Kill the Glasswall Elementals and Hollowing Oozes on the rim, and "
        "bring me wet scales off the Deepwater Horrors there.",
        "Everything you brought back from that rim is wet. The samples I've had from further west "
        "were drier.\n\nSo the water's closer to the surface on the east side. Peska pitched this "
        "camp in the northeast corner, and I'm starting to think she'd guessed that."),
    "ab_the_two_without": (
        "Walk the rims of the Throats and then Underlight in one trip, and kill the Deepwater "
        "Horrors at both.",
        "Nine pits have floors and two don't. The Throats are in the southwest and Underlight's "
        "in the southeast, with the whole field between them. I've let out all hundred and twenty "
        "feet of my line in both and touched nothing.\n\nWalk both rims in one trip, the Throats "
        "first and then Underlight. Deepwater Horrors come out of both, so kill them as you go. "
        "Tell me if the two pits look alike to you.",
        "I think they're one hole. The same animals come out of both, and they come out wet, with "
        "a whole field of pits between them.\n\nI think there's water running under all of it, "
        "from the Throats to Underlight and on to the east. I can't prove that from up here."),
    "ab_everything_points_east": (
        "Bring Peska wet scales from the Deepwater Horrors at Underlight, kill Saltbone Revenants "
        "on the way, then ask her what points east.",
        "Sepp's found brine in the revenants. Hask's found water animals in shrike crops. Vizzi "
        "can't reach the bottom of two pits, and one of them has light coming out of it.\n\nI'm a "
        "surveyor, so I won't guess at a cause. I'll say it all runs toward the east, and I want "
        "one more set of samples before I write that. Bring me wet scales from the Deepwater "
        "Horrors at Underlight, in the southeast corner, and kill the Saltbone Revenants you meet "
        "on the way down. Then ask me what points east.",
        "It all points east, toward the Glittervein. That's the big pit with water in it, where "
        "the goblins have their camp. It wasn't there before the change either.\n\nSomebody over "
        "there should see my book. I can't leave the readings long enough to carry it."),
    "ab_four_carts": (
        "Kill the Cartfall Scavengers at Cartfall and bring Tobbit back the camp's stolen brass.",
        "Everything this camp owns has to fit on four carts, so we can pack up and leave in a "
        "day. We've done it twice. I didn't make the rule, but I was glad of it both times.\n\n"
        "Cartfall Scavengers have been stealing our spare brass fittings, and I can't replace "
        "brass out here. They take it back to Cartfall, west of camp. Kill them and bring the "
        "brass home.",
        "That's most of a cart's fittings. I can tell you what it's worth to the copper.\n\nPrices have been wild since the ground changed three years ago, and "
        "brass has been the worst."),
    "ab_a_short_pantry": (
        "Hunt Pitfall Kodo and Pit Shrikes around Cartfall for Marda's larder.",
        "A desert doesn't offer much to eat, and I've learned what there is over four camps. Most "
        "of our meat is Pitfall Kodo. Pit Shrike's good too, if you don't mind the plucking.\n\n"
        "You'll find both around Cartfall, west of here. The camp's larder is nearly empty, so "
        "kill some of each and I'll butcher them. I'll cook you a plate for it.",
        "You complained about it and you cleaned the plate. Most people do.\n\nSome of what goes "
        "in my pot came through three years ago, with everything else. There are plants in "
        "Tanaris now that shouldn't grow in a desert, and they stew well."),
    "ab_peg_irons": (
        "Kill Limestone Crawlers at the Wide Sink and bring Gorra their shell-plates to line the "
        "survey pegs.",
        "I shod kodo for nine years. Now I make iron tips for survey pegs. Limestone Crawlers "
        "chew those irons off the stakes, and nobody's told me why.\n\nI want to line the next "
        "batch with crawler shell and see if they'll leave it alone. Kill the crawlers at the "
        "Wide Sink, southwest of camp, and bring me their plates.",
        "These'll do. I tried it with a scrap of shell last month and the crawlers left that peg "
        "alone, so now I can line the whole batch.\n\nThe survey's stakes are going to be "
        "armoured with the animal that eats them. I'd like Peska to write that in her book."),
    "ab_three_month_contract": (
        "Kill the Saltbone Revenants and Sinkhole Lurkers along the Long Collapse, then ask Sepp "
        "why he stayed.",
        "I came out with the second camp on a three-month contract. That was two years and two "
        "camps ago. Nobody's brought the contract up since, and I haven't either.\n\nVizzi "
        "carries my glass sample jars down to the Throats, in the southwest, and her path runs "
        "along the Long Collapse. Saltbone Revenants and Sinkhole Lurkers hunt that path. Kill "
        "them so she can make the trip. Then ask me why I stayed, and I'll tell you.",
        "I stayed because I want to be here when somebody finds out what's draining this desert. "
        "Peska might get recalled, and Hask will follow the work.\n\nIt took me eight months to "
        "work that out. Thanks for clearing the path."),
    "ab_carry_the_book": (
        "Carry Peska Vane's collapse log to Ulla Stormhollow, the surveyor at Lastwater in the "
        "Glittervein.",
        "Go out by the east gate and down into the Glittervein. There's a camp at the bottom "
        "called Lastwater, and a tauren surveyor there named Ulla Stormhollow. She's been "
        "studying where the water went.\n\nI've got the date of every collapse since the first "
        "one, three years ago, and no idea what causes them. I'm told she has a cause and no "
        "dates. Take her my log. Ask me why I'm not going myself, if you want to know.",
        "Give me a moment to read this.\n\nShe's got dates. Every collapse, to the day, for three "
        "years. I've known what was happening all that time, and I've never had numbers to check "
        "it against.\n\nThere's been a goblin four days northwest of me writing them down, and "
        "neither of us knew about the other. I'll write her a reply myself.",
        "Three Years of Dates"),
    "ab_the_answer_comes_back": (
        "Carry Ulla's reply back to Chief Surveyor Vane at Fourth Peg, in the Abyssal Sands.",
        "I've written her four pages. The first three are sums she can check herself, because she "
        "won't trust the rest otherwise.\n\nThe fourth page says what's causing it, and she won't "
        "like it. Her pits will keep opening until somebody stops what's taking the water. Carry "
        "it back to Peska Vane at Fourth Peg, in the northeast corner of the Abyssal Sands. Ask "
        "me what's in it first, so you can answer her questions.",
        "I've read it twice. Give me a minute.\n\nThere's nothing wrong with the ground. Hask and I spent two years trying to find the fault in the rock, and the rock's sound. It "
        "was sitting on water, and the water's been draining out from under it since the change."
        "\n\nI've got to tell the camp. Then I've got to write to the port and tell them their road "
        "depends on whatever's at the bottom of the Glittervein."),
}

#: npc_id -> greeting
GREETINGS = {
    "ab_quartermaster":
        "I stock what a camp needs, as long as it fits on four carts.\n\nFour carts is what we "
        "can pack and move in a day. We've had to do that twice. I was glad of the rule both "
        "times, and I was the only one.",
    "ab_cook":
        "There are bedrolls under the awning and the pot's on. You get both with the posting."
        "\n\nI've fed this camp in four places and the food's got better each time. It took me a "
        "while to learn what a desert has to eat. There isn't much, but I know all of it now.",
    "ab_smith":
        "Bring me your gear before it breaks. There's no other forge between here and the port."
        "\n\nI shod kodo for nine years and there's nothing to shoe out here. These days I make "
        "peg irons and chain, and I mend whatever the crawlers have chewed.",
    "ab_reagents":
        "I mix everything thin, so the bottles survive the cart.\n\nI came out with the second "
        "camp on a three-month contract. That was two years and two camps ago. Nobody's mentioned "
        "the contract since, and I haven't either.",
    "ab_surveyor":
        "This is Fourth Peg. The peg's stood seven months, which is longer than the other three "
        "did.\n\nThe first fell in with the ground under it. The second's on the lip of the Wide "
        "Sink, marking ground that's gone. We moved the third because Hask didn't like the "
        "hardpan, and that spot fell in four days later.\n\nThe port at Steamwheedle pays me to "
        "find out if a road can be built across the Abyssal Sands. I don't know yet.",
    "ab_rodman":
        "I'm the one who stands at the far end holding the staff. Out here the far end's usually "
        "somewhere nobody's walked before.\n\nI like the work. I know that sounds odd.\n\nYou can "
        "read this ground if you go slowly. The hardpan sounds different over a hollow, and it's "
        "louder on a cold morning. Peska wants that written up as a method. Every time I try, it "
        "reads like guessing.",
    "ab_teamster":
        "I was driving the second cart at Nineteen Mile when the road went. The lead pair were "
        "six lengths ahead of me.\n\nThe cart went down and I fell off the back, and the ground I "
        "landed on held. I didn't do anything clever. I've told that story four hundred times."
        "\n\nI could hear the lead pair down there for a day and a half. So when the camp talks "
        "about the ground like it's weather, I go and stand somewhere else.",
    "ab_digger":
        "Somebody has to go down the pits on a rope and see if there's a floor. That's me.\n\n"
        "Nine of the eleven have floors. The Throats in the southwest and Underlight in the "
        "southeast don't, as far as my line reaches.\n\nPeska writes those up as 'no bottom "
        "observed'. I'd write 'don't go down'.",
}

#: quest item id -> tooltip
ITEM_TEXT = {
    "ab_lifted_brass": "Brass cart fittings, pried off the survey camp's spares.",
    "ab_sealed_waybill": "A cargo manifest with the seal unbroken, for a cart that went into a pit.",
    "ab_drovers_tag": "Stamped with a house mark and a number. The house is in Steamwheedle.",
    "ab_kodo_harness": "The strap's been cut. Somebody tried to get the animal out.",
    "ab_crawler_plate": "Thin and curved, and stronger than it looks.",
    "ab_second_peg_head": "The top few inches of a survey stake. You can still read the number.",
    "ab_ooze_residue": "What a Hollowing Ooze leaves behind after eating limestone.",
    "ab_fused_shard": "Sand that's melted into glass. It's warm to hold.",
    "ab_wet_scale": "It's been in a bag in the desert for a day and it's still damp.",
    "ab_salt_knuckle": "Cured in brine, four days' walk from the nearest salt.",
    "ab_lurker_spur": "A hooked spur for gripping a pit wall in the dark.",
    "ab_shrike_crop": "Whatever the bird ate last is still in it.",
}


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def patch_quests():
    p = ROOT / "data/quests/abyssal_sands.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    seen = set()
    for q in doc["quests"]:
        new = QUESTS.get(q["quest_id"])
        if not new:
            continue
        seen.add(q["quest_id"])
        q["description"], q["accept_text"], q["turn_in_text"] = new[:3]
        if len(new) > 3:
            q["title"] = new[3]
    missing = set(QUESTS) - seen
    assert not missing, f"quests not in the file: {sorted(missing)}"
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(seen)


def patch_greetings():
    done = set()
    for name, ascii_ in (("vendors", True), ("ambient_npcs", False)):
        p = ROOT / "data/npcs" / f"{name}.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        for key, rec in ((k, v) for d in _walk(doc) for k, v in d.items() if isinstance(v, dict)):
            if key in GREETINGS and "greeting" in rec:
                rec["greeting"] = GREETINGS[key]
                done.add(key)
        for rec in _walk(doc):
            nid = rec.get("npc_id") or rec.get("vendor_id") or rec.get("id")
            if isinstance(nid, str) and nid in GREETINGS and "greeting" in rec:
                rec["greeting"] = GREETINGS[nid]
                done.add(nid)
        p.write_text(json.dumps(doc, indent=2, ensure_ascii=ascii_) + "\n", encoding="utf-8")
    missing = set(GREETINGS) - done
    assert not missing, f"greetings not placed: {sorted(missing)}"
    return len(done)


def patch_roster():
    """Keep tools/abyssal_npc_roster.py saying what the data says, or the next sync undoes this."""
    p = ROOT / "tools/abyssal_npc_roster.py"
    src = p.read_text(encoding="utf-8")
    tree = ast.parse(src)
    edits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and k.value in GREETINGS and isinstance(v, ast.Tuple):
                g = v.elts[-1]
                edits.append((g.lineno, g.col_offset, g.end_lineno, g.end_col_offset, k.value))
    lines = src.split("\n")
    for l0, c0, l1, c1, nid in sorted(edits, reverse=True):
        lit = json.dumps(GREETINGS[nid], ensure_ascii=False)
        lines[l0 - 1:l1] = [lines[l0 - 1][:c0] + lit + lines[l1 - 1][c1:]]
    p.write_text("\n".join(lines), encoding="utf-8")
    assert len(edits) == len(GREETINGS), f"{len(edits)} roster greetings found"
    return len(edits)


def patch_items():
    p = ROOT / "data/creatures/quest_drops.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    done = set()
    for rec in _walk(doc):
        if rec.get("item_id") in ITEM_TEXT and "description" in rec:
            rec["description"] = ITEM_TEXT[rec["item_id"]]
            done.add(rec["item_id"])
    assert done == set(ITEM_TEXT), sorted(set(ITEM_TEXT) - done)
    raw = p.read_text(encoding="utf-8")
    ascii_ = "\\u" in raw
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=ascii_) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
    return len(done)


def main():
    print(f"quests reworded      {patch_quests()}")
    print(f"greetings reworded   {patch_greetings()}")
    print(f"roster kept in step  {patch_roster()}")
    print(f"item tooltips        {patch_items()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
