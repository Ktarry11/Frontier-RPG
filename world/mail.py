"""Mail: letters with money and items, kept on the party and saved with it (docs/auction_house_design.md, section 11).

Kyle, 15 Nov 2026: "maybe NPC auctioneers, MAILBOX and MAIL SERVICE". The auction house pays, refunds and hands
over everything by mail, the way WoW's does, and you can send things to your own recruits (in the party or on the
bench), which is how you hand gear to somebody benched without swapping them in.

Time is the market clock (world/market/market.py), in market hours. A letter from the auction house arrives at
once; a letter you send arrives an hour later.

A LETTER WITH MONEY OR ITEMS NEVER EXPIRES. WoW deletes them after thirty days, and in a game you put down for a
month that would be the auction house quietly eating the epic you won. Plain letters keep thirty market days.
"""
from world.market import goods as G

#: Most items one letter can carry (WoW's twelve).
MAX_ATTACH = 12
#: Copper postage per attached item; a letter with none still costs this once.
POSTAGE = 30
#: Market hours a sent letter takes to arrive.
SEND_DELAY = 1.0
#: Market hours a plain letter (no money, no items) is kept.
PLAIN_KEEP = 30 * 24
#: Market hours a cash-on-delivery offer waits before it goes back to the seller.
COD_KEEP = 3 * 24

#: kind -> icon in assets/ui/auction/icons/ (Kyle's sheet)
KIND_ICON = {
    "auction_won": "letter_auction", "auction_sold": "letter_coins", "outbid": "letter_coins",
    "auction_expired": "letter_returned", "auction_cancelled": "letter_returned", "returned": "letter_returned",
    "letter": "letter_sealed", "parcel": "parcel", "meme": "letter_sealed", "cod": "parcel",
}


