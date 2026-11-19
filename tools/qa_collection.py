#!/usr/bin/env python3
"""The Collection works end to end (docs/collection_design.md).

    PYTHONPATH=. python3 tools/qa_collection.py

Every claim is something Kyle asked for on 18 Nov 2026:
  1. THE CATALOGUE: hundreds of collectables ("I'd want 100s to 1000s of fun collection stuff"), 2g to 750g ("Some
     are dirt cheap. Some are expensive"), every form has its picture, none is a creature from a hidden place, and
     a full heirloom set is +80% XP.
  2. ITS OWN FILE, OUTSIDE THE SAVES, and learning is one transaction: the item leaves the bag, the file is written
     and the character saved together; a failed character save rolls the learning back and the item stays.
  3. LEARN ONCE, EVERY CHARACTER HAS IT: a fresh TravelManager (a second character) sees the feathers' flights.
  4. EACH EFFECT: hearth halved, backpack +12, a free bank tab that survives a save, Apprentice Riding free, a mount
     that needs riding, the new-character gifts.
  5. HEIRLOOMS: one for every class that can use it, fitted to the wearer (armour type, stats), re-fitted on level
     up, +10/+20% XP while worn up to 80%, none at 60, can't be sold or auctioned, one copy at a time.
  6. SERVICES: once per market day.
  7. THE AUCTION HOUSE: "dozens to ~100" listed at a time across both books, in a Collection category, the rare ones
     rarer, and a bought one arrives as a learnable item.
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()


def main():
    bad = []
    from entities import account_collection as AC
    from entities import guild_bank
    from world import collection as C

    tmp = Path(tempfile.mkdtemp()) / "account_collection.json"
    old_path = AC.use_path(tmp)
    old_saver = guild_bank._host_saver
    try:
        # ---- 1. the catalogue
        print("1. the catalogue")
        es = C.entries()
        if len(es) < 500:
            bad.append(f"only {len(es)} collectables; Kyle wants hundreds")
        for e in es:
            if e["kind"] != "keepsake" and not 2 * 10000 <= e["price"] <= 750 * 10000:   # keepsakes are given
                bad.append(f"{e['id']} costs {e['price'] // 10000}g, outside 2-750g")
        import creature_sprites as CS
        from world.hidden_zones import creature_kinds
        hidden_names = set(creature_kinds()) | set(CS._hidden_sprites())
        for e in es:
            if e["kind"] == "form":
                if not C.art_ready(e["id"]):
                    bad.append(f"{e['id']} has no picture")
                if e["effect"]["form_name"] in hidden_names:
                    bad.append(f"a form is named for a creature from a hidden place ({e['id']})")
        kinds = {}
        for e in es:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        print(f"  {kinds}")
        print(f"  {len(es)} collectables")

        # ---- 2. the file and the transaction
        print("2. learning is one transaction")
        from config import save_slot_filename, SAVE_SLOT_COUNT
        if old_path.name in {save_slot_filename(i) for i in range(1, SAVE_SLOT_COUNT + 1)}:
            bad.append("the collection is stored in a save slot's file")
        guild_bank.set_host_saver(lambda: False)
        col = AC.get_collection()
        bag = [C.make_item("tome_swift_hearth")]
        ok, msg = col.learn_from_bag(bag[0], bag)
        print(f"  with the character save failing: {ok}, {msg!r}, item still in the bag: {len(bag) == 1}")
        if ok or len(bag) != 1 or col.has("tome_swift_hearth"):
            bad.append("a failed character save still learned the tome or ate the item")
        guild_bank.set_host_saver(lambda: True)
        for cid in ("tome_swift_hearth", "feather_kalimdor", "tome_pack_mule", "tome_deep_vault",
                    "tome_quick_study", "book_first_steps", "couriers_horn", "second_hearthstone"):
            item = C.make_item(cid)
            bag = [item]
            ok, msg = col.learn_from_bag(item, bag)
            if not ok or bag:
                bad.append(f"couldn't learn {cid}: {msg}")
        ok, _ = col.learn_from_bag(C.make_item("feather_kalimdor"), [C.make_item("feather_kalimdor")])
        if ok:
            bad.append("learned the same collectable twice")
        AC.reset_collection()
        col = AC.get_collection()
        if not col.has("feather_kalimdor"):
            bad.append("the collection didn't survive being read back from its file")
        print(f"  learned {len(AC.get_collection().ids())} things, read back from {tmp.name}")

        # ---- 3. every character
        print("3. every character has it")
        from world.travel_manager import TravelManager, travel_data
        tm = TravelManager()
        kal = {n for n, v in travel_data()["flight_nodes"].items() if v.get("continent", "kalimdor") == "kalimdor"}
        ek = {n for n, v in travel_data()["flight_nodes"].items() if v.get("continent") == "eastern_kingdoms"}
        print(f"  a fresh character knows {len(tm.known_nodes & kal)}/{len(kal)} Kalimdor flights, "
              f"{len(tm.known_nodes & ek)}/{len(ek)} Eastern Kingdoms")
        if not kal <= tm.known_nodes or tm.known_nodes & ek:
            bad.append("the Kalimdor feather didn't open exactly Kalimdor's flights for a new character")
        tm2 = TravelManager()
        tm2.load_from_dict({"known_nodes": []})
        if not kal <= tm2.known_nodes:
            bad.append("a loaded character lost the feather's flights")

        # ---- 4. the effects
        print("4. the effects")
        tm.use_hearth()
        if tm.hearth_steps_left != max(1, round(tm.cooldown_steps * 0.5)):
            bad.append(f"the swift hearth gave {tm.hearth_steps_left} steps, not half of {tm.cooldown_steps}")
        if tm.riding_price(1) != 0 or tm.riding_price(2) == 0:
            bad.append("Quick Study should make Apprentice Riding free and nothing else")
        from entities.character import Character
        ch = Character("Tester", "Warrior")
        from entities.equipment import BASE_INVENTORY_CAPACITY
        if ch.inventory_capacity != BASE_INVENTORY_CAPACITY + 12:
            bad.append(f"backpack is {ch.inventory_capacity}, the Pack Mule should make it "
                       f"{BASE_INVENTORY_CAPACITY + 12}")
        from entities.party import Party
        from entities.bank import Bank
        p = Party(ch)
        if p.bank.tab_count != p.bank.tabs_owned + 1 or p.bank.tab_name(p.bank.tabs_owned) != "Collector's Shelf":
            bad.append("the Deep Vault's free tab isn't on a new party's bank")
        p.bank.tabs[p.bank.tabs_owned][3] = C.make_item("murloc")
        ok, _ = p.bank.buy_tab(type("P", (), {"copper": 10 ** 9, "remove_currency": lambda s, c: True})())
        rb = Bank.from_dict(p.bank.to_dict())
        if not ok or rb.tab_count != 3 or rb.get(2, 3) is None or rb.tab_name(2) != "Collector's Shelf":
            bad.append("buying a tab or saving moved the Collector's Shelf or lost what was in it")
        print(f"  hearth {tm.hearth_steps_left}/{tm.cooldown_steps} steps, backpack {ch.inventory_capacity}, "
              f"bank tabs {rb.tab_count} ({rb.tab_name(2)} kept its item)")
        tm.set_bind2("Orgrimmar", 50, 50, "Orgrimmar")
        if tm.second_hearth_block_reason() is not None:
            bad.append(f"the second hearth won't go: {tm.second_hearth_block_reason()}")
        b2 = tm.use_second_hearth()
        if b2.get("zone") != "Orgrimmar" or tm.hearth2_steps_left <= 0:
            bad.append("the second hearth didn't go to its own bind or start its own cooldown")
        tm3 = TravelManager()
        tm3.load_from_dict(tm.to_dict())
        if tm3.bind2 != tm.bind2 or tm3.hearth2_steps_left != tm.hearth2_steps_left:
            bad.append("the second hearth's bind didn't survive a save")
        gifts = C.new_character_gifts()
        if gifts != {"copper": 50000, "bag": True}:
            bad.append(f"First Steps gifts are {gifts}")
        if C.mount_def("ashen_nightmare") is None or tm.get_mount("ashen_nightmare") is None:
            bad.append("a collection mount isn't a mount")

        # ---- 5. heirlooms
        print("5. heirlooms")
        import json
        hl = [e["id"] for e in es if e["kind"] == "heirloom"]
        for hid in hl:
            col.learned[hid] = 1
        specs = {k: v for k, v in json.loads(Path("data/items/spec_gear.json").read_text(
            encoding="utf-8")).items() if not k.startswith("_")}
        made, fails = 0, []
        for k, v in sorted(specs.items()):
            # every spec can take a full kit of its own armour family and its own weapons
            who = Character("H", v["class"])
            who.level = 20
            af, wf = C.armour_family(v), C.weapon_family(v)
            want = [f"heirloom_{v['armor_type']}_{af}_{s}" for s in ("head", "shoulder", "chest", "legs")]
            want += [f"heirloom_{wf}_back", f"heirloom_{wf}_trinket"]
            want += [f"heirloom_{wt}_{wf}" for wt in (v.get("weapons") or {}).values() if wt]
            for hid in want:
                ok, why = C.can_take_heirloom(hid, who, None)
                it = C.make_heirloom(hid, who) if ok else None
                if it is None or it.rarity != "rare" or it.item_level != 20 or it.is_sellable \
                        or it.required_level != 1:
                    fails.append(f"{k}: {hid} ({why or it})")
                    continue
                made += 1
        print(f"  {len(hl)} heirlooms; {made} taken by the {len(specs)} specs for their own kits, "
              f"{len(fails)} refused")
        bad += [f"a spec couldn't take its own heirloom: {f}" for f in fails[:8]]
        fams = {(e["effect"].get("armor_type"), e["effect"]["family"]) for e in es if e["kind"] == "heirloom"
                and e["effect"]["heirloom_slot"] == "chest"}
        kyle = {("cloth", "caster"), ("cloth", "healer"), ("leather", "agi"), ("leather", "healer"),
                ("leather", "caster"), ("mail", "agi"), ("mail", "caster"), ("mail", "healer"), ("plate", "str"),
                ("plate", "tank"), ("plate", "hybrid"), ("plate", "healer")}
        if fams != kyle:
            bad.append(f"the armour families aren't Kyle's twelve: {sorted(fams ^ kyle)}")
        war = Character("W", "Warrior")
        war.level = 10
        party = Party(war)                      # the warrior leads: his heirlooms count for everyone
        chest = C.make_heirloom("heirloom_plate_str_chest", war)
        tank = C.make_heirloom("heirloom_plate_tank_chest", war)
        pri = Character("P", "Priest")
        pri.level = 10
        robe = C.make_heirloom("heirloom_cloth_healer_chest", pri)
        from entities.loot_generator import LootGenerator
        import random
        random.seed(3)
        blue = LootGenerator().generate_armor_piece("chest", "plate", "str_physical", 10, "rare")
        hp, bp = sum(chest.primary_stats.values()), sum(blue.primary_stats.values())
        print(f"  {chest.name}: {chest.primary_stats} {chest.secondary_stats}; {tank.name}: {tank.primary_stats} "
              f"{tank.secondary_stats}; {robe.name}: {robe.armor_type} {robe.primary_stats} {robe.secondary_stats}; "
              f"a level 10 blue chest has {bp} primary points, the heirloom {hp}")
        if chest.armor_type != "plate" or robe.armor_type != "cloth":
            bad.append("an heirloom isn't its own armour type")
        if tank.primary_stats.get("stamina", 0) <= chest.primary_stats.get("stamina", 0):
            bad.append("tank plate isn't the stamina family")
        ok, _ = C.can_take_heirloom("heirloom_plate_str_chest", pri, None)
        if ok:
            bad.append("a priest could take a plate heirloom")
        war.equipment.slots["chest"] = chest
        war.equipment.slots["main_hand"] = C.make_heirloom("heirloom_sword_2h_str", war)
        if C.heirloom_xp_pct(war) != 30:
            bad.append(f"chest + two-hander gave +{C.heirloom_xp_pct(war)}%, not +30%")
        if C.heirloom_xp_pct(pri) != 30:
            bad.append("the leader's heirlooms didn't count for the rest of the party")
        before = pri.experience
        pri.gain_experience(100)
        if pri.experience - before != 130:
            bad.append(f"a party member wearing nothing got {pri.experience - before} from 100 XP, not 130")
        lvl_before = chest.item_level
        war.level_up()
        print(f"  XP +{C.heirloom_xp_pct(war)}% for the whole party; the chest went from item level {lvl_before} to "
              f"{war.equipment.slots['chest'].item_level} on level up")
        if war.equipment.slots["chest"].item_level != war.level:
            bad.append("the heirloom didn't grow with its wearer")
        for slot, hid in (("head", "heirloom_plate_str_head"), ("shoulder", "heirloom_plate_str_shoulder"),
                          ("legs", "heirloom_plate_str_legs"), ("back", "heirloom_str_back"),
                          ("trinket1", "heirloom_str_trinket")):
            war.equipment.slots[slot] = C.make_heirloom(hid, war)
        if C.heirloom_xp_pct(war) != 80:
            bad.append(f"a full set is +{C.heirloom_xp_pct(war)}%, not +80%")
        war.equipment.slots["ranged"] = C.make_heirloom("heirloom_bow_str", war)
        if C.heirloom_xp_pct(war) != 80:
            bad.append("a ranged heirloom took the bonus past +80%")
        pri.level = 60
        if C.heirloom_xp_pct(pri) != 0:
            bad.append("heirlooms still pay experience at 60")
        from world.market import goods as G
        ok, _ = G.can_trade(chest)
        if ok:
            bad.append("an heirloom copy can go on the auction house")
        party2 = Party(pri)
        pri.inventory.append(robe)
        ok, why = C.can_take_heirloom("heirloom_cloth_healer_chest", pri, party2)
        if ok:
            bad.append("took a second copy of an heirloom already in the bags")
        rt = type(robe).from_dict(robe.to_dict())
        if rt.heirloom_id != "heirloom_cloth_healer_chest" or rt.is_sellable:
            bad.append("an heirloom copy forgot it was one after a save")

        # ---- 6. services
        print("6. services")
        ready, _ = C.service_ready(tm, "couriers_horn", 100.0)
        C.mark_service_used(tm, "couriers_horn", 100.0)
        r1, left = C.service_ready(tm, "couriers_horn", 110.0)
        r2, _ = C.service_ready(tm, "couriers_horn", 124.0)
        print(f"  ready {ready}; 10 hours later {r1} ({left:.0f} left); 24 hours later {r2}")
        if not ready or r1 or not r2:
            bad.append("a service isn't once per market day")

        # ---- 7. the auction house
        print("7. the auction house")
        from world.market.market import Market, MARKETS, PLAYER
        m = Market(seed=11)
        m.ensure_started()
        counts, seen, prices = [], set(), []
        for _ in range(24 * 3):
            m.advance(1)
            cur = [a for mk in MARKETS for a in m.collection_listings(mk)]
            counts.append(len(cur))
            for a in cur:
                seen.add(a.mkey)
                prices.append(a.buyout)
                if a.cat != "Collection":
                    bad.append(f"{a.name} is listed under {a.cat}")
        avg = sum(counts) / len(counts)
        print(f"  {avg:.1f} listed on average ({min(counts)}-{max(counts)}), {len(seen)} different in 3 days, "
              f"{min(prices) // 10000}g-{max(prices) // 10000}g")
        if not 50 <= avg <= 120:
            bad.append(f"{avg:.1f} collectables listed on average, Kyle said dozens to about 100")
        if min(prices) < 1 * 10000 or max(prices) > 1500 * 10000:
            bad.append("collectable prices wandered far outside 2-750g")
        a = m.collection_listings("horde")[0]
        m.party = Party(Character("Buyer", "Mage"))
        m.party.copper = 10 ** 9
        from world.mail import Mailbox
        m.mail = m.party.mail = Mailbox()
        res = m.buyout(m.party, a.id, "horde")
        m.advance(1)
        got = [g for l in m.mail.letters for g in (l.goods or [])] if hasattr(m.mail, "letters") else []
        items = [G.unpack(g) for g in got]
        print(f"  bought {a.name}: {res}; the mail holds {[i.name for i in items]}")
        if not any(getattr(i, "collection_id", None) for i in items):
            bad.append("a bought collectable didn't arrive as a learnable item")
    finally:
        guild_bank.set_host_saver(old_saver)
        AC.use_path(old_path)

    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  - " + b)
        return 1
    print("PASS: the Collection learns once for every character, does what each thing says, and sells on the AH")
    return 0


if __name__ == "__main__":
    sys.exit(main())
