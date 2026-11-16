#!/usr/bin/env python3
"""Epics drop the way Kyle set out on 16 Nov 2026 (docs/epic_drops_plan.md).

    PYTHONPATH=. python3 tools/qa_epic_drops.py

  * Nothing below level 30, either path.
  * ONE roll a kill: a world kill drops an epic about 1 in 400 times, never more than one, and the epic it drops
    fits the ZONE's level band (Kyle: "not picked by player level! picked by zone level").
  * Only a dungeon's FINAL boss rolls a dungeon epic: about 5% from 40 up, about 2% from 30 to 39. Every other
    boss takes the world roll.
  * Every 40+ final boss has one or two epics of its own; every final boss is a real boss.
  * Every zone from 30 up has a good handful of world epics to pick from, and every world epic is reachable from
    some zone. (Counts only: hidden zones are never named.)
  * Every epic rebuilds into a real epic Item with flavour text, and every epic has an icon no other item uses
    (Kyle: "every unique item in the game can only have ONE icon").
  * The spread across armour, weapons and templates holds, and the procedural roller does not swamp the named
    epics.

This rolls the real dice rather than reading the config, for the same reason tools/qa_tier_floor.py does.
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities import epic_drops as ED  # noqa: E402
from entities.epic_drops import MIN_LEVEL, WORLD_CHANCE, roll_epic  # noqa: E402

WORLD_BOUNDS = (0.0015, 0.0040)          # about 1 in 400
FINAL_40_BOUNDS = (0.035, 0.065)         # "4% or 5%"
FINAL_30_BOUNDS = (0.010, 0.030)         # "a smaller roll", about 2%
MIN_PER_ZONE = 8


class _Dummy:
    def __init__(self, name, level, boss=False):
        self.name, self.level, self.is_boss = name, level, boss


def _rate(enemy, zone, n):
    return sum(1 for _ in range(n) if roll_epic(enemy, 60, zone=zone) is not None) / n


def main():
    random.seed(0)
    fails = []
    data = json.loads((ROOT / "data/loot/epic_drops.json").read_text(encoding="utf-8"))
    world, dungeon, finals = data.get("world", []), data.get("dungeon", []), data.get("final_bosses", {})
    if not world or not dungeon or not finals:
        print("FAIL - data/loot/epic_drops.json is missing a pool")
        return 1
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    bands = json.loads((ROOT / "data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]

    # ---- nothing below the gate, either path
    for level in range(1, MIN_LEVEL):
        for boss in (False, True):
            if any(roll_epic(_Dummy("test subject", level, boss), level, zone=None) for _ in range(3000)):
                fails.append(f"an epic dropped at level {level} (boss={boss})")
                break

    # ---- the world roll: one roll, about 1 in 400, and the epic fits the zone
    zone30 = next(z for z, b in bands.items() if b[0] >= 33 and b[1] <= 37)
    rate = _rate(_Dummy("test subject", 35), zone30, 200000)
    print(f"  world      {rate:.4%} per kill  (1 in {int(1 / rate) if rate else 0})")
    if not WORLD_BOUNDS[0] <= rate <= WORLD_BOUNDS[1]:
        fails.append(f"world epic rate is {rate:.4%}, outside {WORLD_BOUNDS[0]:.2%}-{WORLD_BOUNDS[1]:.2%}")
    lo, hi = bands[zone30]
    for _ in range(4000):
        random.seed(_)
        d = ED.world_pool(lo, hi)
        pick = random.choice(d)
        if not lo - ED.BAND_BELOW <= pick["required_level"] <= hi + ED.BAND_ABOVE:
            fails.append(f"{pick['name']} (level {pick['required_level']}) can drop in a {lo}-{hi} zone")
            break
    # the player's level does not move the pick: a level 60 in that zone draws from the same pool
    random.seed(1)
    names = {roll_epic(_Dummy("x", 35), 60, zone=zone30, rng=random.Random(i)) for i in range(20000)}
    names = {n.name for n in names if n}
    allowed = {d["name"] for d in ED.world_pool(lo, hi)}
    if names - allowed:
        fails.append(f"a level 60 in a {lo}-{hi} zone drew {sorted(names - allowed)[0]}, outside the zone's band")

    # ---- final bosses only; 5% from 40 up, 2% from 30 to 39; any other boss takes the world roll
    for boss, info in sorted(finals.items()):
        if boss not in creatures or not creatures[boss].get("is_boss"):
            fails.append(f"final boss {boss} is not a boss in creatures.json")
            continue
        level = creatures[boss]["level_range"][1]
        r = _rate(_Dummy(boss, level, True), None, 20000)
        bounds = FINAL_40_BOUNDS if info["chance"] >= 0.05 else FINAL_30_BOUNDS
        if not bounds[0] <= r <= bounds[1]:
            fails.append(f"{boss} drops an epic {r:.2%} of the time, outside {bounds[0]:.1%}-{bounds[1]:.1%}")
        own = [d for d in dungeon if d.get("boss") == boss]
        if info["chance"] >= 0.05 and not 1 <= len(own) <= 2:
            fails.append(f"{boss} (40+) has {len(own)} epics of its own, not 1 or 2")
        pool = ED.boss_pool(boss)
        if not pool:
            fails.append(f"{boss} has no epics to drop")
    other = next(n for n, v in creatures.items() if v.get("is_boss") and n not in finals
                 and v["level_range"][1] >= 45)
    r = _rate(_Dummy(other, 50, True), None, 200000)
    print(f"  non-final boss {r:.4%} per kill (the world roll)")
    if not WORLD_BOUNDS[0] <= r <= WORLD_BOUNDS[1]:
        fails.append(f"a boss that is not a final boss drops epics at {r:.2%}, not the world rate")
    for d in dungeon:
        if d.get("boss") != ED.SHARED_30S and d.get("boss") not in finals:
            fails.append(f"{d['name']} belongs to {d.get('boss')}, who is not a final boss")

    # ---- every zone from 30 up has a handful; every world epic is reachable
    thin = 0
    reach = set()
    for z, (zlo, zhi) in bands.items():
        if zhi < MIN_LEVEL:
            continue
        pool = ED.world_pool(max(zlo, MIN_LEVEL), max(zhi, MIN_LEVEL))
        reach |= {d["name"] for d in pool}
        if len(pool) < MIN_PER_ZONE:
            thin += 1
    if thin:
        fails.append(f"{thin} zone(s) from level 30 up have fewer than {MIN_PER_ZONE} world epics to pick from")
    unreachable = sorted({d["name"] for d in world} - reach)
    if unreachable:
        fails.append(f"no zone can drop {', '.join(unreachable[:5])}")

    # ---- every entry rebuilds, is epic, carries flavour and its own icon
    from entities.item import Item
    from tools.build_epic_drops import icon_users
    users = icon_users()
    icons = Counter()
    for bucket, rows in (("world", world), ("dungeon", dungeon)):
        for d in rows:
            try:
                it = Item.from_dict(dict(d))
            except Exception as exc:                       # noqa: BLE001
                fails.append(f"{bucket}/{d.get('name')} will not rebuild: {exc}")
                continue
            if it.rarity != "epic":
                fails.append(f"{bucket}/{it.name} is {it.rarity}, not epic")
            if not getattr(it, "flavor_text", ""):
                fails.append(f"{bucket}/{it.name} has no flavour text")
            icons[d.get("icon_id")] += 1
            if users.get(d.get("icon_id")):
                fails.append(f"{it.name}'s icon is also {sorted(users[d['icon_id']])[0]}'s")
            if not (ROOT / "assets/icons/gear" / f"{d.get('icon_id')}.png").exists():
                fails.append(f"{it.name}'s icon {d.get('icon_id')} is not on disk")
            if d.get("item_level", 0) >= 50 and d.get("slot") == "trinket" and not d.get("proc"):
                fails.append(f"{it.name} is a level 50+ trinket that does nothing")
    for icon, n in icons.items():
        if n > 1:
            fails.append(f"{n} epics share the icon {icon}")
    if data.get("pending"):
        fails.append(f"{len(data['pending'])} epics are still waiting on an icon")

    # ---- Kyle's standing rule on loot spread
    rows = world + dungeon
    armour = Counter(d.get("armor_type") for d in rows if d.get("armor_type") not in (None, "accessory"))
    weapons = Counter(d.get("weapon_type") for d in rows if d.get("weapon_type"))
    for cls in ("cloth", "leather", "mail", "plate"):
        if armour[cls] < len(rows) // 12:
            fails.append(f"only {armour[cls]} {cls} epics - the spread is lopsided")
    if weapons and max(weapons.values()) > max(3, sum(weapons.values()) // 3):
        hog = max(weapons, key=weapons.get)
        fails.append(f"{weapons[hog]} of the epic weapons are {hog}")

    # ---- the procedural roller must not outshine the named ones
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    proc = sum(1 for _ in range(40000) if gen.roll_rarity(38) == "epic") / 40000 * 0.35
    print(f"  procedural epics, same level: {proc:.4%} per kill")
    if proc > WORLD_CHANCE * 4:
        fails.append(f"procedural epics ({proc:.4%}) swamp the named world drops "
                     f"({WORLD_CHANCE:.4%}) - lower rarity.json's epic drop_weight")

    print(f"\n== {len(world)} world epics, {len(dungeon)} dungeon epics, {len(finals)} final bosses; "
          f"armour {dict(armour)}")
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("PASS - one roll a kill, picked by zone level, final bosses only, every epic its own icon")
    return 0


if __name__ == "__main__":
    sys.exit(main())
