#!/usr/bin/env python3
"""Run the auction house market (world/market/market.py) and print how it FEELS, as numbers.

    PYTHONPATH=. python3 tools/sim_auction_market.py [--quick]

docs/auction_house_design.md promises a feel: fair prices sell, greed never does, undercutters jump you about a
third of the time, NPCs outbid you sometimes, fat fingers live a couple of hours, prices wander but stay clamped.
This measures each promise by playing it out many times, so a change to any constant shows up here as a change in
the table rather than as a vague sense that the auction house got weird.
"""
import math
import random
import sys
import time
import types

from world.market import catalog as C
from world.market import goods as G
from world.market.market import Market, MARKETS, PLAYER, min_next_bid
from world.mail import Mailbox


class FakeParty:
    def __init__(self):
        self.copper = 10 ** 9
        self.player = types.SimpleNamespace(name="Kyle", level=60, char_class="Warrior", inventory=[], materials=[],
                                            consumables=[], inventory_capacity=999)
        self.members = [self.player]
        self.bench = []
        self.mail = Mailbox()

    def add_currency(self, n):
        self.copper += n

    def remove_currency(self, n):
        if self.copper >= n:
            self.copper -= n
            return True
        return False


def fresh(seed):
    m = Market(seed=seed)
    p = FakeParty()
    m.mail, m.party = p.mail, p
    return m, p


def base_market(seed=1, competitors=None):
    """A lean market for one trial: no background book (the background doesn't touch the key being measured),
    just the clock started. competitors: [(good, unit price)] NPC listings of the same thing, like a real book."""
    import world.market.market as MM
    for k in MM.MARKETS:
        MM.MARKETS[k]["target"] = 0
    m, p = fresh(seed)
    m.started = True
    for good, unit in competitors or []:
        m._new_auction("horde", good, {"good": good}, "Somebody Else", "n:Somebody Else", unit, 48)
    return m, p


def list_raw(m, market, good, unit_price, duration=24, bid_only=False, min_bid=None):
    """Put a good up as the player without needing a real character."""
    a = m._new_auction(market, good, {"good": good}, "Kyle", PLAYER, unit_price, duration, bid_only=bid_only,
                       deposit=0, min_bid_total=min_bid)
    if min_bid:
        a.min_bid = min_bid
    return a


def sale_rate(kind_key, ratio, trials, hours=24, market="horde"):
    sold = undercut = 0
    for t in range(trials):
        m, p = base_market()
        m.rng.seed(1000 + t)
        if kind_key.startswith("proc:"):
            rarity = kind_key.split(":")[1]
            spec = ["Warrior", 40, rarity, 77 + t, "str_physical"]
            good = m._regen_proc(spec)
        else:
            e = C.entries()[kind_key]
            good = e.make(5 if e.kind != G.GEAR else 1)
            g = m.going(good)
            # a real book has a few others selling the same thing, mostly a bit dearer than going
            for i in range(3):
                m._new_auction("horde", good, {"good": good}, "Somebody Else", "n:Somebody Else",
                               g * m.rng.uniform(0.95, 1.3), 48)
        g = m.going(good)
        a = list_raw(m, market, good, g * ratio, duration=hours)
        mid = a.id
        n0 = len(p.mail.letters)
        m.advance(hours)
        got = [x for x in p.mail.letters[n0:] if x.kind == "auction_sold"]
        if got:
            sold += 1
        if a.undercuts:
            undercut += 1
    return sold / trials, undercut / trials


def outbid_rate(ratio, trials, hours=24):
    outbid = 0
    for t in range(trials):
        m, p = base_market()
        m.rng.seed(5000 + t)
        good = m._regen_proc(["Warrior", 40, "uncommon", 900 + t, "str_physical"])
        g = m.going(good)
        a = m._new_auction("horde", good, {"good": good}, "Somebody", "n:Somebody", g * 3.0, hours,
                           min_bid_total=max(1, int(g * 0.3)))
        a.bid, a.bidder = max(a.min_bid, int(g * ratio)), PLAYER
        m.my_bids.add(a.id)
        m.advance(hours)
        if any(x.kind == "outbid" for x in p.mail.letters):
            outbid += 1
    return outbid / trials


