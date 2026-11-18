"""The market: listings, prices, traders, buyers, bids, undercuts, snipes, fat fingers and the clock.

docs/auction_house_design.md is the plan and explains every number here. The short version:

* Two books, Horde (Orgrimmar, Undercity, Freewind Post) and Steamwheedle (the goblin ports), on one market clock
  measured in market hours. The clock moves with play time (1 hour per 150 s), quests (+1), the last boss of a
  dungeon (+6) and the hearthstone (+8). Kyle: "we need to ensure the inn isn't cheeseable... +8 when we HEARTH
  only. and +6 dungeon when LAST boss is killed."
* Every key has a price index I, a mean-reverting random walk (an Ornstein-Uhlenbeck process in ln I) that is
  hard-clamped to [0.35, 3.0]: "the market can go up and down but it never goes to infinity and never crashes to
  nothing". The going price is fair value x I.
* Buyers arrive at the key's demand rate, each with a reservation price R = going x e^(sigma Z), capped at 2.5x
  going, and buy the CHEAPEST auction at or under R. So undercuts steal sales, fair prices sell and greed never
  does.
* Traders are the world's own NPCs and unrecruited recruits, each with a habit. Undercutters jump your listings
  sometimes, flippers snipe anything far too cheap (including fat fingers and your own mistakes), collectors fight
  you for epics, casuals list nonsense.
* Your recruits list their own loot after a dungeon. Kyle: "it'd be surreal if you're in the AH and the priest in
  your party puts up stuff for sale".

Nothing here touches the screen. The party owns one Market (party.market) and one Mailbox (party.mail); everything
the market pays out or hands back goes through the mail, the way WoW does it.
"""
import json
import math
import random

from world.market import catalog as C
from world.market import goods as G
from world.market import meme_mail

PLAYER = "__player__"

# ------------------------------------------------------------------ the clock (design, section 2)
SECONDS_PER_HOUR = 150.0
EVENT_HOURS = {"quest": 1.0, "dungeon": 6.0, "hearth": 8.0}
#: worked an hour at a time up to this many hours, then in COARSE-hour steps
FINE_HOURS = 72
COARSE = 6.0

# ------------------------------------------------------------------ the two books (design, section 1)
#: "target" is how many NPC listings a book holds. Kyle, 16 Nov 2026: "Lets populate the AH by around 300% more items
#: across the board!" (2,600 and 1,700 before, so four times as many). Measured that day: opening the book takes
#: about two seconds, a day of play works out in about three, and the market adds about four megabytes to a save.
MARKETS = {
    "horde": {"name": "Horde Auction House", "cut": 0.05, "deposit": 0.15, "gear_traffic": 1.0, "odd": 1.0,
              "target": 13000},
    "goblin": {"name": "Steamwheedle Auction House", "cut": 0.15, "deposit": 0.25, "gear_traffic": 1.2,
               "odd": 1.5, "target": 8500},
}
#: which book an auctioneer opens
AUCTIONEER_MARKET = {
    "org_auctioneer": "horde", "uc_auctioneer": "horde", "fw_auctioneer": "horde",
    "bb_auctioneer": "goblin", "ratchet_auctioneer": "goblin", "stw_auctioneer": "goblin",
}
DURATIONS = (12, 24, 48)

# ------------------------------------------------------------------ the price index (design, section 4)
THETA = 0.035
NOISE = {"stack": 0.025, "gear": 0.035}
LOG_LO, LOG_HI = math.log(0.35), math.log(3.0)
LIST_SHOCK = 0.22
BUY_SHOCK = 0.12
NEWS_RATE = 1 / 40.0

# ------------------------------------------------------------------ buyers and bids (design, sections 6 and 7)
SIGMA = {"stack": 0.22, "gear": 0.35, "epic": 0.45}
R_CAP = 2.5
BID_STEP = 0.05
BIDDER_SHARE = 0.5
#: Rival bidders on an auction you're winning (design, section 7). Measured with tools/sim_auction_market.py so a
#: green you bid on gets taken off you about half the time at 60% of its going price, a third at 80%, one time in
#: seven at the going price and almost never above it: "SOMETIMES - NOT ALWAYS".
BID_RIVALS = 0.032
BID_RIVAL_MEAN = 0.92
BID_RIVAL_SIGMA = 0.15

# ------------------------------------------------------------------ undercuts, snipes, fat fingers (sections 8, 9)
UNDERCUT_U = 0.05
UNDERCUT_FLOOR = 0.85
SNIPE_BELOW = 0.65
SNIPE_RATE = 0.25
SNIPE_FAT = 0.5
FAT_RATE = 1 / 1500.0
RECRUIT_LIST_CHANCE = 0.15
#: how briskly NPC listings sell to NPC buyers (the part of the market you're not in). Half the full rate keeps a
#: listing around long enough to be browsed (about half the book turns over in a market day).
NPC_TURNOVER = 0.5

# ------------------------------------------------------------------ the Collection (docs/collection_design.md)
#: Kyle, 18 Nov 2026: collectables are "randomly sold in the AH" by whoever has one, at whatever they ask, and the
#: Collection section should hold "dozens to ~100" at a time across both books, each listed for about a market day
#: and picked by rarity (world/collection.py's weights), so the rare ones stay rare.
COLLECTION_TARGET = {"horde": 55, "goblin": 35}
#: new listings an hour, per missing listing, so a book fills back up through the day, not all at once
COLLECTION_ARRIVAL = 0.12
COLLECTION_HOURS = (18.0, 30.0)
#: demand per hour: the odd collector buys one, so something you're watching can vanish
COLLECTION_DEMAND = 0.01
#: cash on delivery (Kyle's): buy at least 5 (consumables, gems) or 10 (common materials) of one thing inside
#: COD_WINDOW market hours and a seller may offer more, at most once a market day per thing
COD_WINDOW = 12.0
#: Kyle, 16 Nov 2026: "we should tone down HOW often these are sent. i want it to kind of feel special. Maybe like...
#: people send letters from the AH a max of around 5% of the time". So no stranger writes more than one time in twenty
#: (COD offers were 0.7, a fat finger 0.85). The mail that pays you or hands you what you bought always comes.
LETTER_MAX = 0.05
COD_CHANCE = LETTER_MAX

# ------------------------------------------------------------------ the letters (meme_mail.py)
#: How often each moment gets a letter. Kyle, 15 Nov 2026: "cod more often. Fat fingers often. Rest infrequently".
MEME_CHANCE = {"fat_finger": LETTER_MAX, "sniped_you": LETTER_MAX, "undercut_smug": 0.03, "undercut_salt": LETTER_MAX,
               "outbid_them": LETTER_MAX, "outbid_you": 0.04, "recruit_sold": 0.5, "won_thanks": 0.03}
#: recruit_sold isn't a stranger: it's one of your own recruits telling you their listing sold

#: listing mix for a fresh NPC listing: (share, what)
MIX = [(0.44, "material"), (0.12, "consumable"), (0.08, "crafted"), (0.20, "proc"), (0.06, "dungeon"),
       (0.035, "recipe"), (0.01, "bag"), (0.004, "epic"), (0.031, "meme")]
PROC_RARITY = [("uncommon", 0.66), ("rare", 0.22), ("common", 0.08), ("poor", 0.02), ("epic", 0.02)]

HABITS = [("farmer", 0.30), ("crafter", 0.20), ("undercutter", 0.12), ("flipper", 0.08), ("casual", 0.18),
          ("collector", 0.06), ("bargain", 0.06)]
HABIT_TEXT = {
    "farmer": "Sells what they gather, by the stack.",
    "crafter": "Sells what they make.",
    "undercutter": "Keeps an eye on everybody else's prices.",
    "flipper": "Buys low and sells high, and never misses a bargain.",
    "casual": "Sells whatever turned up in their bags.",
    "collector": "Buys the good stuff and doesn't like losing.",
    "bargain": "Bids low on everything and waits.",
    "recruit": "In your party.",
}


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def poisson(rng, lam):
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def min_next_bid(a):
    """The least the next bid can be: the starting bid, or the current bid plus 5% (at least 1 copper)."""
    if not a.bid:
        return a.min_bid
    return a.bid + max(1, int(math.ceil(a.bid * BID_STEP)))


def time_left_band(hours):
    if hours < 2:
        return "Short"
    if hours < 8:
        return "Medium"
    if hours <= 24:
        return "Long"
    return "Very Long"


TIME_ICON = {"Short": "hourglass_empty", "Medium": "hourglass_low", "Long": "hourglass_half",
             "Very Long": "hourglass_full"}


def nice(c, rng):
    """Round a price the way a person would type it, half the time."""
    c = max(1, int(c))
    if rng.random() < 0.5:
        return c
    for step in (10000, 1000, 100, 10, 5):
        if c >= step * 20:
            return max(step, int(round(c / step)) * step)
    return c


