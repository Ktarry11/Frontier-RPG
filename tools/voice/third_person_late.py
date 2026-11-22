"""The last third-person offers, in the giver's own voice (22 Nov 2026).

Kyle, 21 Nov 2026: no quests handed out in third person, and a story of five or six sentences. These were the
stragglers tools/audit_quest_voice.py's third-person check found after Azshara, Stonetalon and Deadwind, spread over
eight zones. Each zone's module (tools/voice/<zone>.py) merges its own block from here; the accept line is replaced too
whenever the live one would have pushed the description out of the offer window. Every fact, name and direction the
old narration had is kept.

THIRD = {zone stem: {quest_id: (description, accept_text or None)}}
"""

THIRD = {
    "scarlet_monastery": {
        "sm_the_monasterys_dead": (
            "I've buried half of Brill, and some of them twice. The burial ground at the Scarlet Monastery was "
            "Lordaeron's before it was the Crusade's, and the people lying in it were somebody's family. They don't "
            "rest any more. The Anguished Dead claw their way up out of the graves in the Forlorn Cloister, and the "
            "Haunting Phantasms drift among the stones. I want them laid down, gently if you can manage it, and any "
            "way you can if you can't.",
            "The Monastery's east of here, up the road. Go into the Graveyard, through the crypt chapel, to the open "
            "burial ground with the mausoleum.",
        ),
        "sm_hearts_of_zeal": (
            "I want to know what the Crusade puts in its faithful. The Scarlet Torturers and the Scarlet Scryers in the "
            "Monastery's Graveyard carry little vials of anointing oil. I think there's more in it than oil. Bring me "
            "the vials, and I'll find out what makes a man burn his neighbours and sing while he does it. I've seen "
            "what they do with it, and I'd like to know how.",
            "The Torturers and the Scryers keep to the halls and the Chamber of Atonement in the Graveyard. Don't "
            "drink any of it.",
        ),
        "sm_doans_codex": (
            "I collect what the living throw away, and Arcanist Doan has something I'd like very much. He's spent years "
            "in the Athenaeum at the top of the Monastery's Library, writing a codex of everything he's learned about "
            "the dead. It also covers how to end them, which is the part that worries me. I'd like to read it before "
            "Doan uses it on anyone else. Bring it to me, and I'll keep it out of the Crusade's hands for good.",
            "The Athenaeum's the hall of shelves at the north end of the Library. When Doan's close to dying, he'll "
            "try to take the room with him.",
        ),
        "sm_the_champion_of_the_hall": (
            "I keep a list of the Crusade's people who matter, and Herod is near the top of it. He's their champion, "
            "and he holds the Hall of Champions at the back of the Armory. Lately he's been sending his trainees down "
            "the road to Brill to practise. I want that to stop, and I don't much care how. Put him down, and the road "
            "will be quieter for everyone.",
            "The Hall of Champions is the last room of the Armory. Herod spins when he's angry, so keep moving, and "
            "don't stand in the doorway.",
        ),
        "sm_the_hounds_of_the_library": (
            "I lost two scouts on the Hillsbrad road last month, run down by Scarlet hounds. I tracked the hounds back "
            "to the kennels in the Monastery's Library, and to the man who breeds them, Houndmaster Loksey. I want "
            "Loksey dead, and his Scarlet Tracking Hounds with him. Their families deserve to hear that the dogs are "
            "gone. It's not much, but it's what I can give them.",
            "The kennels are in Huntsman's Cloister, at the top of the Library. Kill the hounds first, or they'll lick "
            "his wounds closed.",
        ),
        "sm_drilled_to_die": (
            "I keep finding Scarlet Soldiers dead in the hills, boys from Southshore who are barely old enough to lift "
            "a sword. The Crusade drills them in the Training Grounds of the Monastery's Armory. The man doing the "
            "drilling is one of the newcomers, a Sergeant Major Cole Brennan, and he's very good at it. I want Brennan "
            "dead and the yard emptied of Scarlet Soldiers. I'd rather fight soldiers than children.",
            "The Armory's the middle door, and the Training Grounds are the yard inside. Brennan calls recruits in "
            "waves, so guard your healer.",
        ),
        "sm_the_preacher_in_the_nave": (
            "I keep the Forsaken chapel in Tarren Mill, and I still pray, which makes me strange even here. I've heard "
            "about a preacher in the Scarlet Cathedral, Brother Corwin Ashe, one of the newcomers. He fills the nave "
            "every night and sends the faithful out to burn. Faith is the one thing I was allowed to keep, and I don't "
            "want to watch it used like that. Stop him, and I'll pray for him afterwards, because somebody should.",
            "The Cathedral's the right-hand door. Go up past the gardens into the Crusader's Chapel. His sermon "
            "shields him, so keep at him.",
        ),
        "sm_a_letter_for_brill": (
            "I've got a friend in Brill who isn't Forsaken and isn't Horde, and who's never once asked me what I am. His "
            "name's Flamewarden Teodor Novak. He watches the Scarlet Monastery for an order called the Pale Flame, and "
            "he needs people who can fight. I've written to him about you. I'd like you to carry the letter yourself, "
            "so he can see who I mean.",
            "Take the zeppelin from Orgrimmar to Tirisfal and walk down into Brill. Novak keeps a room over the inn, "
            "and he doesn't bite.",
        ),
        "sm_pages_for_sun_rock": (
            "I've read Doan's codex through, and one chapter has troubled me. Doan studied the dead that rise far from "
            "the Scourge, with no necromancer behind them, and he wrote down how it starts. I've heard the dead are "
            "rising like that in Mulgore. I've copied the chapter for Spiritwalker Tohana at Sun Rock Retreat, in "
            "Stonetalon, who watches that border. I'd like it carried to him, by someone who won't lose it.",
            "Take the zeppelin to Orgrimmar and a wind rider to Sun Rock. Tell Tohana the arcanist was wrong about a "
            "great deal, but not about this.",
        ),
    },
    "razor_hill": {
        "razorhill_thunder_ridge_approach": (
            "Thunder Ridge rises north-east of Razor Hill, a plateau where the thunder lizards nest and the air "
            "crackles before a storm that never quite arrives. I've sent recruits up there before. The ones who come "
            "back talk about how slow the lizards are, right up until a tail lands on something. I want the herd "
            "thinned. It's good practice for a fight where speed won't save you and only where you stand will.",
            None,
        ),
        "razorhill_supply_run": (
            "I'm still tallying what I lost before the Kolkar were dealt with. There's cargo scattered along the old "
            "caravan route that nobody ever recovered. Crates and bolts of cloth, worth real money to whoever collects "
            "them before they rot. I'm not proud of how long I've let it sit, but I've been busy. Money left on the "
            "ground is still money, and I'd rather it was mine.",
            "Bring back any crates you find along the western route, before the scavengers pick them over.",
        ),
        "razorhill_troll_refuge": (
            "I reached Razor Hill before da Darkspear camp on da Echo Isles had properly taken shape, and I've carried "
            "da guilt of it ever since. My kin are still lost to Zalazane's hex, and I found safe ground on da "
            "mainland. I can't go back myself, because an injury from da crossing never healed right. What I can do is "
            "ask someone capable to check on my people for me. Will you go in my place?",
            "Find Elder Kang'ari at da camp on da Echo Isles. Tell him Tal'rashi still thinks about dem every day.",
        ),
    },
    "moonglade": {
        "mg_something_to_grow": (
            "My grandmother grew chillies on a balcony in Chengdu, and I plant things in the Wakened's gardens because "
            "it's how I know where I am. The druids grow everything here without any help from me. I want something "
            "that's mine. I'd like a bed of Golden Sansam, which grows wild in the high places and nowhere in the "
            "glade. If you bring me some with the roots on, I'll do the rest.",
            "Golden Sansam grows in Felwood, Azshara and the high passes. Pick it with the roots on, and wrap it in "
            "damp moss.",
        ),
        "mg_the_black_gate": (
            "Behind the Black Gate of Jaedenar, the Shadow Council keeps a demon chained. Zar'gothrax the Unbound has "
            "been pulling at those chains since the worlds came together. The Circle has felt every pull in the roots "
            "of the glade, and so have I. I want the demon dead. I've waited three years for someone who could do it.",
            "Jaedenar's in the north-west of North Felwood, behind the Black Gate. Zar'gothrax is at the very bottom, "
            "so take friends you trust.",
        ),
        "mg_what_dies_in_deadwind": (
            "I can walk the Emerald Dream to almost anywhere in Azeroth. Since the worlds came together there's one "
            "place I can't reach, and that's Deadwind Pass. I want to know what's happening to the living things "
            "there. The deer of the pass will tell me, if you bring me what's left of them. The bone remembers what "
            "the animal dreamed, and I'll read it.",
            "The Dissolving Stags wander Deadwind West, coming apart a little more every day. Bring me their antlers.",
        ),
        "mg_the_totems_on_our_backs": (
            "When Thunder Bluff fell, those of us who reached Moonglade carried our lodges' totems up the mountain on "
            "our backs. I've kept them laid down ever since. The survivors built a memorial, and we've argued about it "
            "for three years. I'd like someone who wasn't there to stand at it and tell me what it looks like to a "
            "stranger. Tell me honestly whether it looks like a grave or a promise.",
            "The memorial's a short walk south-east of here, by the lodges, a cairn with feathers on it. Look at it "
            "properly, then come back.",
        ),
        "mg_the_thunder_bluff_road": (
            "I flew the Thunder Bluff road for twenty years before it fell. Elder Longtread at Camp Taurajo keeps the "
            "seat for Cairne Bloodhoof, and I've never been able to bring myself to fly him the list of who reached "
            "Moonglade. Archdruid Hamuul has written it out, every name. Someone has to carry it, and I can't. Will "
            "you take it to him for me?",
            "Camp Taurajo's in the Southern Barrens. Give Longtread the list, and tell him we looked, and that's "
            "everyone.",
        ),
        "mg_the_well_runs_over": (
            "Every night the great moonwell runs over by a finger's width, and every morning it's settled again. I've "
            "been writing down the times, and they match something on the lake. I can't watch both at once. I want "
            "someone at the end of the pier to watch the island while I watch the well. When the well rises, I'll "
            "know, and I think you'll know too.",
            "Go to the end of Nighthaven's pier and watch the island in the middle of the lake. Come back and tell me "
            "what you saw.",
        ),
        "mg_who_are_they_talking_to": (
            "I guard the Barrow Dens' door, and I've heard the sleepers inside answering someone. They aren't talking "
            "to each other, I'm sure of it. They're talking to someone else. I need a witness who isn't a warden, "
            "because the Circle will say a warden was only frightened. Stand at the door with me and listen, nothing "
            "more.",
            "Don't touch the thorns. If you hear it, you'll know, because it's the only voice in there that doesn't "
            "sound asleep.",
        ),
        "mg_the_fish_are_turning": (
            "I've fished Lake Elune'ara my whole life, and the fish have started turning toward the island at night. "
            "All of them turn, the way a field of flowers turns to the sun. My mother fished this lake, and her mother "
            "before her, and neither of them ever saw it. I want someone else to see it, so I know I'm not imagining "
            "it. The falls are where the water's clearest.",
            "The Falls of Elune'ara come down on the north shore. Stand where the spray settles and look into the "
            "water.",
        ),
        "mg_the_same_dream": (
            "I keep a book for my guests to write in, and for the last month half of them have written down the same "
            "dream. It's a door under water, and a stair going down. These are people who've never met, writing the "
            "same thing in their own words. I want Dr. Sandvik to see it, because she's the only one in the glade who "
            "collects dreams on purpose. Take it round the lake to her for me.",
            "It's all in the back half of the book. Take it round the lake to the doctor, she'll want it more than I "
            "do.",
        ),
        "mg_seedlings_for_the_sanctuary": (
            "I grow seedlings from the glade's oldest trees, and the Emerald Reclamation in Felwood has asked for "
            "them. They want to plant them where the fel has been burned away. Moonglade's soil is the cleanest in "
            "Kalimdor, and the Sanctuary needs every bit of it. I've packed a tray, and it needs carrying carefully. "
            "Will you take it down for me?",
            "Fly down to the Emerald Sanctuary in South Felwood and give the tray to Arch Druid Aelyra Moonbough. Keep "
            "them away from Felwood's water.",
        ),
    },
    "hillsbrad_dungeons": {
        "dg_morgrin": (
            "There's a door at the back of the Great Hall that the Stormpike keep shut, and a shrine-keeper standing "
            "in front of it who's made it his life's work. Nobody in the garrison will say what's behind it. I've "
            "asked three times, and three times I've been told to mind my own business. I've decided their silence is "
            "the answer. Get that door open, and we'll find out what they're so careful about.",
            None,
        ),
    },
    "feralas": {
        "fe_raise_it_here": (
            "I've raised the Bloodhoof totem beside Mojache's great totem. Raising it here means we've stopped waiting "
            "to go home. I didn't think I'd ever be ready for that, and I'm still not sure I am. I want the camp to "
            "see someone from outside it standing with us, so they know it isn't only the refugees who mourn. Come "
            "and stand with us at the great totem tonight.",
            "Come to the great totem tonight. You don't have to say anything, only stand with us.",
        ),
        "fe_the_rattles_go_quiet": (
            "With their snares gone, the Woodpaw have pulled back to their camps, and their Woodpaw Mystics are "
            "shaking their rattles all night. I know what that means, because I've heard it before. They're working "
            "themselves up to come back. When the Mystics start rattling, the Woodpaw Brutes come down the hill a "
            "night later. I'd rather we went up first.",
            "Break up the camp before they're ready.",
        ),
        "fe_warm_roots": (
            "I came from Moonglade to the Dream Bough, a great tree whose roots reach into the Dream. They've been "
            "restless since the merge. The stones of the Dreaming Arch at Moonglade have been warm at night for "
            "months, and the Bough's roots touch the same Dream. I want to know whether these roots are warm too. Go "
            "and lay your hand on them tonight, and tell me.",
            "Lay your hand on the Bough's roots tonight, and tell me whether they're warm.",
        ),
        "fe_tell_moonglade": (
            "I've written to Dreamwatcher Lethiel at Moonglade's Dreaming Arch. The roots are warm, the guardians are "
            "dreaming badly, and the giants are walking. She needs to hear all of it, and soon. I can't leave the "
            "Bough while it's like this. Take her my letter, and she'll know what it means, or she'll know who to "
            "ask.",
            "Lethiel sits with the Dreaming Arch in Moonglade's north woods. Take her my letter.",
        ),
    },
    "middle_boughs": {
        "mbq_sealed_for_now": (
            "I want you to stand at the Heartwood Hollow behind Heartwatch and listen, so you know what the watch is "
            "for. The shadow hunters sealed it, and nobody goes in until the tribes say so. It's the split behind me. "
            "Put your ear to the seal, but don't touch it. Then come back and tell me what you heard.",
            "Go and stand at the split behind me and put your ear to the seal. Don't touch it, only listen.",
        ),
    },
    "anchorfields": {
        "afq_engine_seven": (
            "The seventh engine in the Gearwork fed the Third Anchor for nine hundred years. Last month it pulled "
            "itself off its mount and started walking. I call it Engine Seven, and now it's tearing into the other "
            "engines as if it's looking for something. I've tended these engines my whole life, and I've never seen "
            "one do that. Stop it, before it reaches the First Anchor's feed.",
            "Engine Seven's loose in the Gearwork. Stop it before it reaches the First Anchor's feed.",
        ),
    },
    "fading_firmament": {
        "ffq_the_flagship_wardens": (
            "The general won't leave the Moorage now, not this close to sailing. Her Flagship Wardens hold the "
            "gangway, and her Ascendant Battlemages hold the pier. I want the way cleared. If you clear them off, "
            "she'll have to come out and see to it herself, because she always does. I'll be there when you face "
            "her.",
            "Clear her Wardens off the gangway and her Battlemages off the pier, and she'll come down to see why.",
        ),
    },
}


def merge(zone, voice):
    """Fold THIRD[zone] into a zone's VOICE: description and (when given) accept line replaced, turn-in kept."""
    for qid, (d, a) in THIRD.get(zone, {}).items():
        old = voice.get(qid, (None, None, None))
        voice[qid] = (d, a if a is not None else old[1], old[2])
    return voice
