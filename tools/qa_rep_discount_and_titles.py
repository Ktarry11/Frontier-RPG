#!/usr/bin/env python3
"""Reputation makes a town's prices cheaper, and Exalted gives a title.

    PYTHONPATH=. python3 tools/qa_rep_discount_and_titles.py

Kyle, 18 Nov 2026: "each faction should get a title for reaching exalted with them" and "the 5%, 10%, 15%, and 20%
cheaper things for rep. For learning professions, skills, mounts, buying etc. Everything except auction house."
Checks, through the real code:
  1. every faction claims at least one zone (its home or its quest zones), so its discount can apply somewhere,
     except the one that has no home by design
  2. standing in a faction's home: Neutral full price, Friendly 5% off, Honored 10%, Revered 15%, Exalted 20%
  3. every gold price an NPC quotes takes it: a vendor's price, class training, profession training and recipes,
     riding, a stable mount, a flight, a bank tab, the Craftsman's Codex; and a shop shows the note
  4. nothing else does: a barter vendor's token price, what a vendor pays you, and the auction house
  5. every faction has its Exalted title in the Collection, found only; reaching Exalted learns it, once; a save that
     loads already Exalted gets it
"""
import contextlib
import io
import os
import sys
import types
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((8, 8))
    from world import faction_manager as FM
    from world import zone_manager as ZM
    from world import collection as CL
    from entities.account_collection import AccountCollection
    from entities import guild_bank

    fm = FM.get_faction_manager()
    tiers = {t["id"]: t["at"] for t in fm.tiers}

    def stand_in(zone_name):
        ZM.LIVE = types.SimpleNamespace(current_zone=types.SimpleNamespace(name=zone_name))

    def set_tier(fid, tier):
        fm.reset()
        fm.factions[fid].standing = tiers[tier] + 1 if tier != "neutral" else 0

    # A throwaway collection: the real account file is never touched.
    temp = AccountCollection()
    temp.save = lambda: True
    real_collection = CL.collection
    CL.collection = lambda: temp
    saver = guild_bank._host_saver
    guild_bank._host_saver = None
    try:
        # 1 + 2
        for fid, f in fm.factions.items():
            zones = FM.factions_for_zone(f.home_zone) if f.home_zone else []
            if fid == "the_unnamed":
                continue
            if not check(f.home_zone and f in zones, f"{fid} claims no zone, so its discount can't apply anywhere"):
                continue
            stand_in(f.home_zone)
            for tier, pct in (("neutral", 0), ("friendly", 5), ("honored", 10), ("revered", 15), ("exalted", 20)):
                set_tier(fid, tier)
                got = FM.rep_price(10000)
                # another faction sharing the zone may already be better; with everything reset only this one counts
                check(got == 10000 * (100 - pct) // 100, f"{fid} at {tier}: 10000c costs {got}, wanted {pct}% off")

        # 3. every price site, Orgrimmar at Exalted against Neutral
        from entities.character import Character
        with contextlib.redirect_stdout(io.StringIO()):
            ch = Character(name="QA", char_class="Warrior", level=40)
        stand_in("Orgrimmar")

        def prices():
            out = {}
            from ui.screens.vendor_screen import VendorScreen
            vs = VendorScreen.__new__(VendorScreen)
            vs._barter = lambda: None
            out["vendor"] = vs._unit_price(types.SimpleNamespace(vendor_price=10000, sell_price=2500))
            from world import training_manager as TM
            ch.trained_ranks = {}
            ch.training_enabled = True
            offers = TM.offers(ch)
            out["training"] = sum(o["cost"] for o in offers) if offers else None
            from world import profession_manager as PM
            ch.known_professions = []
            rows = PM.offers(ch, "mining")
            out["profession"] = sum(r["cost"] or 0 for r in rows) if rows else None
            from world.travel_manager import get_travel_manager
            tm = get_travel_manager()
            out["riding"] = tm.riding_price(1)
            out["mount"] = tm.mount_price({"price": 100000})
            nodes = list(FM.json.loads((ROOT / "data/travel/travel_data.json").read_text(encoding="utf-8"))
                         ["flight_nodes"])
            out["flight"] = tm.flight_cost(nodes[0], nodes[1])
            from entities.bank import Bank
            out["bank"] = Bank().next_tab_price()
            from world import craftsman_codex as CC
            out["codex"] = CC.price(ch)
            return out

        set_tier("orgrimmar", "neutral")
        base = prices()
        set_tier("orgrimmar", "exalted")
        cheap = prices()
        for k, v in base.items():
            if v in (None, 0):
                continue
            check(cheap[k] is not None and abs(cheap[k] - round(v * 0.8)) <= 1,
                  f"{k}: {v} at Neutral, {cheap[k]} at Exalted, wanted 20% off")
        check(FM.discount_note() == "Exalted with Orgrimmar: 20% off", f"the shop note reads {FM.discount_note()!r}")
        seen = sorted(k for k, v in base.items() if v)
        check({"vendor", "training", "profession", "riding", "mount", "flight", "bank", "codex"} <= set(seen),
              f"rig only priced {seen}")

        # 4. not barter, not selling, not the AH
        from ui.screens.vendor_screen import VendorScreen
        vs = VendorScreen.__new__(VendorScreen)
        vs._barter = lambda: {"prices": {"x": 7}, "default": 7}
        check(vs._unit_price(types.SimpleNamespace(_sells_id="x", vendor_price=10000)) == 7, "a barter price moved")
        market_src = (ROOT / "world/market/market.py").read_text(encoding="utf-8")
        check("rep_price" not in market_src and "discount(" not in market_src, "the auction house reads the discount")
        sell_src = (ROOT / "ui/screens/vendor_screen.py").read_text(encoding="utf-8")
        check(sell_src.count("rep_price(") == 1, "the vendor screen applies the discount somewhere besides its own price")

        # 5. titles
        for fid in fm.factions:
            e = CL.get_entry(CL.exalted_title(fid))
            if check(e is not None, f"{fid} has no Exalted title"):
                check(e["kind"] == "title" and e.get("found_only"), f"{fid}'s title can be sold by traders")
        names = [CL.get_entry(CL.exalted_title(fid))["name"] for fid in fm.factions]
        check(len(set(names)) == len(names), "two factions share a title")
        fm.reset()
        f = fm.factions["cenarion_circle"]
        f.standing = tiers["exalted"] - 10
        gained, tier_up = fm.award("cenarion_circle", 20)
        check(tier_up and tier_up["id"] == "exalted", "the rig didn't reach Exalted")
        check(temp.has("title_exalted_cenarion_circle"), "reaching Exalted didn't learn its title")
        check(CL.exalted_line("cenarion_circle") == "You've earned a title: Guardian of Cenarius.",
              f"the announcement reads {CL.exalted_line('cenarion_circle')!r}")
        n = len(temp.learned)
        fm.award("cenarion_circle", 500)
        check(len(temp.learned) == n, "a title was learned twice")
        fm.reset()
        fm.load_from_dict({"standing": {"the_liquidators": tiers["exalted"] + 5}})
        check(temp.has("title_exalted_the_liquidators"), "a save already Exalted didn't get its title on load")
    finally:
        CL.collection = real_collection
        guild_bank._host_saver = saver
        fm.reset()

    print(f"{len(fm.factions)} factions, five tiers each, every price site checked")
    if fails:
        print(f"FAIL {len(fails)}:")
        for x in fails[:25]:
            print("  ", x)
        return 1
    print("reputation discount and Exalted titles OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