# ================================================================== auctions
class Auction:
    """One listing. Prices are totals for the whole auction (as WoW stores them); per-unit is worked out."""
    __slots__ = ("id", "market", "seller", "seller_id", "src", "qty", "min_bid", "buyout", "bid", "bidder",
                 "bidders", "posted_at", "ends_at", "deposit", "name", "level", "rarity", "cat", "sub", "mkey",
                 "ikey", "kind", "icon", "fat", "meant", "undercuts", "meme", "val", "dem", "sig")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))
        self.bid = int(self.bid or 0)
        self.buyout = int(self.buyout or 0)
        self.min_bid = max(1, int(self.min_bid or 1))
        self.qty = int(self.qty or 1)
        self.bidders = list(self.bidders or [])
        self.deposit = int(self.deposit or 0)
        self.undercuts = int(self.undercuts or 0)

    @property
    def mine(self):
        return self.seller_id == PLAYER

    def unit(self, price):
        return price / max(1, self.qty)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def to_row(self):
        """A compact row for the save: values in __slots__ order, floats rounded. A full book is a few thousand of
        these, and the keys alone were half the save."""
        out = []
        for k in self.__slots__:
            v = getattr(self, k)
            if isinstance(v, float):
                v = round(v, 4)
            out.append(v)
        return out

    @classmethod
    def from_row(cls, row):
        return cls(**dict(zip(cls.__slots__, row)))

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: d.get(k) for k in cls.__slots__})


# ================================================================== traders
class Trader:
    __slots__ = ("name", "habit", "home", "personality")

    def __init__(self, name, habit, home, personality="bro"):
        self.name, self.habit, self.home, self.personality = name, habit, home, personality


_ROSTER = {}
_TITLE_WORDS = ("guard", "grunt", "peon", "citizen", "deathguard", "brave", "watcher", "sentry", "patrol",
                "worker", "refugee", "villager", "townsfolk", "orphan", "laborer", "labourer", "dockhand",
                "sailor", "bruiser", "thug", "trainer", "master", "keeper", "innkeep", "auctioneer", "banker",
                "flight", "wind rider", "bat handler", "vendor", "merchant", "quartermaster", "spirit healer",
                "scout", "lookout", "acolyte", "apprentice", "initiate", "recruit", "dummy", "test")


def _zone_title(slug):
    return " ".join(w.capitalize() for w in str(slug).replace("_", " ").split())


def roster(market):
    """The traders of one book: the world's own NPCs who aren't in a hidden place, plus the recruits nobody has
    recruited. Built once per run, the same every run (habits come from the name)."""
    if market in _ROSTER:
        return _ROSTER[market]
    import json
    import zlib
    hidden = C._hidden_zone_slugs()
    names = {}
    races = {}

    def ok_name(n):
        low = str(n).lower()
        return (" " in str(n) and len(str(n)) <= 26 and not any(w in low for w in _TITLE_WORDS)
                and not low.startswith("the ") and "'s " not in low)

    goblin_zones = {"booty_bay", "ratchet", "steamwheedle_port", "fourth_peg", "gadgetzan", "the_shimmering_flats",
                    "stranglethorn_vale", "tanaris", "the_cape_of_stranglethorn", "azshara"}
    try:
        doc = json.loads((C.ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))
        for n in doc.get("npcs", []):
            z = _slug_zone(n.get("zone", ""))
            if z in hidden or str(n.get("npc_id", "")).startswith("hz_") or not ok_name(n.get("name", "")):
                continue
            names.setdefault(n["name"], z)
            races.setdefault(n["name"], n.get("race"))
    except Exception:
        pass
    try:
        doc = json.loads((C.ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))
        for v in doc.get("vendors", []):
            z = _slug_zone(v.get("zone", ""))
            if v.get("hidden") or z in hidden or not ok_name(v.get("name", "")):
                continue
            names.setdefault(v["name"], z)
            races.setdefault(v["name"], v.get("race"))
    except Exception:
        pass
    recruits = {}
    try:
        doc = json.loads((C.ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))
        for r in doc.get("recruits", []):
            if r.get("name"):
                recruits[r["name"]] = _slug_zone(r.get("zone", ""))
    except Exception:
        pass
    pool = []
    for n, z in sorted(names.items()):
        h = zlib.crc32(n.encode("utf-8"))
        goblin = z in goblin_zones
        # Steamwheedle is mostly goblin-town folk with some everybody else; the Horde book is everybody else
        if market == "goblin" and not goblin and h % 3:
            continue
        if market == "horde" and goblin and h % 4:
            continue
        pool.append((n, z, h))
    for n, z in sorted(recruits.items()):
        pool.append((n, z, zlib.crc32(n.encode("utf-8"))))
    out = []
    for n, z, h in pool:
        x = (h % 10000) / 10000.0
        acc = 0.0
        habit = HABITS[-1][0]
        for hb, share in HABITS:
            acc += share
            if x < acc:
                habit = hb
                break
        from world.market.personalities import personality_for
        race = races.get(n) or ("goblin" if z in goblin_zones else None)
        out.append(Trader(n, habit, _zone_title(z) if z else "", personality_for(n, race)))
    _ROSTER[market] = out
    _ROSTER[market + ":by_habit"] = {}
    for t in out:
        _ROSTER[market + ":by_habit"].setdefault(t.habit, []).append(t)
    _ROSTER[market + ":by_name"] = {t.name: t for t in out}
    _ROSTER[market + ":recruits"] = set(recruits)
    return out


def _slug_zone(z):
    return str(z or "").lower().replace("'", "").replace(" ", "_")


def trader_named(market, name):
    roster(market)
    return _ROSTER[market + ":by_name"].get(name)


#: names of the people in the player's party and on the bench: they don't trade as strangers (they list their own
#: loot under "recruit:" instead). Kept up to date by market_of.
_IN_PARTY = set()


def pick_trader(market, habit, rng, exclude=()):
    roster(market)
    skip = set(exclude) | _IN_PARTY
    pool = [t for t in _ROSTER[market + ":by_habit"].get(habit, []) if t.name not in skip]
    if not pool:
        pool = [t for t in roster(market) if t.name not in skip]
    return rng.choice(pool)