def fat_life(trials=60):
    lives = []
    for t in range(trials):
        m, p = base_market()
        m.rng.seed(9000 + t)
        e = C.entries()["m:cloth_silk"] if "m:cloth_silk" in C.entries() else next(iter(C.entries().values()))
        good = e.make(20)
        g = m.going(good)
        a = m._new_auction("horde", good, {"entry": e.key}, "Fumbles", "n:Fumbles", g / 100, 48, fat=True,
                           meant=int(g * 20))
        h = 0
        while a.id in m.books["horde"] and h < 48:
            m.advance(1)
            h += 1
        lives.append(h)
    lives.sort()
    return sum(lives) / len(lives), lives[len(lives) // 2]


def clamp_year():
    m, p = base_market()
    keys = [k for k, e in C.entries().items() if e.kind == G.MATERIAL][:40]
    lo, hi = 9.0, 0.0
    for day in range(365):
        for k in keys[:5]:                    # a hostile player dumps five things every day
            m.shock(k, -5.0)
        for k in keys[5:10]:                  # and buys out five others
            m.shock(k, +5.0)
        m.advance(24 if day % 10 else 72)
        for k in keys:
            i = m.index(k)
            lo, hi = min(lo, i), max(hi, i)
    return lo, hi


def greed_never(trials=40):
    """Listings at 2.5x and up: how many ever sold in a long run."""
    sold = 0
    for t in range(trials):
        m, p = base_market()
        m.rng.seed(7000 + t)
        e = C.entries()["m:herb_peacebloom"]
        good = e.make(5)
        g = m.going(good)
        list_raw(m, "horde", good, g * 2.6, duration=48)
        m.advance(48)
        sold += sum(1 for x in p.mail.letters if x.kind == "auction_sold")
    return sold


def main():
    quick = "--quick" in sys.argv
    n = 40 if quick else 150
    t0 = time.time()
    m, p = fresh(1)
    m.ensure_started()       # the full book, for the timing line (before base_market empties the targets)
    t1 = time.time()
    m.advance(24)
    t2 = time.time()
    print(f"fill {t1 - t0:.1f}s, one market day {t2 - t1:.2f}s ({(t2 - t1) / 24 * 1000:.0f} ms an hour); "
          f"{sum(len(b) for b in m.books.values())} listings; stats {m.stats}")
    print()
    print("SALE CHANCE IN 24 HOURS (and chance an undercutter jumped you)")
    for key, label in (("m:herb_peacebloom", "Peacebloom x5"), ("m:cloth_silk", "Silk Cloth x5"),
                       ("proc:uncommon", "a green, level 40"), ("proc:rare", "a blue, level 40")):
        if not key.startswith("proc:") and key not in C.entries():
            continue
        row = []
        for r in (0.7, 1.0, 1.3, 1.6, 2.0, 2.6):
            s, u = sale_rate(key, r, n)
            row.append(f"{r:.1f}x {s * 100:4.0f}% ({u * 100:2.0f}%)")
        print(f"  {label:22s} " + "  ".join(row))
    print()
    print("CHANCE YOU GET OUTBID ON A 24 HOUR AUCTION (a green, by your bid as a share of the going price)")
    print("  " + "  ".join(f"{r:.1f}x {outbid_rate(r, n) * 100:4.0f}%" for r in (0.6, 0.8, 1.0, 1.2)))
    print()
    mean, med = fat_life()
    print(f"A FAT FINGER LIVES {mean:.1f} market hours on average (median {med})")
    lo, hi = clamp_year()
    print(f"A HOSTILE YEAR: every index stayed inside [{lo:.2f}, {hi:.2f}] (the clamp is [0.35, 3.00])")
    print(f"GREED: listings at 2.6x the going price that sold in 48 hours: {greed_never()}")


if __name__ == "__main__":
    main()
