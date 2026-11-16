"""Who's writing: eight trader personalities, each with their own letters for every auction-house moment.

Kyle, 15 Nov 2026: "Give MULTIPLE people with MULTIPLE personalities lol". A trader keeps one personality for good
(picked from their name, leaning on their race: goblins mostly hustle, the Forsaken are dry or litigious, tauren
are gentle), so the same seller always sounds like themselves. meme_mail.py's shared pools stay as a fallback and
for the moments that have no personality lines.

Two or three sentences at most. Placeholders: {item} {paid} {meant} {n} {each} {you}.
"""
import zlib

PERSONALITIES = ["wailer", "grump", "gentle", "hustler", "deadpan", "sunshine", "lawyer", "bro"]

#: race -> the personalities it leans toward (the rest of the time it's any of the eight)
LEANS = {
    "goblin": ["hustler", "hustler", "lawyer", "sunshine"],
    "forsaken": ["deadpan", "deadpan", "lawyer", "wailer"],
    "undead": ["deadpan", "deadpan", "lawyer", "wailer"],
    "tauren": ["gentle", "gentle", "sunshine", "deadpan"],
    "orc": ["grump", "grump", "bro", "wailer"],
    "troll": ["bro", "sunshine", "hustler", "grump"],
    "blood_elf": ["lawyer", "wailer", "deadpan", "hustler"],
}


#: one line for the seller tooltip, so you can tell who you're dealing with before you deal with them
BLURB = {
    "wailer": "Takes every sale personally.",
    "grump": "Short with everybody.",
    "gentle": "Soft-spoken and fair.",
    "hustler": "Always has a deal for you.",
    "deadpan": "Dry as a crypt.",
    "sunshine": "Unreasonably cheerful.",
    "lawyer": "Writes everything down.",
    "bro": "Calls everyone bro.",
}