# ================================================================== the market
class Market:
    def __init__(self, seed=None):
        self.clock = 0.0
        self.play_seconds = 0.0
        self.next_id = 1
        self.books = {m: {} for m in MARKETS}
        self.idx = {}                  # ikey -> [ln I, t]
        self.news = []                 # [{"market", "text", "at"}]
        self.favourites = set()        # item names
        self.my_bids = set()           # auction ids the player has bid on and not yet settled
        self.recruit_seen = set()      # recruits who've already written about you buying their stuff
        self.undercut_by = {}          # trader name -> times the player undercut them
        self.bulk = {}                 # mkey -> [[clock, qty, total paid, seller]] recent buyouts of stackables
        self.cod_sent = {}             # mkey -> clock of the last cash-on-delivery offer
        self.mail = None               # set by the party
        self.party = None              # set by the party (for recruits' names)
        self.rng = random.Random(seed)
        self._vcache = {}
        self._dcache = {}
        self._goods = {}               # auction id -> materialised good (not saved)
        self._by_key = {m: {} for m in MARKETS}
        self.stats = {"sold_to_npc": 0, "sniped": 0, "undercut": 0, "fat": 0, "news": 0, "outbid": 0}
        self.started = False

    # ------------------------------------------------------------ keys and values
    def good_of(self, a):
        """The good an auction holds, built on demand and cached."""
        g = self._goods.get(a.id)
        if g is None:
            g = self._materialise(a.src, a.qty)
            self._goods[a.id] = g
        return g

    def _materialise(self, src, qty):
        if "good" in src:
            return src["good"]
        if "entry" in src:
            e = C.entries().get(src["entry"])
            if e is None:
                return None
            return e.make(qty)
        if "proc" in src:
            return self._regen_proc(src["proc"])
        return None

    def ikey_of(self, good, mkey=None):
        mkey = mkey or G.market_key(good)
        if good["data"].get("collection_id"):
            return "col:" + good["data"]["collection_id"]
        if good["kind"] == G.GEAR and mkey not in C.entries():
            cat, sub = C.category_of(good)
            return f"gc:{cat}/{sub}:{G.rarity(good)}:{C.level_of(good) // 10}"
        return mkey

    def value(self, good):
        """Fair copper per unit (design, section 3)."""
        mkey = G.market_key(good)
        e = C.entries().get(mkey)
        if e is not None:
            return e.value
        if good["data"].get("collection_id"):
            from world.collection import get_entry
            return int((get_entry(good["data"]["collection_id"]) or {}).get("price", 1000000))
        if mkey in self._vcache:
            return self._vcache[mkey]
        k = good["kind"]
        d = good["data"]
        if k == G.MATERIAL:
            v = C.value(d.get("material_id"), "material")
        elif k == G.CONSUMABLE:
            v = C.value(d.get("consumable_id"), "consumable")
        elif k == G.LOOT:
            v = max(1, int(d.get("sell_price", 0) or 0))
        else:
            item = G.unpack(good)
            v = C.gear_value(item)
            if getattr(item, "enchant_id", None):
                from world.market.catalog import value as mv
                v += int(mv(item.enchant_id, "material") * 0.6)   # an enchant on it is worth something, not all
        self._vcache[mkey] = max(1, int(v))
        return self._vcache[mkey]

    def demand(self, good, market):
        mkey = G.market_key(good)
        hit = self._dcache.get((mkey, market))
        if hit is not None:
            return hit
        d = self._demand(good, market, mkey)
        self._dcache[(mkey, market)] = d
        return d

    def _demand(self, good, market, mkey):
        e = C.entries().get(mkey)
        k = good["kind"]
        if good["data"].get("collection_id"):
            return COLLECTION_DEMAND
        if e is not None:
            d = e.demand
        elif k == G.GEAR:
            item = G.unpack(good)
            base = 0.02 if getattr(item, "rarity", "") == "epic" else 0.025
            if getattr(item, "rarity", "") in ("poor", "common"):
                base = 0.006
            d = base * (0.55 + 0.9 * C.want(item))
        elif k == G.LOOT:
            d = 0.01
        elif k == G.MATERIAL:
            m = C.materials().get(good["data"].get("material_id")) or {}
            d = C._material_demand(good["data"].get("material_id"), m) if m else 0.1
            if good["data"].get("material_id") in C._vendor_stock():
                d *= 0.15            # the vendor sells it; only the lazy buy it here
        else:
            d = 0.25
        if k == G.GEAR:
            d *= MARKETS[market]["gear_traffic"]
        return d

    def sigma(self, good):
        if good["data"].get("collection_id"):
            return SIGMA["epic"]
        if good["kind"] == G.GEAR:
            return SIGMA["epic"] if G.rarity(good) == "epic" else SIGMA["gear"]
        return SIGMA["stack"]

    # ------------------------------------------------------------ the index (design, section 4)
    def log_index(self, ikey):
        """ln I for a key, brought up to the clock. Lazy and exact: an Ornstein-Uhlenbeck step over however
        many hours passed since it was last looked at, so a key nobody touches costs nothing."""
        rec = self.idx.get(ikey)
        if rec is None:
            return 0.0
        x, t = rec
        dt = self.clock - t
        if dt > 1e-9:
            a = (1.0 - THETA) ** dt
            s = NOISE["gear"] if ikey.startswith("g") else NOISE["stack"]
            var = s * s * (1 - a * a) / (1 - (1 - THETA) ** 2)
            x = x * a + math.sqrt(var) * self.rng.gauss(0, 1)
            x = min(LOG_HI, max(LOG_LO, x))
            rec[0], rec[1] = x, self.clock
        return rec[0]

    def shock(self, ikey, amount):
        """Move ln I by amount, then clamp. Every shock in the game goes through here."""
        x = self.log_index(ikey)
        rec = self.idx.setdefault(ikey, [0.0, self.clock])
        rec[0] = min(LOG_HI, max(LOG_LO, x + amount))
        rec[1] = self.clock

    def index(self, ikey):
        return math.exp(self.log_index(ikey))

    def going(self, good, ikey=None):
        """Going price per unit right now: fair value x I."""
        return self.value(good) * self.index(ikey or self.ikey_of(good))

    def going_a(self, a):
        """Going price per unit for an auction, from what it remembered when it was listed."""
        if a.val is None:
            good = self.good_of(a)
            if good is None:
                return 0.0
            a.val, a.dem, a.sig = self.value(good), self.demand(good, "horde"), self.sigma(good)
        return a.val * self.index(a.ikey)

    def _dem(self, a, market):
        if a.dem is None:
            self.going_a(a)
        d = a.dem or 0.0
        if a.kind == G.GEAR:
            d *= MARKETS[market]["gear_traffic"]
        return d

    def depth(self, good, market):
        avg = 1 if good["kind"] == G.GEAR else (8 if good["kind"] == G.MATERIAL else 6)
        return max(1.0, self.demand(good, market) * 24 * avg)

    # ------------------------------------------------------------ book keeping
    def _add(self, a, good=None):
        self.books[a.market][a.id] = a
        self._by_key[a.market].setdefault(a.mkey, set()).add(a.id)
        if good is not None:
            self._goods[a.id] = good

    def _remove(self, a):
        self.books[a.market].pop(a.id, None)
        s = self._by_key[a.market].get(a.mkey)
        if s:
            s.discard(a.id)
            if not s:
                self._by_key[a.market].pop(a.mkey, None)
        self._goods.pop(a.id, None)

    def same_key(self, market, mkey):
        return [self.books[market][i] for i in self._by_key[market].get(mkey, ()) if i in self.books[market]]

    def _new_auction(self, market, good, src, seller, seller_id, unit_buyout, duration, bid_only=False,
                     posted_at=None, fat=False, meant=0, deposit=0, min_bid_total=None):
        qty = G.quantity(good)
        buyout = 0 if bid_only else max(1, int(round(unit_buyout * qty)))
        if min_bid_total is None:
            min_bid_total = max(1, int((buyout or unit_buyout * qty) * self.rng.uniform(0.7, 0.9)))
        mkey = G.market_key(good)
        cat, sub = C.category_of(good)
        posted = self.clock if posted_at is None else posted_at
        d = good["data"]
        icon = (good["kind"], d.get("icon_id") or "", d.get("material_type") or "",
                d.get("consumable_id") or "")
        a = Auction(id=self.next_id, market=market, seller=seller, seller_id=seller_id, src=src, qty=qty,
                    min_bid=min(min_bid_total, buyout) if buyout else min_bid_total, buyout=buyout, bid=0,
                    bidder=None, bidders=[], posted_at=posted, ends_at=posted + duration, deposit=deposit,
                    name=G.name(good), level=C.level_of(good), rarity=C.rarity_of(good), cat=cat, sub=sub,
                    mkey=mkey, ikey=self.ikey_of(good, mkey), kind=good["kind"], icon=list(icon), fat=fat,
                    meant=meant)
        # what the hourly sums need, worked out once (so a loaded game never re-rolls a thousand pieces of gear just
        # to price them): fair value per unit, demand per hour (Horde traffic), price spread
        a.val = self.value(good)
        a.dem = self.demand(good, "horde")
        a.sig = self.sigma(good)
        if good["kind"] == G.LOOT:
            a.val = max(a.val, G.sell_price(good))     # trash is only ever worth the vendor
        self.next_id += 1
        self._add(a, good)
        return a

    # ------------------------------------------------------------ NPC listings
    def _pick_mix(self):
        x = self.rng.random()
        acc = 0.0
        for share, what in MIX:
            acc += share
            if x < acc:
                return what
        return "material"

    _POOLS = None

    def _pools(self):
        if Market._POOLS is None:
            pools = {}
            for k, e in C.entries().items():
                src = e.source
                what = {"material": "material", "consumable": "consumable", "crafted": "crafted",
                        "dungeon": "dungeon", "recipe": "recipe", "bag": "bag", "epic_world": "epic",
                        "epic_dungeon": "epic"}.get(src, "material")
                if what == "dungeon" and e.rarity == "epic":
                    what = "epic"
                band = min(11, max(0, (int(e.level or 1) - 1) // 5))
                pools.setdefault(what, {}).setdefault(band, []).append(e)
            Market._POOLS = pools
        return Market._POOLS

    def _pick_entry(self, what):
        bands = self._pools().get(what) or {}
        if not bands:
            return None
        if what in ("bag", "recipe"):
            # a small pool: by weight across all of it (a band with one bag in it shouldn't flood the book with
            # that bag), and the rarer the bag the rarer the listing
            es = [e for b in bands.values() for e in b]
            w = [max(0.01, e.weight) * {"epic": 0.08, "rare": 0.4}.get(e.rarity, 1.0) for e in es]
            return self.rng.choices(es, weights=w, k=1)[0]
        band = self.rng.choice(list(bands))           # a wide spread of levels, every band as likely
        es = bands[band]
        return self.rng.choices(es, weights=[max(0.01, e.weight or 0.1) for e in es], k=1)[0]

    def spawn_npc_listing(self, market, posted_at=None, duration=None):
        rng = self.rng
        what = self._pick_mix()
        if what == "proc":
            made = self._make_proc()
            if made is None:
                return None
            good, src = made
            habit = "casual"
        elif what == "meme":
            made = self._make_meme(market)
            if made is None:
                return None
            good, src, unit, bid_only, start = made
            if good is None:
                return None
            t = pick_trader(market, "casual", rng)
            dur = duration or rng.choice(DURATIONS)
            a = self._new_auction(market, good, src, t.name, "n:" + t.name, unit, dur, bid_only=bid_only,
                                  posted_at=posted_at, min_bid_total=start)
            a.meme = True
            return a
        else:
            e = self._pick_entry(what)
            if e is None:
                return None
            qty = rng.choice(e.stacks or [1])
            good = e.make(qty)
            if good is None:
                return None
            src = {"entry": e.key}
            habit = {"material": "farmer", "consumable": "crafter", "crafted": "crafter"}.get(what, "casual")
            if what == "material" and (C.materials().get(e.id) or {}).get("material_type") in (
                    "bar", "bolt", "plank", "cut_gem", "enchant_scroll", "rune", "upgrade_kit", "rune_ink"):
                habit = "crafter"
        t = pick_trader(market, habit if rng.random() < 0.85 else "casual", rng)
        g = self.going(good)
        factor = {"farmer": rng.uniform(0.9, 1.15), "crafter": rng.uniform(0.9, 1.2)}.get(t.habit)
        if factor is None:                            # casuals, and anybody else listing a drop
            x = rng.random()
            factor = (rng.uniform(0.8, 1.4) if x < 0.7 else rng.uniform(1.4, 3.0) if x < 0.9
                      else rng.uniform(0.55, 0.8))
        unit = g * factor * math.exp(0.12 * rng.gauss(0, 1))
        if good["kind"] == G.GEAR:                    # nobody lists gear for less than three quarters of the vendor
            unit = max(unit, G.sell_price(good) * 0.75)
        unit = nice(unit * G.quantity(good), rng) / G.quantity(good)
        fat, meant = False, 0
        total = unit * G.quantity(good)
        if total >= 5000 and rng.random() < FAT_RATE * MARKETS[market]["odd"]:
            # only the listings with enough digits to fumble (design, section 9). Measured with
            # tools/sim_auction_market.py: about two a market day across both books, each living a couple of hours,
            # so you catch one on maybe one visit in eight. Lucky, not routine.
            meant = int(total)
            div = rng.choices([10, 100, 1000], weights=[60, 35, 5])[0]
            unit = max(1, int(total / div)) / G.quantity(good)
            fat = True
            self.stats["fat"] += 1
        bid_only = good["kind"] == G.GEAR and t.habit == "casual" and rng.random() < 0.12 and not fat
        dur = duration or rng.choice(DURATIONS)
        a = self._new_auction(market, good, src, t.name, "n:" + t.name, unit, dur, bid_only=bid_only,
                              posted_at=posted_at, fat=fat, meant=meant)
        if bid_only:
            a.min_bid = max(1, int(g * rng.uniform(0.5, 0.9)))
        # some gear already has a bid on it when you find it
        if good["kind"] == G.GEAR and not fat and rng.random() < 0.25:
            b = pick_trader(market, rng.choice(["collector", "bargain"]), rng, exclude=(t.name,))
            a.bid = min(a.buyout - 1 if a.buyout else 10 ** 9, int(a.min_bid * rng.uniform(1.0, 1.2)))
            a.bid = max(a.min_bid, a.bid)
            a.bidder = b.name
            a.bidders.append(b.name)
        return a

    def _make_proc(self):
        """A procedurally rolled piece of gear for a random spec at a random level: the world drops people list."""
        rng = self.rng
        level = rng.randint(3, 60)
        rarity = rng.choices([r for r, _ in PROC_RARITY], weights=[w for _, w in PROC_RARITY])[0]
        if rarity == "epic" and level < 30:
            rarity = "rare"
        specs = list(C.specs().values())
        sp = rng.choice(specs)
        seed = rng.randrange(1 << 30)
        spec = [sp.get("class"), level, rarity, seed, sp.get("stat_template") if rng.random() < 0.75 else None]
        good = self._regen_proc(spec)
        if good is None:
            return None
        return good, {"proc": spec}

    def _regen_proc(self, spec):
        cls, level, rarity, seed, template = spec[:5]
        state = random.getstate()
        try:
            random.seed(seed)
            from entities.loot_generator import LootGenerator
            item = _gen().generate_item_for_class(cls, level, rarity=rarity, player_level=60,
                                                   stat_template=template)
        except Exception:
            item = None
        finally:
            random.setstate(state)
        if item is None:
            return None
        if len(spec) > 5 and spec[5]:
            item.enchant_id = spec[5]
        return G.pack(item)

    def _make_meme(self, market):
        """Kyle: "absolute trash for fuck all....even vendor trash or whites....Or you'll see something absolutely
        fucking unhinged like a lvl 5 grey 2H shovel with crusader for 10g", and "these are examples....go wild".

        -> (good, src, unit price, bid only, starting bid or None), or None.
        """
        rng = self.rng
        x = rng.random()
        if x < 0.32:                                  # a stack of vendor trash, for nothing or for a fortune
            from entities import vendor_trash as VT
            cfg = VT._config()
            fam = rng.choice(list(cfg["families"]))
            entry = rng.choice(cfg["families"][fam])
            info = VT.make_item(fam, entry, rng.randint(1, 60))
            from entities.loot_item import LootItem
            li = LootItem(info["item_id"], info["name"], category="trash", description=info["description"],
                          icon_id=info["icon_id"], sell_price=info["price"], rarity="poor")
            li.quantity = rng.choice([1, 1, 2, 3, 5, 12])
            good = G.pack(li)
            unit = info["price"] * rng.choice([rng.uniform(0.3, 0.9), rng.uniform(1.0, 3.0), rng.uniform(5, 40)])
            return good, {"good": good}, unit, False, None
        if x < 0.52:                                  # a white or grey, for nothing or for far too much
            sp = rng.choice(list(C.specs().values()))
            spec = [sp.get("class"), rng.randint(1, 45), rng.choice(["poor", "common"]), rng.randrange(1 << 30), None]
            good = self._regen_proc(spec)
            if good is None:
                return None
            sell = max(1, G.sell_price(good))
            unit = sell * (rng.uniform(0.2, 0.9) if rng.random() < 0.6 else rng.uniform(20, 300))
            return good, {"proc": spec}, unit, False, None
        if x < 0.64:                                  # ONE of the most common thing in the game, priced like an epic
            pool = [e for e in C.entries().values() if e.kind == G.MATERIAL and e.level <= 15 and e.value < 100]
            if not pool:
                return None
            e = rng.choice(pool)
            good = e.make(1)
            unit = rng.choice([999999, 123456, 696969, 500000, 99999, 424242, 777777])
            return good, {"entry": e.key}, unit, False, None
        if x < 0.80:                                  # a penny auction: a decent piece, bid only, from one copper
            sp = rng.choice(list(C.specs().values()))
            spec = [sp.get("class"), rng.randint(8, 58), rng.choice(["uncommon", "uncommon", "rare"]),
                    rng.randrange(1 << 30), sp.get("stat_template")]
            good = self._regen_proc(spec)
            if good is None:
                return None
            return good, {"proc": spec}, 1, True, 1
        # the unhinged one: a grey or white weapon from the bottom of the game wearing a top-end enchant
        from world import enchanting as EN
        ench = [k for k, v in EN.data()["enchants"].items()
                if v.get("group") in ("weapon", "2h") and int(v.get("skill", 0) or 0) >= 190 and not v.get("secret")]
        level = rng.randint(2, 12)
        for _ in range(8):
            sp = rng.choice(list(C.specs().values()))
            spec = [sp.get("class"), level, rng.choice(["poor", "common"]), rng.randrange(1 << 30), None]
            good = self._regen_proc(spec)
            if good is None:
                return None
            item = G.unpack(good)
            fits = [e for e in ench if EN.fits(item, e)]
            if fits:
                spec.append(rng.choice(fits))
                good = self._regen_proc(spec)
                unit = rng.choice([50000, 77700, 100000, 150000, 250000, 420000, 999999]) * rng.uniform(0.9, 1.1)
                return good, {"proc": spec}, unit, rng.random() < 0.2, None
        return None

    def ensure_started(self):
        if self.started:
            return
        self.started = True
        for market, conf in MARKETS.items():
            for _ in range(conf["target"]):
                dur = self.rng.choice(DURATIONS)
                self.spawn_npc_listing(market, posted_at=self.clock - self.rng.uniform(0, dur * 0.95),
                                       duration=dur)
            for _ in range(COLLECTION_TARGET[market]):
                self._list_collectable(market, force=True)

    # ------------------------------------------------------------ the clock
    def advance(self, hours):
        """Move the market forward and work out everything that happened. Returns the hours worked.

        Before anybody has opened an auction house there's nothing to work out: the clock just moves (the book is
        filled the first time an auctioneer or a mailbox is used, so starting a game costs nothing)."""
        hours = max(0.0, float(hours))
        if not self.started:
            self.clock += hours
            if self.mail is not None:
                self.mail.tidy(self.clock)
                if self.party is not None:
                    self.mail.deliver_due(self.clock, self.party, self.rng)
            return hours
        done = 0.0
        while hours - done > 1e-9:
            step = 1.0 if done < FINE_HOURS else COARSE
            step = min(step, hours - done)
            self._step(step)
            done += step
        if self.mail is not None:
            self.mail.tidy(self.clock)
            if self.party is not None:
                self.mail.deliver_due(self.clock, self.party, self.rng)
        return done

    def on_play_seconds(self, seconds):
        """Overworld time. Whole market hours are worked as they accrue."""
        self.play_seconds += max(0.0, seconds)
        if self.started:
            self._trickle()
        n = int(self.play_seconds // SECONDS_PER_HOUR)
        if n:
            self.play_seconds -= n * SECONDS_PER_HOUR
            self.advance(n)
        return n

    def on_event(self, kind):
        return self.advance(EVENT_HOURS.get(kind, 0.0))

    def _step(self, dt):
        self.clock += dt
        for market in MARKETS:
            self._settle_ended(market)
            self._npc_turnover(market, dt)
            self._player_keys(market, dt)
            self._snipes(market, dt)
            self._news(market, dt)
            self._collection_supply(market, dt)
            # the hour only tops the book up a little; the rest goes back a couple of listings a frame while you
            # play (_trickle), so working out an hour never stalls the game
            self._refill(market, cap=max(150, MARKETS[market]["target"] // 40))

    # ------------------------------------------------------------ hourly pieces
    def _settle_ended(self, market):
        for a in [a for a in self.books[market].values() if a.ends_at <= self.clock]:
            self._end(a)

    def _end(self, a):
        """An auction's time ran out: the high bidder wins it, or it goes back to its seller."""
        good = self.good_of(a)
        self._remove(a)
        name = a.name + (f" ({a.qty})" if a.qty > 1 else "")
        if a.bidder == PLAYER:
            self.my_bids.discard(a.id)
            self._letter(MARKETS[a.market]["name"], f"Auction won: {name}",
                         f"You won {name} for {_c(a.bid)}.", goods=[good], kind="auction_won")
            prev = [b for b in a.bidders if b != PLAYER]
            if prev and self.rng.random() < MEME_CHANCE["outbid_them"] and a.rarity in ("rare", "epic"):
                self._meme("outbid_them", prev[-1], a, paid=a.bid)
            elif self.rng.random() < MEME_CHANCE["won_thanks"] and not a.mine:
                self._meme("won_thanks", a.seller, a, paid=a.bid)
        if a.mine:
            if a.bid and a.bidder:
                self._pay_seller(a, a.bid, a.bidder)
            else:
                self._letter(MARKETS[a.market]["name"], f"Auction expired: {name}",
                             f"Your auction of {name} has expired and is returned to you.", goods=[good],
                             kind="auction_expired")

    def _pay_seller(self, a, price, buyer):
        cut = int(math.ceil(price * MARKETS[a.market]["cut"]))
        net = price - cut + a.deposit
        name = a.name + (f" ({a.qty})" if a.qty > 1 else "")
        self._letter(MARKETS[a.market]["name"], f"Auction successful: {name}",
                     f"Sold to {buyer}.\nSale price: {_c(price)}\nDeposit returned: {_c(a.deposit)}\n"
                     f"Auction house cut: {_c(cut)}\nYou receive: {_c(net)}", copper=net, kind="auction_sold")

    def _refund_player_bid(self, a, by, why="outbid"):
        if a.bidder != PLAYER or not a.bid:
            return
        self.stats["outbid"] += 1
        name = a.name + (f" ({a.qty})" if a.qty > 1 else "")
        if why == "outbid":
            self._letter(MARKETS[a.market]["name"], f"Outbid on {name}",
                         f"You have been outbid on {name}. Your bid of {_c(a.bid)} is returned.", copper=a.bid,
                         kind="outbid")
            if self.rng.random() < MEME_CHANCE["outbid_you"]:
                self._meme("outbid_you", by, a, paid=a.bid)
        else:
            self._letter(MARKETS[a.market]["name"], f"Auction ended: {name}",
                         f"{name} sold to someone who bought it outright. Your bid of {_c(a.bid)} is returned.",
                         copper=a.bid, kind="outbid")

    def _npc_turnover(self, market, dt):
        """NPC listings nobody you care about is in: buyers come at the key's rate and take the cheap ones."""
        book = self.books[market]
        busy = {a.mkey for a in book.values() if a.mine or a.bidder == PLAYER}
        counts = {}
        for a in book.values():
            counts[a.mkey] = counts.get(a.mkey, 0) + 1
        for a in list(book.values()):
            if a.mkey in busy or a.mine:
                continue
            g = self.going_a(a)
            if g <= 0:
                self._remove(a)
                continue
            if not a.buyout:
                # bid-only: bargain hunters and collectors nudge the bid up while it runs (penny auctions climb)
                lam = self._dem(a, market) * BIDDER_SHARE
                for _ in range(poisson(self.rng, lam * dt)):
                    r_total = min(R_CAP * g, g * math.exp(a.sig * self.rng.gauss(0, 1))) * a.qty
                    nxt = min_next_bid(a)
                    if r_total >= nxt:
                        who = pick_trader(market, self.rng.choice(["bargain", "collector"]), self.rng)
                        a.bid = nxt if self.rng.random() < 0.7 else max(nxt, int(0.6 * r_total))
                        a.bidder = who.name
                        a.bidders.append(who.name)
                continue
            r = a.unit(a.buyout) / max(1e-9, g)
            if r >= R_CAP:
                continue
            s = 1.0 - phi(math.log(max(1e-9, r)) / a.sig)
            lam = NPC_TURNOVER * self._dem(a, market) * s / max(1, counts.get(a.mkey, 1)) ** 0.5
            if self.rng.random() < 1.0 - math.exp(-lam * dt):
                self.stats["sold_to_npc"] += 1
                self._remove(a)

    def _player_keys(self, market, dt):
        """Keys you're in (as seller or bidder): the full model, buyer by buyer (design, sections 6 to 8)."""
        book = self.books[market]
        keys = {}
        for a in book.values():
            if a.mine or a.bidder == PLAYER:
                keys.setdefault(a.mkey, []).append(a)
        rng = self.rng
        for mkey, mine in keys.items():
            all_here = self.same_key(market, mkey)
            if not all_here:
                continue
            good = self.good_of(mine[0])
            if good is None:
                continue
            g = self.going(good, mine[0].ikey)
            lam = self.demand(good, market)
            sig = self.sigma(good)
            # buyers: each buys out the cheapest per-unit auction at or under their limit
            for _ in range(poisson(rng, lam * dt)):
                r_unit = min(R_CAP * g, g * math.exp(sig * rng.gauss(0, 1)))
                cands = sorted((a for a in self.same_key(market, mkey) if a.buyout),
                               key=lambda a: (a.unit(a.buyout), a.posted_at))
                for a in cands:
                    if a.unit(a.buyout) <= r_unit:
                        buyer = pick_trader(market, rng.choice(["casual", "crafter", "farmer", "collector"]), rng)
                        self._sold_to_npc(a, a.buyout, buyer.name)
                        break
                    break                               # buyers look at the cheapest; if that's too dear, they leave
            # bidders: on your listings, and against your bids
            for a in list(self.same_key(market, mkey)):
                if not (a.mine or a.bidder == PLAYER):
                    continue
                against_you = a.bidder == PLAYER
                rate = (BID_RIVALS * (0.6 + 0.8 * min(1.0, lam / 0.03)) if a.kind == G.GEAR else
                        lam * BIDDER_SHARE) if against_you else lam * BIDDER_SHARE
                for _ in range(poisson(rng, rate * dt)):
                    if a.id not in self.books[market]:
                        break
                    if against_you:
                        # a rival bidder: knows what it's worth, a little under it, and doesn't chase far
                        r_unit = g * BID_RIVAL_MEAN * math.exp(BID_RIVAL_SIGMA * rng.gauss(0, 1))
                    else:
                        r_unit = g * math.exp(sig * rng.gauss(0, 1))
                    r_total = min(R_CAP * g, r_unit) * a.qty
                    nxt = min_next_bid(a)
                    if r_total < nxt or (a.buyout and r_total >= a.buyout):
                        continue
                    who = pick_trader(market, rng.choice(["collector", "bargain", "casual"]), rng)
                    amount = nxt if rng.random() < 0.7 else max(nxt, int(0.85 * r_total))
                    if a.buyout:
                        amount = min(amount, a.buyout - 1)
                    if amount < nxt:
                        continue
                    if a.bidder == PLAYER:
                        self._refund_player_bid(a, who.name)      # stays in my_bids: the Bids tab shows it as Outbid
                        against_you = False
                    a.bid, a.bidder = amount, who.name
                    a.bidders.append(who.name)
            # undercutters: only on things that can be the same thing (stacks and named items)
            for a in list(mine):
                if not a.mine or a.id not in self.books[market] or not a.buyout:
                    continue
                if a.kind == G.GEAR and a.mkey not in C.entries():
                    continue
                age = self.clock - a.posted_at
                want = min(1.5, max(0.5, lam / 0.5))
                p = UNDERCUT_U * (1 + 2 * math.exp(-age / 3.0)) * want
                if rng.random() >= 1.0 - math.exp(-p * dt):
                    continue
                u = a.unit(a.buyout)
                lowest = min((x.unit(x.buyout) for x in self.same_key(market, mkey) if x.buyout), default=u)
                if u > lowest + 1e-9 or u < UNDERCUT_FLOOR * g:
                    continue                            # you're not the cheapest, or you're already under cost
                self._undercut(market, a, good, u, g)

    def _undercut(self, market, a, good, u, g):
        rng = self.rng
        x = rng.random()
        if x < 0.4:
            new = u - 1.0 / max(1, a.qty) * max(1, a.qty)    # one copper under per unit
            new = u - 1
        elif x < 0.7:
            step = 10000 if u > 50000 else 1000 if u > 5000 else 100 if u > 500 else 10 if u > 50 else 1
            new = (math.ceil(u / step) - 1) * step
            if new >= u:
                new = u - step
        else:
            new = u * (1 - rng.uniform(0.02, 0.08))
        new = max(1, int(new))
        if new < UNDERCUT_FLOOR * g * 0.95:
            return
        t = pick_trader(market, "undercutter", rng)
        qty = max(1, min(G.quantity(good), int(round(a.qty * rng.uniform(0.6, 1.4)))))
        g2 = G.with_quantity(good, qty) if good["kind"] != G.GEAR else good
        src = {"good": g2} if good["kind"] == G.GEAR or "entry" not in (a.src or {}) else {"entry": a.src["entry"]}
        if a.kind != G.GEAR and "entry" in (a.src or {}):
            src = {"entry": a.src["entry"]}
        self._new_auction(market, g2, src, t.name, "n:" + t.name, new, rng.choice(DURATIONS))
        a.undercuts += 1
        self.stats["undercut"] += 1
        if rng.random() < MEME_CHANCE["undercut_smug"]:
            self._meme("undercut_smug", t.name, a, paid=new)

    def _snipes(self, market, dt):
        """Flippers buy anything far under the going price, fat fingers fastest (design, section 9)."""
        rng = self.rng
        for a in list(self.books[market].values()):
            if not a.buyout or a.bidder == PLAYER and a.mine:
                continue
            g = self.going_a(a)
            if g <= 0 or a.unit(a.buyout) >= SNIPE_BELOW * g:
                continue
            good = self.good_of(a)
            if good is None:
                continue
            rate = SNIPE_FAT if a.fat else SNIPE_RATE
            if rng.random() >= 1.0 - math.exp(-rate * dt):
                continue
            t = pick_trader(market, "flipper", rng)
            self.stats["sniped"] += 1
            if a.mine:
                self._sold_to_npc(a, a.buyout, t.name)
                if rng.random() < MEME_CHANCE["sniped_you"]:
                    self._meme("sniped_you", t.name, a, paid=a.buyout, meant=int(g * a.qty))
            else:
                if a.bidder == PLAYER:
                    self._refund_player_bid(a, t.name, why="bought")
                    self.my_bids.discard(a.id)
                self._remove(a)
            if rng.random() < 0.6 and a.kind != G.LOOT:   # and it comes back at the going price
                self._new_auction(market, good, a.src if "entry" in (a.src or {}) else {"good": good}, t.name,
                                  "n:" + t.name, g * rng.uniform(0.95, 1.12), rng.choice(DURATIONS))

    def _sold_to_npc(self, a, price, buyer):
        if a.bidder == PLAYER:
            self._refund_player_bid(a, buyer, why="bought")
            self.my_bids.discard(a.id)
        self._remove(a)
        if a.mine:
            self._pay_seller(a, price, buyer)

    def _news(self, market, dt):
        rng = self.rng
        if rng.random() >= 1.0 - math.exp(-NEWS_RATE * dt):
            return
        from world.market.news import pick
        item = pick(rng)
        if not item:
            return
        text, keys, mult = item
        for k in keys:
            if k in C.entries():
                self.shock(k, math.log(mult))
        self.news.append({"market": market, "text": text, "at": self.clock})
        self.news = self.news[-12:]
        self.stats["news"] += 1

    def collection_listings(self, market):
        book = self.books[market]
        return [book[i] for k, ids in self._by_key[market].items() if k.startswith("g:collectable_")
                for i in ids if i in book]

    def _collection_supply(self, market, dt):
        """Keep the book's Collection section stocked (docs/collection_design.md): new listings arrive through the
        day while it's short of COLLECTION_TARGET."""
        short = COLLECTION_TARGET[market] - len(self.collection_listings(market))
        if short <= 0:
            return 0
        n = min(short, poisson(self.rng, short * COLLECTION_ARRIVAL * dt))
        for _ in range(n):
            self._list_collectable(market)
        return n

    def _list_collectable(self, market, force=False):
        """One collectable listed by a trader at their own price, picked by rarity from the ones not already listed
        in either house."""
        from world import collection as CL
        listed = {a.mkey for m in MARKETS for a in self.collection_listings(m)}
        # a found-only collectable (the fishing mounts and titles, world/harvest_finds.py) is caught or earned, never
        # put up by a trader; one a player caught and lists themselves is still theirs to sell
        pool = [e for e in CL.entries() if f"g:collectable_{e['id']}" not in listed and not e.get("found_only")]
        if not pool:
            return None
        weights = [CL.rarity_weight(e["rarity"]) for e in pool]
        e = self.rng.choices(pool, weights=weights)[0]
        item = CL.make_item(e["id"])
        good = G.pack(item)
        g = self.going(good)
        unit = nice(g * self.rng.uniform(0.9, 1.25), self.rng)
        seller = pick_trader(market, "collector", self.rng)
        dur = self.rng.uniform(*COLLECTION_HOURS)
        return self._new_auction(market, good, {"good": good}, seller.name, "n:" + seller.name, unit, dur,
                                 posted_at=self.clock - (0 if not force else self.rng.uniform(0, dur * 0.6)))

    def _refill(self, market, cap=400):
        npc = sum(1 for a in self.books[market].values() if not a.mine)
        need = MARKETS[market]["target"] - npc
        for _ in range(max(0, min(need, cap))):
            self.spawn_npc_listing(market, posted_at=self.clock - self.rng.uniform(0, 1))

    #: listings put back per frame of overworld play, per book, while it's under its target
    TRICKLE = 2

    def _trickle(self):
        """A few listings a frame. The book's size is len(book): the player's own handful of listings makes no
        difference to a book of thousands, and counting them every frame would."""
        for market, conf in MARKETS.items():
            short = conf["target"] - len(self.books[market])
            for _ in range(max(0, min(short, self.TRICKLE))):
                self.spawn_npc_listing(market, posted_at=self.clock - self.rng.uniform(0, 1))

    # ------------------------------------------------------------ letters
    def _letter(self, sender, subject, body, copper=0, goods=None, kind="letter", delay=0.0, sender_kind="auction"):
        if self.mail is None:
            return
        from world.mail import Letter
        self.mail.deliver(Letter(sender, subject, body=body, copper=copper, goods=[g for g in (goods or []) if g],
                                 kind=kind, sent_at=self.clock, arrives_at=self.clock + delay,
                                 sender_kind=sender_kind))

    def _meme(self, pool, sender, a, paid=0, meant=0):
        you = getattr(getattr(self.party, "player", None), "name", "friend") if self.party else "friend"
        fields = dict(item=a.name, paid=_c(paid), meant=_c(meant or a.meant or 0), you=you,
                      name=str(sender).split()[0])
        # in the sender's own voice when they have one (world/market/personalities.py); two times in three, so
        # the shared pool still turns up now and then
        t = trader_named(a.market, sender)
        made = None
        if t is not None and self.rng.random() < 0.67:
            from world.market.personalities import write as _pwrite
            made = _pwrite(pool, t.personality, self.rng, **fields)
        subj, body = made or meme_mail.write(pool, self.rng, **fields)
        self._letter(sender, subj, body, kind="meme", delay=self.rng.uniform(0.5, 5.0), sender_kind="npc")

    # ================================================================== the player's side
    def deposit_for(self, good, duration, market):
        """Copper held for listing this good (design, section 10)."""
        per = MARKETS[market]["deposit"] * (duration / 12.0)
        return max(1, int(math.ceil(G.sell_price(good) * G.quantity(good) * per)))

    def post(self, party, character, obj, qty, min_bid, buyout, duration, market):
        """List from your bags. (ok, message)."""
        self.ensure_started()
        ok, why = G.can_trade(obj)
        if not ok:
            return False, why
        if duration not in DURATIONS:
            return False, "Pick how long it runs."
        min_bid, buyout = int(min_bid or 0), int(buyout or 0)
        if min_bid < 1:
            return False, "Set a starting bid."
        if buyout and buyout < min_bid:
            return False, "The buyout can't be less than the starting bid."
        probe = G.pack(obj, qty)
        dep = self.deposit_for(probe, duration, market)
        if party.copper < dep:
            return False, f"You need {_c(dep)} for the deposit."
        good = G.take(character, obj, qty)
        if good is None:
            return False, "That can't be listed."
        party.remove_currency(dep)
        a = self._new_auction(market, good, {"good": good}, getattr(party.player, "name", "You"), PLAYER,
                              buyout / max(1, G.quantity(good)), duration, bid_only=not buyout, deposit=dep,
                              min_bid_total=min_bid)
        a.min_bid = min_bid
        # you undercut somebody? they notice, now and then (meme_mail.UNDERCUT_SALT)
        if buyout:
            u = a.unit(buyout)
            under = [x for x in self.same_key(market, a.mkey) if not x.mine and x.buyout and x.unit(x.buyout) > u]
            if under:
                victim = min(under, key=lambda x: x.unit(x.buyout))
                n = self.undercut_by.get(victim.seller, 0) + 1
                self.undercut_by[victim.seller] = n
                if n >= 2 and self.rng.random() < MEME_CHANCE["undercut_salt"] and victim.seller_id.startswith("n:"):
                    self._meme("undercut_salt", victim.seller, a, paid=buyout)
        self.shock(a.ikey, -LIST_SHOCK * G.quantity(good) / self.depth(good, market))
        return True, f"Listed {a.name}" + (f" ({a.qty})" if a.qty > 1 else "") + f". Deposit {_c(dep)}."

    def cancel(self, party, auction_id, market):
        a = self.books[market].get(auction_id)
        if a is None or not a.mine:
            return False, "That isn't one of yours."
        fee = int(math.ceil(a.bid * MARKETS[market]["cut"])) if a.bid else 0
        if fee and party.copper < fee:
            return False, f"Cancelling with a bid on it costs the cut, {_c(fee)}."
        if fee:
            party.remove_currency(fee)
        good = self.good_of(a)
        self._remove(a)
        name = a.name + (f" ({a.qty})" if a.qty > 1 else "")
        self._letter(MARKETS[market]["name"], f"Auction cancelled: {name}",
                     f"You cancelled your auction of {name}. The deposit is kept.", goods=[good],
                     kind="auction_cancelled")
        return True, "Cancelled. It's in your mail." + (f" The cut on the bid cost {_c(fee)}." if fee else "")

    def place_bid(self, party, auction_id, amount, market):
        a = self.books[market].get(auction_id)
        if a is None:
            return False, "That auction's gone."
        if a.mine:
            return False, "You can't bid on your own auction."
        amount = int(amount)
        if a.buyout and amount >= a.buyout:
            return self.buyout(party, auction_id, market)
        nxt = min_next_bid(a) if a.bidder != PLAYER else a.bid + max(1, int(math.ceil(a.bid * BID_STEP)))
        if amount < nxt:
            return False, f"The least you can bid is {_c(nxt)}."
        extra = amount - (a.bid if a.bidder == PLAYER else 0)
        if party.copper < extra:
            return False, "You don't have that much."
        party.remove_currency(extra)
        a.bid, a.bidder = amount, PLAYER
        a.bidders.append(PLAYER)
        self.my_bids.add(a.id)
        return True, f"Bid placed on {a.name}. You're the high bidder."

    def buyout(self, party, auction_id, market):
        a = self.books[market].get(auction_id)
        if a is None:
            return False, "That auction's gone."
        if a.mine:
            return False, "You can't buy your own auction."
        if not a.buyout:
            return False, "That one's bid only."
        refund = a.bid if a.bidder == PLAYER else 0
        if party.copper + refund < a.buyout:
            return False, "You don't have that much."
        party.remove_currency(a.buyout - refund)
        good = self.good_of(a)
        self._remove(a)
        self.my_bids.discard(a.id)
        name = a.name + (f" ({a.qty})" if a.qty > 1 else "")
        self._letter(MARKETS[market]["name"], f"Auction won: {name}", f"You bought {name} for {_c(a.buyout)}.",
                     goods=[good], kind="auction_won")
        self.shock(a.ikey, BUY_SHOCK * a.qty / self.depth(good, market))
        if a.seller_id and a.seller_id.startswith("recruit:"):
            if a.seller not in self.recruit_seen or self.rng.random() < 0.3:
                self.recruit_seen.add(a.seller)
                if self.rng.random() < MEME_CHANCE["recruit_sold"]:
                    self._meme("recruit_sold", a.seller, a, paid=a.buyout)
        elif a.fat and self.rng.random() < MEME_CHANCE["fat_finger"]:
            self._meme("fat_finger", a.seller, a, paid=a.buyout, meant=a.meant)
        if a.kind in (G.MATERIAL, G.CONSUMABLE) and not a.fat:
            self._maybe_cod(a, good)
        return True, f"Bought {name} for {_c(a.buyout)}. It's in your mail."

    def _maybe_cod(self, a, good):
        """Buying a lot of one stackable thing in a short stretch: sometimes a seller offers more, privately,
        cash on delivery, below what you've been paying (the auction house's cut stays in both your pockets)."""
        rng = self.rng
        rows = [r for r in self.bulk.get(a.mkey, []) if self.clock - r[0] <= COD_WINDOW]
        rows.append([self.clock, a.qty, a.buyout, a.seller])
        self.bulk[a.mkey] = rows
        bought = sum(r[1] for r in rows)
        need = 4 if a.kind == G.CONSUMABLE or a.rarity != "common" else 8
        if bought < need or self.clock - self.cod_sent.get(a.mkey, -1e9) < 24:
            return
        self.cod_sent[a.mkey] = self.clock          # one roll per thing per market day, offer or not
        if rng.random() >= COD_CHANCE:
            return
        paid = sum(r[2] for r in rows)
        avg = paid / max(1, bought)
        n = max(1, min(int(G.quantity(good) * 4) or 5, int(round(bought * rng.uniform(0.2, 0.6)))))
        if a.kind == G.MATERIAL:
            n = max(n, 3)
        each = max(1, int(nice(avg * rng.uniform(0.55, 0.85), rng)))
        sellers = [r[3] for r in rows if r[3] and not str(r[3]).startswith("recruit")]
        who = rng.choice(sellers) if sellers and rng.random() < 0.6 else pick_trader(
            a.market, "farmer" if a.kind == G.MATERIAL else "crafter", rng).name
        t = trader_named(a.market, who)
        made = None
        if t is not None:
            from world.market.personalities import write as _pwrite
            made = _pwrite("cod", t.personality, rng, item=a.name, n=n, each=_c(each))
        subj, body = made or meme_mail.write("cod", rng, item=a.name, n=n, each=_c(each))
        from world.mail import Letter
        extra = G.with_quantity(good, n)
        if self.mail is not None:
            self.mail.deliver(Letter(who, subj, body=body, goods=[extra], kind="cod", sent_at=self.clock,
                                     arrives_at=self.clock + rng.uniform(1.0, 4.0), can_return=True,
                                     sender_kind="npc", cod=each * n))
        self.cod_sent[a.mkey] = self.clock

    def toggle_favourite(self, name):
        if name in self.favourites:
            self.favourites.discard(name)
            return False
        self.favourites.add(name)
        return True

    # ------------------------------------------------------------ what the screen asks
    def search(self, market, text="", exact=False, lo=None, hi=None, rarity=None, usable_by=None, cat=None,
               sub=None, favourites=False):
        self.ensure_started()
        text = (text or "").strip().lower()
        r_min = C.RARITY_ORDER.index(rarity) if rarity in C.RARITY_ORDER else None
        out = []
        for a in self.books[market].values():
            if favourites and a.name not in self.favourites:
                continue
            if text:
                n = a.name.lower()
                if (exact and n != text) or (not exact and text not in n):
                    continue
            if lo is not None and (a.level or 0) < lo:
                continue
            if hi is not None and (a.level or 0) > hi:
                continue
            if r_min is not None and C.RARITY_ORDER.index(a.rarity if a.rarity in C.RARITY_ORDER else "common") < r_min:
                continue
            if cat and a.cat != cat:
                continue
            if sub and a.sub != sub:
                continue
            if usable_by is not None and not self.usable(a, usable_by):
                continue
            out.append(a)
        return out

    def usable(self, a, who):
        if a.kind == G.MATERIAL or a.kind == G.LOOT:
            return a.kind == G.MATERIAL
        if a.kind == G.CONSUMABLE:
            return (a.level or 0) <= who.level
        good = self.good_of(a)
        if good is None:
            return False
        item = G.unpack(good)
        if getattr(item, "recipe_id", None):
            prof = getattr(item, "recipe_profession", None)
            return bool(prof) and who.knows_profession(prof) if hasattr(who, "knows_profession") else False
        if int(getattr(item, "required_level", 1) or 1) > who.level:
            return False
        from entities.proficiency import can_equip
        try:
            return can_equip(who, item)[0]
        except Exception:
            return False

    def my_auctions(self, market):
        return sorted((a for a in self.books[market].values() if a.mine), key=lambda a: a.ends_at)

    def bids(self, market):
        """Auctions you've bid on that are still running, winning or outbid."""
        alive = set()
        for b in self.books.values():
            alive.update(i for i in self.my_bids if i in b)
        self.my_bids &= alive
        out = [self.books[market][i] for i in self.my_bids if i in self.books[market]]
        return sorted(out, key=lambda a: a.ends_at)

    def going_for(self, obj, market):
        """(going per unit, fair value per unit, index) for something in your bags."""
        good = G.pack(obj)
        ik = self.ikey_of(good)
        return self.going(good, ik), self.value(good), self.index(ik)

    def competition(self, market, obj):
        """The other listings of the same thing, cheapest per unit first."""
        mkey = G.market_key(G.pack(obj))
        return sorted((a for a in self.same_key(market, mkey) if a.buyout),
                      key=lambda a: a.unit(a.buyout))

    def suggest(self, market, obj, qty):
        """(starting bid, buyout) the WoW way: a copper under the cheapest per unit, or the going price."""
        g, _v, _i = self.going_for(obj, market)
        comp = [a for a in self.competition(market, obj) if not a.mine and not a.fat]
        unit = (comp[0].unit(comp[0].buyout) - 1) if comp else g
        unit = max(1, unit)
        buyout = max(1, int(unit * qty))
        return max(1, int(buyout * 0.85)), buyout

    def seller_info(self, a):
        """Who's selling: (title line, detail line)."""
        if a.mine:
            return "You", ""
        if a.seller_id and a.seller_id.startswith("recruit:"):
            return a.seller, "In your party."
        t = trader_named(a.market, a.seller)
        if t is None:
            return a.seller, ""
        where = f"From {t.home}. " if t.home else ""
        from world.market.personalities import BLURB
        return a.seller, where + HABIT_TEXT.get(t.habit, "") + " " + BLURB.get(t.personality, "")

    def time_left(self, a):
        return time_left_band(max(0.0, a.ends_at - self.clock))

    # ------------------------------------------------------------ your recruits sell their loot
    def recruits_list_loot(self, party, level):
        """After the last boss of a dungeon: each recruit in the party might put a few things up."""
        rng = self.rng
        self.ensure_started()
        for m in list(getattr(party, "members", []))[1:]:
            if rng.random() >= RECRUIT_LIST_CHANCE:
                continue
            for _ in range(rng.randint(1, 3)):
                if rng.random() < 0.7:
                    e = self._near_level("material", level)
                    if e is None:
                        continue
                    good = e.make(rng.choice(e.stacks or [1]))
                    src = {"entry": e.key}
                else:
                    sp = rng.choice(list(C.specs().values()))
                    spec = [sp.get("class"), max(1, level + rng.randint(-2, 1)),
                            rng.choice(["uncommon", "uncommon", "common", "rare"]), rng.randrange(1 << 30),
                            sp.get("stat_template")]
                    good = self._regen_proc(spec)
                    src = {"proc": spec}
                if good is None:
                    continue
                g = self.going(good)
                unit = g * rng.uniform(0.85, 1.6)
                self._new_auction("horde", good, src, m.name, "recruit:" + m.name, unit, 24)

    def _near_level(self, what, level):
        es = [e for b in self._pools().get(what, {}).values() for e in b if abs(int(e.level or 1) - level) <= 6]
        if not es:
            return None
        return self.rng.choices(es, weights=[max(0.01, e.weight) for e in es], k=1)[0]

    # ------------------------------------------------------------ save
    def to_dict(self):
        books = {}
        for m, b in self.books.items():
            rows = []
            for a in b.values():
                if "good" in (a.src or {}) and a.src["good"] is None:
                    continue
                rows.append(a.to_row())
            books[m] = rows
        # COMPRESSED. Five times the listings (Kyle, 16 Nov 2026: "I want this AH fleshed out 5 times over") made
        # the books eight megabytes of a save; zlib takes them to about two. Saves from before load either way.
        import base64
        import zlib
        packed = base64.b64encode(zlib.compress(json.dumps(books, separators=(",", ":")).encode("utf-8"), 6))
        return {"clock": self.clock, "play_seconds": self.play_seconds, "next_id": self.next_id,
                "books_z": packed.decode("ascii"),
                "idx": self.idx, "news": self.news, "favourites": sorted(self.favourites),
                "my_bids": sorted(self.my_bids), "recruit_seen": sorted(self.recruit_seen),
                "undercut_by": self.undercut_by, "started": self.started, "bulk": self.bulk,
                "fields": list(Auction.__slots__),
                "cod_sent": self.cod_sent}

    @classmethod
    def from_dict(cls, d):
        m = cls()
        d = d or {}
        m.clock = float(d.get("clock", 0.0))
        m.play_seconds = float(d.get("play_seconds", 0.0))
        m.next_id = int(d.get("next_id", 1))
        m.idx = {k: list(v) for k, v in (d.get("idx") or {}).items()}
        m.news = list(d.get("news") or [])
        m.favourites = set(d.get("favourites") or [])
        m.my_bids = set(d.get("my_bids") or [])
        m.recruit_seen = set(d.get("recruit_seen") or [])
        m.undercut_by = dict(d.get("undercut_by") or {})
        m.started = bool(d.get("started", False))
        m.bulk = {k: [list(r) for r in v] for k, v in (d.get("bulk") or {}).items()}
        m.cod_sent = dict(d.get("cod_sent") or {})
        books = d.get("books") or {}
        if d.get("books_z"):
            import base64
            import zlib
            books = json.loads(zlib.decompress(base64.b64decode(d["books_z"])).decode("utf-8"))
        for mk, rows in books.items():
            if mk not in m.books:
                continue
            fields = d.get("fields")
            for row in rows:
                if isinstance(row, dict):
                    a = Auction.from_dict(row)
                elif fields and list(fields) != list(Auction.__slots__):
                    a = Auction.from_dict(dict(zip(fields, row)))     # a save from before a field was added
                else:
                    a = Auction.from_row(row)
                # an NPC listing of something the catalog no longer sells (a reputation reward, Kyle 16 Nov 2026:
                # "never ever ever ever allow rep items to be sold") comes off the book when the save loads
                src = a.src or {}
                if not a.mine and "entry" in src and src["entry"] not in C.entries():
                    continue
                m._add(a)
        return m


_GEN = None


def _gen():
    global _GEN
    if _GEN is None:
        from entities.loot_generator import LootGenerator
        _GEN = LootGenerator()
    return _GEN


def _c(copper):
    from entities.coins import coins
    return coins(copper)


def market_of(party):
    """The party's market, made on first use (and wired to its mailbox)."""
    m = getattr(party, "market", None)
    if m is None:
        m = Market()
        party.market = m
    if getattr(party, "mail", None) is None:
        from world.mail import Mailbox
        party.mail = Mailbox()
    m.mail = party.mail
    m.party = party
    _IN_PARTY.clear()
    _IN_PARTY.update(getattr(x, "name", "") for x in list(getattr(party, "members", [])) + list(getattr(party, "bench", [])))
    return m


# ------------------------------------------------------------------ hooks the rest of the game calls
_LIVE = {"zone_manager": None, "party": None}


def bind_live(zone_manager=None, party=None):
    if zone_manager is not None:
        _LIVE["zone_manager"] = zone_manager
    if party is not None:
        _LIVE["party"] = party


def on_quest_turned_in(party):
    try:
        market_of(party).on_event("quest")
    except Exception as exc:
        print(f"market: quest tick failed: {exc}")


def on_hearth(party):
    try:
        market_of(party).on_event("hearth")
    except Exception as exc:
        print(f"market: hearth tick failed: {exc}")


def on_boss_down(party, enemies):
    """The last boss of a dungeon just fell: +6 market hours, and the recruits list their loot. Kyle: "+6 dungeon
    when LAST boss is killed". Only once per visit (the cave is marked, so a wipe-and-retry can't double it)."""
    try:
        if not any(getattr(e, "is_boss", False) for e in enemies or []):
            return False
        zm = _LIVE.get("zone_manager")
        if zm is None or not zm.is_in_cave():
            return False
        zone = zm.current_zone
        from world.zone_classification import is_dungeon
        if not is_dungeon(getattr(zone, "name", "")):
            return False
        if zm.cave_spawns.boss_alive() or getattr(zone, "boss_defeated", False):
            return False
        zone.boss_defeated = True          # also what the "dungeon_clear" banter has been waiting for
        m = market_of(party)
        m.on_event("dungeon")
        level = max((int(getattr(e, "level", 1) or 1) for e in enemies), default=1)
        m.recruits_list_loot(party, level)
        return True
    except Exception as exc:
        print(f"market: dungeon tick failed: {exc}")
        return False
