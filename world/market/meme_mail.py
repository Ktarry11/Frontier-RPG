"""Letters from the other traders: the auction house's human side (docs/auction_house_design.md).

Kyle, 15 Nov 2026: "I'd pay good money for meme mail if you get a fat finger seller and scoop his item", then
"Should have like.... I dunno, 50 or so mails that can be sent....only like 2 to 3 sentences max per mail....
sometimes simple stuff like 'Bro wtf! I didn't mean to sell it for x'".

They come SOMETIMES, never every time, or they stop being funny: the chances are in market.py next to the moment
that sends them. Each pool is picked from at random. Placeholders:

    {item}    the thing         {paid}   what you paid or bid       {meant}  what they meant to ask
    {you}     your name         {name}   the sender's first name
"""

#: You bought out a fat-fingered listing. From the seller.
FAT_FINGER = [
    "Bro wtf! I didn't mean to sell {item} for {paid}. I meant {meant}. Please.",
    "You absolute vulture. That was supposed to be {meant}. I hope it gives you a rash.",
    "Hi. Small thing. I may have left out a couple of zeroes on {item}. Any chance you'd sell it back for what you paid? No? Cool. Cool cool cool.",
    "I've been staring at the decimal point for an hour. It's still in the wrong place. You're a monster and I respect it.",
    "{paid}. For {item}. I'm going to go lie face down in the Barrens for a while.",
    "My cat walked across the counting machine. That's my story and nobody can prove otherwise. Enjoy your {item}.",
    "Listen, I'll give you {meant} for it back. That's what it's worth! That's literally the price I meant to put!",
    "Do you just sit at the auction house all day waiting for people to make mistakes? Asking because I'd like to hire you.",
    "Congratulations on {item}. I have informed my ancestors. They are disappointed in both of us.",
    "That listing was a test. You passed. Please return the {item} to collect your prize, which is my gratitude.",
    "Bro. Bro. {paid}?? You couldn't have left it up for one minute so I could fix it?",
    "I clicked post and felt my soul leave my body. Then I watched it sell. Then my soul left again.",
    "Not mad. Just wanted you to know I'm thinking about you. Every day. Forever. Enjoy the {item}.",
    "My accountant says I'm not allowed to use the auction house anymore. I hope you're happy.",
    "Fine. Keep it. But if you ever list anything I want, I'm buying it out of spite at full price, and you'll never know it was me.",
    "I was going to retire on what {item} sold for. Now I'm going to retire on {paid}. That's about one sandwich.",
    "Okay, real talk, how fast were you? It was up for like four seconds.",
    "Somewhere a goblin is laughing at me and I think it's you.",
    "The {item} was my grandfather's. Not really, but I needed to see if that would work. Did it work?",
    "Gg. Well played. I hate it here.",
    "...nice.",
    "Tell me honestly. Did you actually need {item}, or did you just see the price and black out?",
]

#: You listed something far too cheap and a flipper snapped it up. From the flipper.
SNIPED_YOU = [
    "Thanks for the {item}! I'll put it back up at {meant} tomorrow. No hard feelings, right?",
    "Hey, I just want you to know your mistake paid for my new boots. They're very comfortable.",
    "Saw {item} for {paid} and I've never moved faster in my life. You should check your decimals, friend.",
    "Heads up, I think you priced {item} wrong. Don't worry, I fixed it for you by buying it.",
    "Pleasure doing business. Please keep pricing things like that. I'll be watching.",
    "I was going to write something nice but I'm too busy relisting your {item}.",
]

#: Somebody you keep undercutting finally writes to you.
UNDERCUT_SALT = [
    "Every time. Every single time I post, there you are, one copper under. Do you sleep?",
    "One copper. You undercut me by ONE COPPER. Is that what we're doing now?",
    "I see what you're doing with the {item} market and I want you to know I'm taking it personally.",
    "I'll go down to cost if I have to. I'll go under cost. I have nothing left to lose but my dignity, and that's already gone.",
    "Funny how my {item} stopped selling right when you showed up. Real funny.",
    "Let's make a deal. You stay off {item}, I stay off whatever you sell next. Shake on it?",
]

#: An undercutter just went under you, and wants you to know.
UNDERCUT_SMUG = [
    "Saw your {item}. Cute price. Mine's cheaper.",
    "Nothing personal about the {item}. Okay, it's a little personal.",
    "Sorry about your {item} listing. Not that sorry.",
]