class Letter:
    __slots__ = ("id", "sender", "subject", "body", "copper", "goods", "kind", "sent_at", "arrives_at", "read",
                 "can_return", "sender_kind", "to", "note", "cod")

    def __init__(self, sender, subject, body="", copper=0, goods=None, kind="letter", sent_at=0.0, arrives_at=None,
                 can_return=False, sender_kind="npc", to=None, note=None, cod=0):
        self.id = 0
        self.sender = sender
        self.subject = subject
        self.body = body
        self.copper = int(copper or 0)
        self.goods = list(goods or [])
        self.kind = kind
        self.sent_at = float(sent_at)
        self.arrives_at = float(sent_at if arrives_at is None else arrives_at)
        self.read = False
        self.can_return = bool(can_return)
        self.sender_kind = sender_kind
        self.to = to
        self.note = note
        #: Cash on delivery: what you pay to take the items. Kyle, 15 Nov 2026: "the seller can send you a Cash on
        #: Delivery of like.... 1-5 additional ones for cheap... I do this in WoW to cut out the AH cut myself".
        self.cod = int(cod or 0)

    @property
    def empty(self):
        return not self.copper and not self.goods

    @property
    def icon(self):
        if self.kind in ("letter", "meme") and self.goods:
            return "parcel"
        if self.kind in ("letter", "meme") and self.copper:
            return "letter_coins"
        return KIND_ICON.get(self.kind, "letter_sealed")

    def days_left(self, now):
        """Whole market days before a plain letter goes; None for one holding money or items."""
        if self.cod and self.goods:
            return max(0, int((self.arrives_at + COD_KEEP - now) // 24))
        if not self.empty:
            return None
        return max(0, int((self.arrives_at + PLAIN_KEEP - now) // 24))

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}

    @classmethod
    def from_dict(cls, d):
        x = cls(d.get("sender", "?"), d.get("subject", ""))
        for k in cls.__slots__:
            if k in d:
                setattr(x, k, d[k])
        x.goods = list(x.goods or [])
        return x


class Mailbox:
    """Every letter for the party. The player reads them; letters addressed to a recruit are delivered into that
    recruit's bags when they arrive (deliver_due)."""

    def __init__(self):
        self.letters = []
        self.next_id = 1
        self.outgoing = []          # letters you sent, on their way to a recruit

    # ------------------------------------------------------------ in
    def deliver(self, letter):
        letter.id = self.next_id
        self.next_id += 1
        self.letters.append(letter)
        return letter

    def visible(self, now):
        """Letters that have arrived, newest first."""
        out = [x for x in self.letters if x.arrives_at <= now + 1e-9]
        out.sort(key=lambda x: (-x.arrives_at, -x.id))
        return out

    def unread(self, now):
        return sum(1 for x in self.visible(now) if not x.read)

    def tidy(self, now):
        """Drop plain letters past their keep, and cash-on-delivery offers nobody paid for (the goods were the
        seller's all along). Never a letter with your money or your items in it."""
        self.letters = [x for x in self.letters
                        if not (x.empty and x.arrives_at + PLAIN_KEEP <= now)
                        and not (x.cod and x.goods and x.arrives_at + COD_KEEP <= now)]

    def pay_cod(self, letter, party, character):
        """(ok, message). Pay the seller and take everything in the letter."""
        if not letter.cod or not letter.goods:
            return False, "There's nothing to pay for."
        if party.copper < letter.cod:
            return False, "You don't have enough to pay for it."
        if not G.room_for(character, letter.goods):
            return False, "Your bags are full."
        party.remove_currency(letter.cod)
        paid = letter.cod
        letter.cod = 0
        n = 0
        while letter.goods:
            ok, _m = self.take_good(letter, 0, character)
            if not ok:
                break
            n += 1
        from entities.coins import coins
        return True, f"Paid {coins(paid)}. Took everything."

    def refuse_cod(self, letter):
        """Send a cash-on-delivery offer back unopened."""
        if not letter.cod:
            return False
        if letter in self.letters:
            self.letters.remove(letter)
        return True

    # ------------------------------------------------------------ taking
    def take_money(self, letter, party):
        if not letter.copper:
            return 0
        n = letter.copper
        party.add_currency(n)
        letter.copper = 0
        return n

    def take_good(self, letter, index, character):
        """(ok, message). The good goes into the character's bags or stays in the letter."""
        if letter.cod:
            return False, "Pay the cash on delivery first."
        if not (0 <= index < len(letter.goods)):
            return False, "There's nothing there."
        good = letter.goods[index]
        if not G.give(character, good):
            return False, "Your bags are full."
        letter.goods.pop(index)
        return True, f"Took {G.name(good)}" + (f" x{G.quantity(good)}" if G.quantity(good) > 1 else "") + "."

    def take_all(self, letter, party, character):
        if letter.cod:
            return 0, 0, bool(letter.goods)
        got = self.take_money(letter, party)
        taken = 0
        while letter.goods:
            ok, _msg = self.take_good(letter, 0, character)
            if not ok:
                break
            taken += 1
        return got, taken, bool(letter.goods)

    def delete(self, letter):
        """Only an empty letter can be thrown away: nothing is ever lost by a click."""
        if not letter.empty:
            return False
        if letter in self.letters:
            self.letters.remove(letter)
        return True

    def return_to_sender(self, letter, now):
        """A letter a recruit sent can go back to them. It leaves your mailbox with everything in it."""
        if not letter.can_return or letter.empty:
            return False
        self.letters.remove(letter)
        self.outgoing.append({"to": letter.sender, "goods": letter.goods, "copper": letter.copper,
                              "arrives_at": now + SEND_DELAY, "subject": "Returned: " + letter.subject})
        return True

    # ------------------------------------------------------------ sending to recruits
    @staticmethod
    def postage(n_goods):
        return POSTAGE * max(1, n_goods)

    def send(self, to_name, subject, body, goods, now):
        """Queue a parcel for a recruit. The caller has already taken the goods out of the bags and paid."""
        self.outgoing.append({"to": to_name, "goods": list(goods), "copper": 0, "arrives_at": now + SEND_DELAY,
                              "subject": subject, "body": body})

    def deliver_due(self, now, party, rng=None):
        """Put arrived parcels into the recruits' bags. A recruit whose bags are full sends it back to you."""
        import random
        rng = rng or random
        still = []
        people = {m.name: m for m in list(getattr(party, "members", [])) + list(getattr(party, "bench", []))}
        for p in self.outgoing:
            if p["arrives_at"] > now:
                still.append(p)
                continue
            who = people.get(p["to"])
            placed = []
            if who is not None and G.room_for(who, p["goods"]):
                for g in p["goods"]:
                    if G.give(who, g):
                        placed.append(g)
            leftover = [g for g in p["goods"] if g not in placed]
            if leftover or who is None:
                self.deliver(Letter(p["to"], "Returned: " + p.get("subject", ""),
                                    body=(f"{p['to']} couldn't carry it, so it came back." if who
                                          else "Nobody by that name could be found, so it came back."),
                                    goods=leftover or p["goods"], kind="returned", sent_at=now,
                                    sender_kind="recruit"))
            elif placed and rng.random() < 0.35:
                self.deliver(Letter(p["to"], "Re: " + (p.get("subject") or "your parcel"),
                                    body=rng.choice(RECRUIT_THANKS).format(name=p["to"].split()[0]),
                                    kind="letter", sent_at=now, sender_kind="recruit"))
        self.outgoing = still

    # ------------------------------------------------------------ save
    def to_dict(self):
        return {"letters": [x.to_dict() for x in self.letters], "next_id": self.next_id,
                "outgoing": self.outgoing}

    @classmethod
    def from_dict(cls, d):
        box = cls()
        box.letters = [Letter.from_dict(x) for x in (d or {}).get("letters", [])]
        box.next_id = int((d or {}).get("next_id", len(box.letters) + 1))
        box.outgoing = list((d or {}).get("outgoing", []))
        return box


RECRUIT_THANKS = [
    "Got it. Thanks. I'll put it to use, or at least I'll carry it around looking like I might.",
    "Arrived safe. You didn't have to, but I'm glad you did.",
    "Thanks for this. Next round's on me, assuming anybody in this world still sells a round.",
    "It fits. Mostly. I'm not sending it back.",
    "Received with thanks. Whoever packed it used a lot of string.",
    "That's kind of you. I'll try not to get it covered in anything awful. No promises.",
]
