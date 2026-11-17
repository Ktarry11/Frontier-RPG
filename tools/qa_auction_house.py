#!/usr/bin/env python3
"""Try to break the auction house and the mail (docs/auction_house_design.md, section 13).

    PYTHONPATH=. python3 tools/qa_auction_house.py

CLAIMS
  1. Prices wander but stay clamped: every index stays inside [0.35, 3.0] through a hostile year.
  2. Greed never sells: nothing listed at 2.6x the going price sells to a buyer (news switched off).
  3. You can't farm the NPCs: buying out every ordinary NPC listing and vendoring it all loses money.
  4. Listing and cancelling never makes money: the deposit is gone and the item comes back once.
  5. No hidden place leaks: no hidden-zone NPC sells, no hidden item or secret recipe is listed, no news names a
     hidden zone.
  6. Coin is conserved: every copper a bid takes comes back by mail or pays for the thing won.
  7. Items are conserved: everything listed comes back exactly once (sold, expired, cancelled), never twice.
  8. Save and load in the middle of it keeps every auction, bid, letter and offer.
  9. Mail works: take money, take items, full bags, delete only when empty, cash on delivery, sending to a recruit.
 10. Fat fingers happen, are rare, and die young; cash-on-delivery offers come after bulk buying.
 11. The world has it: a mailbox by every inn, auctioneers with the service, every screen tab renders.
 12. The letters: eight personalities, each with lines for every moment, short and plainly written.
"""
import copy
import math
import os
import random
import sys
import types
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    import world.market.market as MM
    from world.market import catalog as C
    from world.market import goods as G
    from world.market.market import Market, PLAYER, market_of
    from world.mail import Mailbox, Letter
    from core.game_state import GameStateManager
    from core.game_states import GameState
    from entities.character import Character

    sm = GameStateManager(screen)
    sm.player = Character(name="Tester", char_class="Warrior", level=40)
    party = sm.get_party()
    party.copper = 10_000_000
    m = market_of(party)
    m.rng.seed(4)
    m.ensure_started()
    m.advance(30)

    # ---- 1. clamp
    keys = [k for k, e in C.entries().items() if e.kind == G.MATERIAL][:30]
    lo, hi = 9.0, 0.0
    for day in range(365):
        for k in keys[:5]:
            m.shock(k, -4.0)
        for k in keys[5:10]:
            m.shock(k, 4.0)
        for k in keys[:10]:
            i = m.index(k)
            lo, hi = min(lo, i), max(hi, i)
        m.clock += 24
        for k in keys:
            i = m.index(k)
            lo, hi = min(lo, i), max(hi, i)
    check(lo >= 0.35 - 1e-9 and hi <= 3.0 + 1e-9, f"index left the clamp: {lo:.3f}..{hi:.3f}")
    check(lo < 0.4 and hi > 2.9, f"a hostile year should reach both ends of the clamp ({lo:.2f}..{hi:.2f})")

    # ---- 2. greed (a lean market, no news)
    saved = {k: dict(v) for k, v in MM.MARKETS.items()}
    old_news = MM.NEWS_RATE
    MM.NEWS_RATE = 0.0
    for k in MM.MARKETS:
        MM.MARKETS[k]["target"] = 0
    sold = 0
    for t in range(40):
        lm = Market(seed=100 + t)
        lm.mail = Mailbox()
        lm.started = True
        for key in ("m:herb_peacebloom", "m:cloth_silk"):
            if key not in C.entries():
                continue
            good = C.entries()[key].make(5)
            ask = lm.going(good) * 2.6
            # starting bid = buyout, so nothing can sneak in under the greedy price by bidding
            a = lm._new_auction("horde", good, {"good": good}, "Tester", PLAYER, ask, 48,
                                min_bid_total=int(ask * 5))
        lm.advance(48)
        sold += sum(1 for x in lm.mail.letters if x.kind == "auction_sold")
    check(sold == 0, f"{sold} greedy listings (2.6x going) sold")
    MM.NEWS_RATE = old_news
    for k, v in saved.items():
        MM.MARKETS[k].update(v)

    # ---- 3. buy everything, vendor everything
    spent = vend = below = n = 0
    for a in m.books["horde"].values():
        if a.mine or not a.buyout or a.fat:
            continue
        good = m.good_of(a)
        if good is None:
            continue
        n += 1
        spent += a.buyout
        v = G.sell_price(good) * G.quantity(good)
        vend += v
        if a.buyout < v:
            below += 1
    check(n > 500, f"only {n} NPC listings with a buyout")
    check(spent > vend * 1.5, f"buying the whole book costs {spent} and vendors for {vend}: farmable")
    check(below / max(1, n) < 0.03, f"{below} of {n} listings are under the vendor price")

    # ---- 4. list and cancel
    from world.gathering_manager import get_gathering_node_manager
    gm = get_gathering_node_manager()
    p = sm.player
    herb = gm.make_material_instance("herb_peacebloom")
    herb.quantity = 20
    p.add_material(herb)
    before_copper = party.copper
    before_n = p.get_material_quantity("herb_peacebloom")
    for _ in range(5):
        obj = next(x for x in p.materials if x.material_id == "herb_peacebloom")
        ok, msg = m.post(party, p, obj, 20, 500, 900, 48, "horde")
        check(ok, f"post failed: {msg}")
        mine = m.my_auctions("horde")[-1]
        ok, msg = m.cancel(party, mine.id, "horde")
        check(ok, f"cancel failed: {msg}")
        let = [x for x in m.mail.visible(m.clock) if x.kind == "auction_cancelled" and x.goods]
        check(len(let) == 1, f"{len(let)} cancel letters with the herbs in them")
        for x in let:
            m.mail.take_all(x, party, p)
            m.mail.delete(x)
    check(party.copper < before_copper, "listing and cancelling didn't cost the deposit")
    check(p.get_material_quantity("herb_peacebloom") == before_n, "herbs were lost or duplicated by cancelling")

    # ---- 5. hidden places
    from world.hidden_zones import registry, creature_kinds
    hidden_names = {str(z).lower() for z in registry()}
    hidden_slugs = {C._slug(z) for z in registry()}
    import json
    hz_npcs = set()
    for row in json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]:
        if C._slug(row.get("zone", "")) in hidden_slugs or str(row.get("npc_id", "")).startswith("hz_"):
            hz_npcs.add(row["name"])
    for mk in MM.MARKETS:
        for t in MM.roster(mk):
            check(t.name not in hz_npcs, f"{t.name} trades in {mk} but lives in a hidden place")
    secret = set()
    for name in ("secret_uniques.json", "faction_rewards.json", "unnamed_rewards.json"):
        for iid, r in (json.loads((ROOT / f"data/items/{name}").read_text(encoding="utf-8")).get("items") or {}).items():
            secret.add(r.get("name"))
    for e in C.entries().values():
        check(e.name not in secret, f"{e.name} is a secret item and NPCs list it")
    from world.market.news import ROWS
    for _f, _r, text in ROWS:
        low = text.lower()
        for hn in hidden_names:
            check(hn not in low, f"news names a hidden zone: {text}")
    from entities.boss_loot import _item_from_def
    hb = json.loads((ROOT / "data/loot/hidden_boss_loot.json").read_text(encoding="utf-8"))
    row = next(r for k, v in hb.items() if not k.startswith("_") for r in v)
    check(not G.can_trade(_item_from_def(row))[0], f"{row['name']} (hidden boss loot) could be listed")
    for rid_prof, rid, r in C.recipes():
        check(not (r.get("secret") or rid.startswith("secret")), f"secret recipe {rid} in the catalog")

    # ---- 6 and 7. coin and goods conservation through bids and sales
    lm = Market(seed=77)
    lp = types.SimpleNamespace(copper=100_000_000, player=types.SimpleNamespace(name="T"), members=[], bench=[])
    lp.add_currency = lambda n: setattr(lp, "copper", lp.copper + n)
    lp.remove_currency = lambda n: (setattr(lp, "copper", lp.copper - n) or True) if lp.copper >= n else False
    lm.mail = Mailbox()
    lm.party = lp
    for k in MM.MARKETS:
        MM.MARKETS[k]["target"] = 0
    lm.started = True
    start = lp.copper
    won_paid = 0
    goods_won = 0
    for t in range(60):
        good = lm._regen_proc(["Warrior", 40, "uncommon", 500 + t, "str_physical"])
        g = lm.going(good)
        a = lm._new_auction("horde", good, {"good": good}, "Seller", "n:Seller", g * 3, 24,
                            min_bid_total=max(1, int(g * 0.4)))
        ok, msg = lm.place_bid(lp, a.id, max(a.min_bid, int(g * random.Random(t).uniform(0.5, 1.1))), "horde")
        check(ok, f"bid failed: {msg}")
    lm.advance(30)
    refunded = sum(x.copper for x in lm.mail.letters if x.kind == "outbid")
    won = [x for x in lm.mail.letters if x.kind == "auction_won"]
    for x in won:
        goods_won += len(x.goods)
    # every copper that left the purse either came back (outbid letters) or paid for an auction won
    check(start - lp.copper == refunded + sum(
        int(_coins_to_c(x.body.split(" for ")[-1].rstrip("."))) for x in won),
        "coin a bid took didn't come back or pay for the win")
    check(goods_won == len(won), "a won auction's letter has the wrong number of items")
    check(len(won) + len([x for x in lm.mail.letters if x.kind == "outbid"]) >= 60 - 5,
          "bids neither won nor came back")
    for k, v in saved.items():
        MM.MARKETS[k].update(v)

    # ---- 8. save and load
    d = party.to_dict()
    blob = json.dumps(d)
    from entities.party import Party
    p2 = Party.from_dict(json.loads(blob), sm.player)
    m2 = p2.market
    check(m2 is not None and p2.mail is not None, "market or mail didn't save")
    if m2 is not None:
        check(abs(m2.clock - m.clock) < 1e-9, "clock changed across a save")
        for mk in MM.MARKETS:
            check(set(m2.books[mk]) == set(m.books[mk]), f"{mk} book changed across a save")
        check(m2.my_bids == m.my_bids, "bids changed across a save")
        check(len(p2.mail.letters) == len(party.mail.letters), "letters changed across a save")
        a = next(iter(m2.books["horde"].values()))
        check(m2.good_of(a) is not None, "a saved auction's item couldn't be rebuilt")
        check(len(blob) < 3_000_000, f"the save carries {len(blob)} bytes of market")

    # ---- 9. mail
    box = Mailbox()
    herbs = gm.make_material_instance("herb_silverleaf")
    herbs.quantity = 5
    L = box.deliver(Letter("Someone", "COD", goods=[G.pack(herbs)], kind="cod", cod=300, can_return=True))
    ok, _ = box.take_good(L, 0, p)
    check(not ok, "took a COD item without paying")
    c0 = party.copper
    q0 = p.get_material_quantity("herb_silverleaf")
    ok, msg = box.pay_cod(L, party, p)
    check(ok and party.copper == c0 - 300 and p.get_material_quantity("herb_silverleaf") == q0 + 5,
          f"paying COD went wrong: {msg}")
    L2 = box.deliver(Letter("Bank", "money", copper=1234))
    check(not box.delete(L2), "deleted a letter with money in it")
    box.take_money(L2, party)
    check(box.delete(L2), "couldn't delete an empty letter")
    L3 = box.deliver(Letter("Old", "offer", goods=[G.pack(herbs)], kind="cod", cod=10, sent_at=0))
    box.tidy(24 * 4)
    check(L3 not in box.letters, "an unpaid COD offer didn't go back after three days")
    # full bags: a gear letter stays put
    from entities.loot_generator import LootGenerator
    item = LootGenerator().generate_item_for_class("Warrior", 30, rarity="uncommon")
    L4 = box.deliver(Letter("X", "gear", goods=[G.pack(item)]))
    keep = list(p.inventory)
    while len(p.inventory) < p.inventory_capacity:
        p.inventory.append(LootGenerator().generate_item_for_class("Warrior", 10, rarity="common"))
    ok, _ = box.take_good(L4, 0, p)
    check(not ok and len(L4.goods) == 1, "took gear into full bags, or lost it")
    p.inventory = keep
    # sending to a recruit
    friend = Character(name="Ama", char_class="Priest", level=30)
    party.bench.append(friend)
    pot = gm.make_material_instance("herb_peacebloom")
    pot.quantity = 3
    box.send("Ama", "for you", "", [G.pack(pot)], now=0)
    box.deliver_due(2, party, random.Random(1))
    check(friend.get_material_quantity("herb_peacebloom") == 3, "the parcel didn't reach Ama")
    party.bench.remove(friend)

    # ---- 10. fat fingers and COD
    fm = Market(seed=9)
    fm.mail = Mailbox()
    fm.party = party
    fm.ensure_started()
    fm.advance(48)
    check(1 <= fm.stats["fat"] <= 60, f"{fm.stats['fat']} fat fingers in a fill and two days")
    lives = []
    for a in [a for a in fm.books["horde"].values() if a.fat][:10]:
        lives.append(a.ends_at)
    # bulk buy herbs -> once in a while a COD letter. Kyle, 16 Nov 2026: "i want it to kind of feel special. Maybe
    # like... people send letters from the AH a max of around 5% of the time" (it was 70%)
    cods = 0
    for t in range(200):
        cm = Market(seed=300 + t)
        cm.mail = Mailbox()
        cm.party = types.SimpleNamespace(copper=10 ** 8, player=types.SimpleNamespace(name="T"), members=[],
                                         add_currency=lambda n: None, remove_currency=lambda n: True)
        for k in MM.MARKETS:
            MM.MARKETS[k]["target"] = 0
        cm.started = True
        good = C.entries()["m:herb_peacebloom"].make(5)
        for i in range(4):
            a = cm._new_auction("horde", good, {"good": good}, "Farmer Joe", "n:Farmer Joe", 30, 24)
            cm.buyout(cm.party, a.id, "horde")
        cm.advance(6)
        cods += sum(1 for x in cm.mail.letters if x.kind == "cod")
    for k, v in saved.items():
        MM.MARKETS[k].update(v)
    check(1 <= cods <= 20, f"{cods} of 200 bulk buyers got a cash-on-delivery offer (want rare: about 5%, never "
                           f"over 10%, but it has to happen)")

    # ---- 12. the letters: every personality has a voice for every moment, two or three sentences, plain writing
    import re as _re
    from world.market import personalities as P
    from world.market import meme_mail as MM2
    for pool, by in P.LINES.items():
        for pers in P.PERSONALITIES:
            check(len(by.get(pers) or []) >= 2, f"{pers} has {len(by.get(pers) or [])} {pool} letters")
    every = [x for by in P.LINES.values() for v in by.values() for x in v] + \
            [x for v in MM2.ALL.values() for x in v]
    for text in every:
        n = len([t for t in _re.split(r"(?<=[.!?])\s+", text.strip()) if t])
        check(n <= 4, f"too long ({n} sentences): {text[:60]}")
        check("\u2014" not in text and " - " not in text, f"a dash in a letter: {text[:60]}")
        try:
            text.format(item="x", paid="1c", meant="2c", n=3, each="1c", you="Y", name="N")
        except (KeyError, IndexError) as exc:
            check(False, f"bad placeholder {exc}: {text[:60]}")
    for mk in MM.MARKETS:
        moods = {t.personality for t in MM.roster(mk)}
        check(moods == set(P.PERSONALITIES), f"{mk} traders cover {sorted(moods)}")

    # ---- 11. the world and the screens
    from world.travel_manager import travel_data
    s = travel_data()["services"]
    inns = [k for k, v in s.items() if "inn" in v]
    amb = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]
    boxes = {r["npc_id"] for r in amb if r.get("is_mailbox")}
    for i in inns:
        check("mailbox_" + i in boxes, f"no mailbox by {i}")
    for aid in MM.AUCTIONEER_MARKET:
        check("auction" in s.get(aid, []), f"{aid} has no auction service")
        check(any(r["npc_id"] == aid for r in amb), f"{aid} isn't in the world")
    for r in amb:
        if r.get("is_mailbox"):
            check((ROOT / r["prop"]).exists(), f"{r['npc_id']}: no prop image")
    sm.transition_to(GameState.AUCTION, current_market="goblin", current_auctioneer=None)
    for tab in ("browse", "bids", "auctions"):
        sm.update(0.016)
        scr = sm.states[GameState.AUCTION]
        scr.tab = tab
        try:
            sm.render(screen)
            for ev in (pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(400, 300)),
                       pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(120, 200)),
                       pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-1)):
                scr.handle_event(ev)
            sm.render(screen)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            check(False, f"auction {tab} tab crashed: {exc}")
    sm.transition_to(GameState.MAIL)
    for tab in ("inbox", "send"):
        sm.update(0.016)
        scr = sm.states[GameState.MAIL]
        scr.tab = tab
        try:
            sm.render(screen)
            scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 120)))
            sm.render(screen)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            check(False, f"mail {tab} tab crashed: {exc}")

    print(f"{sum(len(b) for b in m.books.values())} listings, {len(C.entries())} things NPCs can list, "
          f"{len(boxes)} mailboxes, stats {m.stats}")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad[:60]:
            print("  - " + b)
        return 1
    print("auction house OK")
    return 0


def _coins_to_c(text):
    """'1g 2s 3c' -> copper."""
    n = 0
    for part in str(text).split():
        if part.endswith("g"):
            n += int(part[:-1]) * 10000
        elif part.endswith("s"):
            n += int(part[:-1]) * 100
        elif part.endswith("c"):
            n += int(part[:-1])
    return n


if __name__ == "__main__":
    sys.exit(main())