def personality_for(name, race=None):
    h = zlib.crc32(str(name).encode("utf-8"))
    lean = LEANS.get(str(race or "").lower())
    if lean and h % 10 < 7:
        return lean[(h // 10) % len(lean)]
    return PERSONALITIES[(h // 7) % len(PERSONALITIES)]


LINES = {
    # ------------------------------------------------------------------ you scooped their fat finger
    "fat_finger": {
        "wailer": [
            "WHY would you do this to me? I meant {meant} for {item}, not {paid}, and now I am lying in the road.",
            "I have wept three times since breakfast and every one of them was about {item}.",
            "Do you know what {paid} buys? Nothing! A sad apple! I sold you {item} for a sad apple!",
            "Tell my family I tried. Tell them about the decimal point. Tell them everything.",
        ],
        "grump": [
            "You. {item}. {paid}. Give it back or I find you.",
            "I hit the wrong key. You hit the buy button. One of us is a thief and it isn't me.",
            "That was supposed to be {meant}. I hope it pinches.",
            "Enjoy it. I'll be at the inn breaking a table.",
        ],
        "gentle": [
            "I think I made a mistake with {item}. It's all right. I hope it serves you well.",
            "I meant to ask {meant}, but the wind took the decimal. If you ever want to make it right, I'd be grateful.",
            "No hard feelings. The Earth Mother gives and the auction house takes, mostly from me.",
            "It was a good {item}. Look after it, friend.",
        ],
        "hustler": [
            "Okay, okay, you got me. {paid} for {item}. I'll buy it back at {meant}, no questions, best deal you'll get all week.",
            "Listen, pal. That listing was a clerical error and I've got a cousin in clerical errors. Let's talk.",
            "I respect the hustle. I hate it, but I respect it. How about I sell you something else, full price, as an apology to me?",
            "Rule one of the Cartel: never list tired. I listed tired. You win this one.",
        ],
        "deadpan": [
            "I listed {item} for {paid}. I meant {meant}. I've been dead for six years and this is the worst thing that's happened to me.",
            "My hands don't work as well as they used to. Some of the fingers are elsewhere. That's my excuse.",
            "Congratulations on {item}. I'd cry, but the ducts went years ago.",
            "Keep it. I have eternity to earn it back, and you don't.",
        ],
        "sunshine": [
            "Yay, somebody bought my {item}! Wait, was that really the price? Oh well, enjoy it!",
            "I'm so glad {item} went to a good home! I'm a little sad it went for {paid}, but mostly glad!",
            "Hi! I think I put the wrong number on {item}! Silly me! Anyway, hope you love it!",
            "Fun fact, I meant {meant}! Less fun fact, I got {paid}! Have a great day!",
        ],
        "lawyer": [
            "Re: {item}. Please be advised the listing price of {paid} was a clerical error. My client, me, requests its return at once.",
            "Under Steamwheedle trading law, section who-cares, a sale made in obvious error may be contested. I am contesting it, in writing, right now.",
            "Pursuant to our recent transaction, you owe me the difference of {meant} less {paid}. Kindly remit.",
            "This letter is a formal notice of extreme displeasure. Further notices will follow, probably.",
        ],
        "bro": [
            "Bro wtf! I didn't mean to sell {item} for {paid}! It was supposed to be {meant}!",
            "Broooo. {paid}?? You couldn't have left it up for like one minute so I could fix it?",
            "Okay bro, real talk, how fast were you? It was up for like four seconds.",
            "Not even mad bro. Okay a little mad. Enjoy the {item}.",
        ],
    },
    # ------------------------------------------------------------------ cash on delivery after you bought a lot
    "cod": {
        "wailer": [
            "I saw you buying {item} and I thought, finally, somebody who understands me. {n} more at {each} each. Please don't leave me.",
            "My bags are so heavy with {item}, and my heart is heavier. {n} for {each} each, cash on delivery.",
            "Take them. {n} {item} at {each}. I can't look at them any more.",
        ],
        "grump": [
            "You want {item}. I have {n}. {each} each. Pay or send it back.",
            "COD on the letter. {n} {item}, {each} apiece. Don't haggle.",
            "Saw you buying. Got more. {each}. Done.",
        ],
        "gentle": [
            "I noticed you need {item}. I have {n} more I can spare at {each} each, if it helps.",
            "No auction house cut between friends. {n} {item}, {each} each. Only if you want them.",
            "I gathered these with care. {n} {item} at {each} each, cash on delivery.",
        ],
        "hustler": [
            "Pal! Buddy! You're buying {item}, I'm selling {item}. {n} at {each}, no house cut, everybody wins except the house.",
            "Exclusive offer for preferred customers, meaning you. {n} {item}, {each} each. Price goes up tomorrow.",
            "Why pay the block when you can pay me? {n} {item}, {each} a piece. Cash on delivery, cash on the barrel.",
        ],
        "deadpan": [
            "You've been buying {item} like you're going to live forever. I'd know. {n} more at {each} each.",
            "{n} {item}. {each} each. I don't sleep, so I had time to gather them.",
            "Here are {n} {item} at {each} each. Pay or don't. I have nowhere to be.",
        ],
        "sunshine": [
            "Hi! You like {item}! I like {item}! Here's {n} more for {each} each, isn't that fun!",
            "Surprise! {n} {item} at {each} each! Pay the cash on delivery and they're yours!",
            "I had extra {item} and thought of you! {each} each! Have the best day!",
        ],
        "lawyer": [
            "Offer of sale: {n} units of {item} at {each} per unit, payable on delivery. Offer expires in three days.",
            "Please find enclosed {n} {item}. Remit {each} per unit to accept. Silence will be read as a no.",
            "By private treaty and outside the auction house's jurisdiction: {n} {item}, {each} each.",
        ],
        "bro": [
            "Yo bro, saw you buying {item}. I got {n} more, {each} each, no AH cut. Hook it up.",
            "Bro, {n} {item} at {each} each, cash on delivery. Let's go.",
            "Cutting out the middleman bro. {n} {item} at {each}. You're welcome.",
        ],
    },
    # ------------------------------------------------------------------ you listed too cheap and they sniped it
    "sniped_you": {
        "wailer": [
            "Your {item} at {paid}! I nearly fainted! I bought it before I could stop myself, and now I feel so guilty, but also rich.",
            "I'm going to relist your {item} at {meant} and I want you to know it hurts me more than it hurts you.",
        ],
        "grump": [
            "Bought your {item}. Check your prices.",
            "Thanks for the cheap {item}. Do it again.",
        ],
        "gentle": [
            "I think your {item} was priced by mistake. I bought it so nobody worse would. You can have it back for what I paid.",
            "Please check your listings, friend. Somebody else would not have written to tell you.",
        ],
        "hustler": [
            "{item} for {paid}? Pal, I'd frame that listing if I wasn't busy selling it again at {meant}.",
            "Thank you for your business, and by business I mean your mistake.",
        ],
        "deadpan": [
            "Your {item} was very cheap. Now it's mine. That's the auction house.",
            "I bought your {item}. I'd say I'm sorry, but I haven't felt sorry since the plague.",
        ],
        "sunshine": [
            "I got your {item} for {paid}! What a lucky day! Is it a lucky day for you too?",
            "Thank you so much for the {item}! You're so generous!",
        ],
        "lawyer": [
            "Receipt: one {item}, {paid}, purchased in good faith. No refunds. Kind regards.",
            "Please note that a listing is a binding offer. Yours bound you to {paid}.",
        ],
        "bro": [
            "Bro your {item} was {paid}. I couldn't not. Respect though.",
            "Thanks for the {item} bro. Check your zeroes next time.",
        ],
    },
    # ------------------------------------------------------------------ you keep undercutting them
    "undercut_salt": {
        "wailer": [
            "Every time I post {item}, you're there, one copper under. Is this how it ends? Is this my life now?",
            "I've stopped selling {item}. I've stopped selling anything. I just sit and watch your listings.",
        ],
        "grump": [
            "One copper. You undercut me by ONE COPPER. Do it again and see.",
            "Stay off my {item}.",
        ],
        "gentle": [
            "I see we both sell {item}. There's room for both of us, I think, if we're both fair.",
            "Your price on {item} is lower than mine. Mine feeds my family. I just thought you should know.",
        ],
        "hustler": [
            "Let's make a deal. You stay off {item}, I stay off whatever you sell next. Shake on it?",
            "Undercutting me on {item}? Cute. I've been undercut by better goblins than you. Actually you're not a goblin, which makes it worse.",
        ],
        "deadpan": [
            "You undercut me on {item} again. I'll outlive you. Then the market's mine.",
            "Funny how my {item} stopped selling when you showed up. I don't laugh any more, but it's funny.",
        ],
        "sunshine": [
            "Hi! We both sell {item}, so we should be friends! Could you maybe stop undercutting me though?",
            "Your {item} is so cheap! Mine was cheap too, until yours was cheaper! Ha!",
        ],
        "lawyer": [
            "Cease and desist undercutting my client's {item}. My client is me.",
            "Your pricing of {item} constitutes, in my professional opinion, a nuisance.",
        ],
        "bro": [
            "Bro, EVERY time, one copper under on {item}. Do you even sleep?",
            "Bro let me sell ONE {item}. Just one.",
        ],
    },
    # ------------------------------------------------------------------ they undercut you and want you to know
    "undercut_smug": {
        "wailer": ["I'm so sorry I went under your {item}. Truly. Deeply. Financially, not at all.",
                   "I had to undercut your {item}, I simply had to. Forgive me."],
        "grump": ["Your {item}. Mine's cheaper.", "Saw your price on {item}. Laughed."],
        "gentle": ["I priced my {item} a little under yours. I hope you don't mind. I really need the coin.",
                   "Sorry about the {item}. The market is the market."],
        "hustler": ["Nothing personal about the {item}. Okay, it's a little personal.",
                    "Your {item} price was a gift, and I'm a gift-receiving kind of goblin."],
        "deadpan": ["I undercut your {item}. Someone had to.", "Your {item} was overpriced. Mine is merely priced."],
        "sunshine": ["Hi! I put my {item} up just under yours! Good luck to us both!",
                     "Guess what, my {item} is cheaper than yours! Isn't trading fun!"],
        "lawyer": ["Notice: my {item} is now listed below yours. This is legal. I checked.",
                   "For your records, your {item} has been undercut."],
        "bro": ["Sorry bro, had to go under on {item}. Business.", "Your {item} bro. Mine's cheaper. Gg."],
    },
    # ------------------------------------------------------------------ you outbid a collector
    "outbid_them": {
        "wailer": ["You took the {item} from me in the final hour. I'll never love another {item} again.",
                   "Two days I watched that {item}. Two days! And you swooped in like a vulture in a hat."],
        "grump": ["You outbid me on {item}. I'll remember your name.", "Last-second bid on {item}. Classy."],
        "gentle": ["You won the {item}. I hope it brings you more joy than it would have brought me.",
                   "Well bid on the {item}, friend. It went to someone who wanted it more."],
        "hustler": ["You beat me to the {item}. Want to sell it to me for a modest markup? Very modest. Huge.",
                    "Well played on the {item}. I'll be watching your auctions now. Purely professionally."],
        "deadpan": ["You won the {item}. I wanted it for my coffin. I'll make do.",
                    "Outbid at the end. I'm used to losing things. Mostly organs."],
        "sunshine": ["Aw, you won the {item}! Congratulations! I'll just be over here, crying happy tears!",
                     "You got the {item}! I'm so happy for you! I'm also very sad! Both!"],
        "lawyer": ["Regarding the {item}: I dispute the timing of your bid and reserve all my rights.",
                   "Please be advised I intended to win the {item} and am noting your interference."],
        "bro": ["Bro you sniped my {item} at the buzzer. Cold.", "Gg on the {item} bro. Rematch."],
    },
    # ------------------------------------------------------------------ a rival outbid you and gloats
    "outbid_you": {
        "wailer": ["I had to have the {item}. I'm sorry. I'm not sorry. I'm so conflicted.",
                   "The {item} called to me. It called louder than your bid."],
        "grump": ["Was that your bid on {item}? Weak.", "My {item} now. Go home."],
        "gentle": ["I outbid you on the {item}. I hope there's another one out there for you.",
                   "Sorry about the {item}. I needed it for my mother."],
        "hustler": ["Thanks for warming up the {item} for me, pal.", "Never bid against a goblin who's had coffee."],
        "deadpan": ["My bid on {item} was higher. Like my body count.", "I outbid you. Try being dead, it's very freeing."],
        "sunshine": ["I outbid you on {item}! Sorry! Not really! Kind of!", "Yay, I got the {item}! You were close though!"],
        "lawyer": ["Please note my bid on {item} now supersedes yours. Regards.", "Your bid on {item} has been lawfully exceeded."],
        "bro": ["Outbid you on {item} bro. Gotta be quicker.", "My {item} bro. Better luck next time."],
    },
    # ------------------------------------------------------------------ the seller is just happy it sold
    "won_thanks": {
        "wailer": ["You bought my {item}! Someone finally sees me!", "My {item} found a home. I'm overwhelmed."],
        "grump": ["You bought my {item}. Good.", "Sold. Don't break it."],
        "gentle": ["Thank you for buying the {item}. Look after it.", "I'm glad the {item} went to you."],
        "hustler": ["Pleasure doing business! Tell your friends! Tell your enemies, they pay better!",
                    "You bought my {item}. Want another? I have, theoretically, a lot."],
        "deadpan": ["You bought my {item}. I'm as happy as I get, which is not very.",
                    "Thanks for the coin. I'll spend it on nothing, slowly."],
        "sunshine": ["You bought my {item}! Thank you thank you thank you!", "Yay! The {item} is yours! Have fun with it!"],
        "lawyer": ["This letter confirms the transfer of {item}. Thank you for your business.",
                   "Sale of {item} complete. Please retain this letter for your records."],
        "bro": ["Thanks for grabbing the {item} bro.", "Bro you bought my {item}. Legend."],
    },
}


def write(pool, personality, rng, **fields):
    """(subject, body) in this personality's voice, or None when it has no lines for this moment."""
    lines = (LINES.get(pool) or {}).get(personality)
    if not lines:
        return None
    from world.market.meme_mail import SUBJECTS
    body = rng.choice(lines)
    subj = rng.choice(SUBJECTS.get(pool, ["{item}"]))
    try:
        return subj.format(**fields), body.format(**fields)
    except (KeyError, IndexError):
        return subj, body


def count():
    return sum(len(v) for p in LINES.values() for v in p.values())
