#!/usr/bin/env python3
"""The bank stores things, charges for tabs, and does not eat items.

    PYTHONPATH=. python3 tools/qa_bank.py

A STORAGE SYSTEM FAILS BY LOSING THINGS, and losing things is silent. Nothing crashes when a full bank
swallows an item, when a withdraw into full bags deletes it, or when a save round-trip drops the sparse
slots - the player just finds out, much later, that the thing they put away is gone. So this tests the
loop rather than the parts: put real items in, take them out, buy tabs with real money, save, load, and
count everything at every step.

It also checks the things that are data rather than code: MerchantTusk exists in each major city, is a
banker, is a troll, and stands on a walkable tile.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from entities.bank import Bank, SLOTS_PER_TAB, MAX_TABS, TAB_PRICES, gold_str  # noqa: E402

from world.zone_keys import zone_key  # noqa: E402

#: The cities Kyle said get a banker: "Major cities only should have bankers."
#: Canonical zone keys (see world/zone_keys.py), not display names - this
#: used to be a hand-written {slug: display name} map, which was a SEVENTH
#: private answer to the question that file exists to answer once. It also
#: had "Undercity" capitalised among two lowercase slugs, and it is what
#: made this check report the Booty Bay banker as standing on an unwalkable
#: tile: the lookup missed (the real zone key is "Booty Bay", not
#: "booty_bay"), is_walkable was never called, and `not None` read as "not
#: walkable". Both sides of the lookup go through zone_key now, which is
#: the invariant world/zone_keys.py is for, and a lookup miss is reported
#: as a miss rather than as a different failure.
MAJOR_CITIES = {zone_key(z) for z in ("Orgrimmar", "Undercity", "Freewind Post")}


def main():
    fails = []

    print("== the curve")
    print("  " + "  ".join(f"tab{i+1} {gold_str(p) if p else 'free'}" for i, p in enumerate(TAB_PRICES)))
    print(f"  {MAX_TABS} tabs x {SLOTS_PER_TAB} = {MAX_TABS * SLOTS_PER_TAB} slots, "
          f"{gold_str(sum(TAB_PRICES))} all in")

    print("\n== buying tabs costs exactly what it says")
    from entities.character import Character
    from entities.party import Party
    player = Character("QA", "Warrior")
    party = Party(player)
    bank = party.bank
    party.copper = sum(TAB_PRICES)
    for want in range(1, MAX_TABS):
        price = bank.next_tab_price()
        before = party.copper
        ok, msg = bank.buy_tab(party)
        if not ok:
            fails.append(f"could not buy tab {want+1} with the exact money: {msg}")
            break
        if before - party.copper != price:
            fails.append(f"tab {want+1} charged {before - party.copper}, priced at {price}")
    print(f"  bought up to {bank.tabs_owned} tabs, {bank.capacity} slots, purse left "
          f"{party.get_currency_string()}")
    if party.copper != 0:
        fails.append(f"buying every tab with exactly the listed total left {party.copper} copper over")
    ok, msg = bank.buy_tab(party)
    print(f"  buying an eighth: {msg}")
    if ok:
        fails.append("bought a tab beyond MAX_TABS")

    print("\n== a poor party cannot buy a tab")
    p2 = Party(Character("Broke", "Mage"))
    p2.copper = TAB_PRICES[1] - 1
    ok, msg = p2.bank.buy_tab(p2)
    print(f"  {gold_str(p2.copper)} against a {gold_str(TAB_PRICES[1])} tab: {msg}")
    if ok or p2.bank.tabs_owned != 1:
        fails.append("a party that could not afford a tab got one anyway")
    if p2.copper != TAB_PRICES[1] - 1:
        fails.append("a failed tab purchase still took money")

    print("\n== a full bank refuses rather than eating the item")
    from entities.loot_generator import LootGenerator
    lg = LootGenerator()
    small = Bank(1)
    for i in range(SLOTS_PER_TAB):
        small.deposit(lg.generate_item_for_class("Warrior", 20, rarity="common"))
    doomed = lg.generate_item_for_class("Warrior", 20, rarity="rare")
    spot = small.deposit(doomed)
    print(f"  {small.used}/{small.capacity} used, depositing one more returned {spot}")
    if spot is not None:
        fails.append("a full bank accepted an item - something was overwritten")

    print("\n== items survive a save and keep their slots")
    party.bank = Bank(3)
    gear = lg.generate_item_for_class("Warrior", 30, rarity="rare")
    loot = lg.generate_bag(player_level=20)
    party.bank.deposit(gear, 0)
    party.bank.tabs[2][SLOTS_PER_TAB - 1] = loot          # last slot of the last tab, sparse
    before = party.bank.used
    blob = json.loads(json.dumps(party.to_dict()))        # through real JSON, not just dicts
    restored = Party.from_dict(blob, player)
    rb = restored.bank
    print(f"  {before} items, {party.bank.tabs_owned} tabs -> reloaded {rb.used} items, "
          f"{rb.tabs_owned} tabs")
    if rb.used != before or rb.tabs_owned != party.bank.tabs_owned:
        fails.append(f"save round-trip changed the bank: {before}/{party.bank.tabs_owned} -> "
                     f"{rb.used}/{rb.tabs_owned}")
    kept = rb.get(2, SLOTS_PER_TAB - 1)
    print(f"  far slot (tab 3, slot {SLOTS_PER_TAB}): {getattr(kept, 'name', None)}")
    if kept is None or kept.name != loot.name:
        fails.append("an item in a high slot index did not survive the round-trip")
    first = rb.get(0, 0)
    if first is None or type(first).__name__ != type(gear).__name__:
        fails.append(f"item class changed across save: {type(gear).__name__} -> "
                     f"{type(first).__name__ if first else None}")

    print("\n== a save written before the bank existed still loads")
    legacy = {k: v for k, v in blob.items() if k != "bank"}
    old = Party.from_dict(legacy, player)
    print(f"  no 'bank' key -> {old.bank.tabs_owned} tab, {old.bank.capacity} slots, "
          f"{old.bank.used} items")
    if old.bank.tabs_owned != 1 or old.bank.used != 0:
        fails.append("a pre-bank save did not come back with one empty free tab")

    print("\n== MerchantTusk is in every major city and nowhere else")
    from world.zone_generator import create_all_zones
    Z = {zone_key(name): zone for name, zone in create_all_zones().items()}
    npcs = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text())["npcs"]
    bankers = [n for n in npcs if n.get("is_banker")]
    seen = set()
    for n in bankers:
        z = Z.get(zone_key(n["zone"]))
        walk = z.is_walkable(n["x"], n["y"]) if z else "NO SUCH ZONE"
        print(f"  {n['npc_id']:<12}{n['name']:<14}{n['zone']:<16}{(n['x'], n['y'])} "
              f"race={n.get('race')} walkable={walk}")
        seen.add(zone_key(n["zone"]))
        if n["name"] != "MerchantTusk":
            fails.append(f"{n['npc_id']} is a banker but is not MerchantTusk")
        if n.get("race") != "troll":
            fails.append(f"{n['npc_id']} is not a troll")
        if z is None:
            fails.append(f"{n['npc_id']} names zone {n['zone']!r}, which no "
                         f"generated zone matches")
        elif not walk:
            fails.append(f"{n['npc_id']} stands on an unwalkable tile - unreachable")
    missing = set(MAJOR_CITIES) - seen
    extra = seen - set(MAJOR_CITIES)
    if missing:
        fails.append(f"major cities with no banker: {sorted(missing)}")
    if extra:
        fails.append(f"bankers outside the major cities (Kyle: major cities only): {sorted(extra)}")

    print()
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
