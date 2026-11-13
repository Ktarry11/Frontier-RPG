"""Three things a playtester should not have to fight: quest drops, a rare quest mob, and beasts.

Kyle, 12 Nov: "For drop rates of quest items, we should have them around 75% (when multiple
drops are needed)"; a friend on Building Something Permanent: "too low of a coconut crab spawn
rate and too low of coral drop rate"; and "For skinning... an item that can buff the party for
improving chance of beasts spawning by 50%."
"""
import json
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)


def main():
    bad = []
    from set_quest_drop_rates import wanted, FLOOR
    most = wanted()
    drops = json.load(open("data/creatures/quest_drops.json"))["drops"]
    low = [(c, d["item_id"], d["chance"]) for c, ds in drops.items() for d in ds
           if most.get(d.get("item_id"), 0) > 1 and d.get("chance", 1) < FLOOR]
    for c, item, chance in low[:10]:
        bad.append(f"{c} drops {item} {chance:.0%} of the time and a quest wants {most[item]}")
    coral = [d["chance"] for d in drops.get("Isle Coconut Crab", []) if d["item_id"] == "sturdy_reef_coral"]
    if coral != [FLOOR]:
        bad.append(f"coral drops at {coral}")

    from world.creature_manager import CreatureManager
    cm = CreatureManager()

    def share(test, n=4000, **kw):
        random.seed(5)
        hits = 0
        for _ in range(n):
            c = cm.get_random_creature("Echo Isles", **kw)
            hits += bool(c is not None and test(c.name))
        return hits / n

    # Kyle, 12 Nov: "coconut crabs which should only be in tidal flats and they're barely spawning."
    crab = lambda name: name == "Isle Coconut Crab"
    if "Isle Coconut Crab" in cm.get_encounter_table("Echo Isles", "open_zone", None):
        bad.append("coconut crabs are in the Echo Isles open-zone table; they belong to the Tidal Flats only")
    flats = dict(location_type="subzone", subzone_name="Tidal Flats")
    plain = share(crab, **flats)
    if plain < 0.33:
        bad.append(f"a coconut crab is {plain:.0%} of Tidal Flats encounters with no quest")
    hunting = share(crab, quest_targets={"Isle Coconut Crab"}, **flats)
    if hunting < 0.6:
        bad.append(f"a coconut crab is only {hunting:.0%} of Tidal Flats encounters while you are hunting it")

    # EVERY SUBZONE: 90% its own, 10% the country around it - or 84 / 6 / 10 with a rare.
    # Kyle, 12 Nov: "subzones also are 90% special mobs (or 84% and 6% if there's a rare). With
    # the other 10% being non-subzone." Worked out of the tables, not sampled.
    checked = 0
    for zone, table in cm.encounters.items():
        open_names = set((table.get("open_zone", {}) or {}).get("creatures", {}) or {})
        for key, sz in (table.get("subzones") or {}).items():
            own = {n: w for n, w in (sz.get("creatures") or {}).items()}
            trash_own = {n: w for n, w in own.items() if w > 0 and not cm.creatures.get(n, {}).get("is_boss")}
            if not trash_own or cm.is_safe_subzone(zone, key):
                continue
            blended = cm.get_encounter_table(zone, "subzone", key)
            trash = {n: w for n, w in blended.items() if w > 0 and not cm.creatures.get(n, {}).get("is_boss")}
            outsiders = sum(w for n, w in trash.items() if n not in own)
            if not outsiders:
                continue                      # the open zone has nothing this subzone lacks
            has_rare = any(cm.creatures.get(n, {}).get("is_boss") for n in own)
            of_roll = (outsiders / sum(trash.values())) * (0.94 if has_rare else 1.0)
            checked += 1
            if abs(of_roll - 0.10) > 0.005:
                bad.append(f"{zone} / {key}: {of_roll:.1%} of encounters come from outside the subzone, not 10%")
    if checked < 100:
        bad.append(f"only {checked} subzones could be checked for the 90/10 split")

    # ...and "hunting it" has to be true for a FETCH quest, which is what this one is
    from world.zone_manager import ZoneManager
    if "Isle Coconut Crab" not in ZoneManager._carriers_of(ZoneManager.__new__(ZoneManager), "sturdy_reef_coral"):
        bad.append("needing coral does not make the game look for the crab that drops it")
    src = open("world/zone_manager.py").read()
    if "ObjectiveType.FETCH" not in src[src.index("def active_kill_targets"):src.index("_carriers = None")]:
        bad.append("active_kill_targets ignores fetch quests")

    # the lure: beasts half again as likely, nothing else touched
    from entities.skinning_drops import SKINNABLE
    from entities.vendor_trash import classify
    beast = lambda name: classify(name)[0] in SKINNABLE
    zone = "Durotar"
    table = cm.get_encounter_table(zone, "open_zone", None)
    w_beast = sum(w for n, w in table.items() if beast(n) and not cm.creatures.get(n, {}).get("is_boss"))
    w_other = sum(w for n, w in table.items() if not beast(n) and not cm.creatures.get(n, {}).get("is_boss"))
    if w_beast and w_other:
        n = 6000
        random.seed(9)
        base = sum(beast(cm.get_random_creature(zone).name) for _ in range(n)) / n
        for pct in (25, 50, 100):
            random.seed(9)
            lit = sum(beast(cm.get_random_creature(zone, beast_lure=pct).name) for _ in range(n)) / n
            k = 1 + pct / 100.0
            want = k * w_beast / (k * w_beast + w_other)
            if abs(lit - want) > 0.03 or lit <= base:
                bad.append(f"+{pct}% lure: beasts went {base:.0%} -> {lit:.0%}, expected about {want:.0%}")

    # Kyle, 12 Nov: "5s for 25% more beasts, 50s for 50% more beasts and 5g for 100% more beasts.
    # Lesser, normal, greater."
    from entities.consumable_manager import get_consumable_manager as _gcm
    for cid, pct, price in (("beast_lure_lesser", 25, 500), ("beast_lure", 50, 5000), ("beast_lure_greater", 100, 50000)):
        c = _gcm().get_consumable(cid)
        if c is None or c.effect_value != pct or c.vendor_price != price:
            bad.append(f"{cid}: should be +{pct}% for {price}c, is "
                       f"{getattr(c, 'effect_value', None)}% for {getattr(c, 'vendor_price', None)}c")
        if not os.path.isfile(f"assets/icons/consumables/{cid}.png"):
            bad.append(f"{cid} has no icon")

    from entities.character import Character
    from entities.consumable_manager import get_consumable_manager
    hero = Character("Hero", "Hunter", 20)
    lure = get_consumable_manager().get_consumable("beast_lure")
    if lure is None:
        bad.append("there is no Beast Lure")
    else:
        lure.use(hero)
        if hero.beast_lure_seconds != 1800 or hero.beast_lure_pct != 50:
            bad.append(f"lighting a lure leaves {hero.beast_lure_seconds}s of it")
        hero.update_buff_timers(1700)
        if not 0 < hero.beast_lure_seconds <= 100:
            bad.append("the lure does not burn down")
        again = Character.from_dict(hero.to_dict())
        if not again.beast_lure_seconds or again.beast_lure_pct != 50:
            bad.append("the lure is lost on save and load")
        hero.update_buff_timers(200)
        if hero.beast_lure_seconds or hero.beast_lure_pct:
            bad.append("the lure never goes out")
    vendors = json.load(open("data/npcs/vendors.json"))
    vendors = vendors.get("vendors", vendors)
    vendors = vendors if isinstance(vendors, list) else list(vendors.values())
    if not any("beast_lure" in (v.get("sells") or []) for v in vendors):
        bad.append("nobody sells a Beast Lure")
    if not os.path.isfile("assets/icons/consumables/beast_lure.png"):
        bad.append("the Beast Lure has no icon")

    print(f"coconut crabs: {plain:.0%} of Tidal Flats encounters, {hunting:.0%} on the quest; coral {FLOOR:.0%}; "
          f"{checked} subzones hold the 90/10 split")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nhunting OK - multi-item quest drops are 75%, subzones are 90% their own, the crabs turn up, and a lure brings beasts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