#: You outbid a collector on something they wanted.
OUTBID_THEM = [
    "I'd been watching that {item} for two days. Two days! Enjoy it, I guess.",
    "Outbid at the last minute. Classy. I'll remember your name.",
    "Fine. Take the {item}. I didn't want it anyway. That's a lie, I wanted it very much.",
    "You know there are other {item}s out there, right? You didn't have to take mine.",
    "I hope you know I was going to give that to my mother.",
    "Wow. Okay. Big spender over here.",
]

#: An NPC outbid you, and gloats about it.
OUTBID_YOU = [
    "Sorry, I needed that {item} more than you did. Better luck next time.",
    "Was that your bid on {item}? Adorable.",
    "Nice try on the {item}. My purse is deeper than yours.",
    "Don't take it hard. Bidding wars aren't for everybody.",
]

#: You bought something your own recruit had listed. From the recruit.
RECRUIT_SOLD_TO_YOU = [
    "You know you could have just asked me for the {item}, right? Thanks for the coin though.",
    "I can't believe you bought my {item}. We're in the same party. We share a purse. What are we doing.",
    "Thanks for buying the {item}! I'm going to spend the money on something for the group. Probably. Maybe.",
    "Did you buy my {item} as a joke or did you not know it was me? Either way, I'm keeping the money.",
]

#: You won an auction with a bid and the seller is just happy it sold.
WON_THANKS = [
    "Glad the {item} went to somebody who'll use it. Look after it.",
    "Thanks for the bid! That {item} had been sitting in my bags forever.",
    "Pleasure doing business. If you need more, you know where to find me.",
]

#: You've been buying a lot of one thing; a seller offers more by cash on delivery. Kyle, 15 Nov 2026: "Ama notices
#: you're buying healing potions at like....20s per potion and you buy 10....She sends you mail with an additional 5
#: giving you the option to buy them for 10s each". Extra placeholders: {n} how many, {each} the price each.
COD_OFFER = [
    "Saw you buying up {item}. I've got {n} more I'll let go for {each} each, no auction house cut. Cash on delivery's on the letter.",
    "You're going through {item} like it's free. Here's {n} more at {each} apiece. Pay the COD if you want them, send it back if you don't.",
    "I make {item} and you clearly need {item}. {n} for {each} each, straight from me. The auction house can find its own lunch.",
    "Psst. {n} {item}, {each} each. Cheaper than the block and nobody has to know.",
    "Whatever you're doing with all that {item}, I support it. Have {n} more at {each}. COD attached.",
    "Bought a stack of mine earlier, didn't you? I've got {n} left over. {each} each and they're yours.",
    "My bags are full and you look like a buyer. {n} {item} at {each} each. Last offer, mostly.",
    "Cutting out the middleman. {n} {item}, {each} each, cash on delivery. Pleasure doing business, probably.",
]

ALL = {"cod": COD_OFFER, "fat_finger": FAT_FINGER, "sniped_you": SNIPED_YOU, "undercut_salt": UNDERCUT_SALT,
       "undercut_smug": UNDERCUT_SMUG, "outbid_them": OUTBID_THEM, "outbid_you": OUTBID_YOU,
       "recruit_sold": RECRUIT_SOLD_TO_YOU, "won_thanks": WON_THANKS}

SUBJECTS = {
    "cod": ["more {item}?", "{item}, cheap", "a private offer", "saw you buying"],
    "fat_finger": ["about that {item}", "WAIT", "please", "re: {item}", "the decimal point"],
    "sniped_you": ["thanks!", "re: your {item}", "a small favour"],
    "undercut_salt": ["one copper", "re: {item}", "we need to talk"],
    "undercut_smug": ["{item}", "hi neighbour"],
    "outbid_them": ["re: {item}", "really?"],
    "outbid_you": ["{item}", "better luck next time"],
    "recruit_sold": ["re: {item}", "uh"],
    "won_thanks": ["{item}", "thanks"],
}


def write(pool, rng, **fields):
    """(subject, body) from a pool, filled in."""
    body = rng.choice(ALL[pool])
    subj = rng.choice(SUBJECTS[pool])
    safe = {k: v for k, v in fields.items()}
    try:
        return subj.format(**safe), body.format(**safe)
    except (KeyError, IndexError):
        return subj, body
