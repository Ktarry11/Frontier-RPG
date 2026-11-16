#!/usr/bin/env python3
"""Stonetalon is built the way docs/stonetalon_brief.md says, and its loot is for all 30 classes.

    PYTHONPATH=. python3 tools/qa_stonetalon.py

Kyle, 15 Nov 2026: Stonetalon, 26-32, two zones, scarred vs untouched. And, twice the same evening: "don't
neglect people - stop defaulting to classic 9 classes" and "dont forget to not ignore the 21 CoA classes or
stuff thats not traditional 9 classes!" This holds:

  - STONETALON EAST: every part of the map is reachable from the Barrens road; its doors to the Barrens and
    Ashenvale lead somewhere and come back; its subzones and encounter tables agree; rares are in subzones
    only, and every creature has a sprite on disk;
  - THE RARES' LOOT IS FOR EVERY SPEC. Against all 97 specs of the 30 classes in data/items/spec_gear.json:
    every spec can equip at least one rare drop in the zone that's made for its stat template (a hybrid also
    takes its parent's: an agility/intellect spec takes agility gear; a strength/intellect spec takes strength
    or caster gear). Not the classic nine;
  - the loot is spread: strength leather, a mail healer, a caster's shield, a plate healer are all in it;
  - THE ELDEST SEQUOIA (the dungeon): both maps reach every boss, chest and door; you go in at the foot of the
    tree, up the trunk, onto the crown, and the crown's far end drops you back at the foot ONE WAY: nothing
    outside leads to the crown; every boss has a pool of five or more, and every creature placed is written.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

bad = []

#: a spec's stat template -> the item templates it takes
TAKES = {
    "str_physical": {"str_physical"},
    "agi_physical": {"agi_physical"},
    "int_caster": {"int_caster"},
    "spi_healer": {"spi_healer"},
    "agi_int_hybrid": {"agi_int_hybrid", "agi_physical"},
    "str_int_hybrid": {"str_int_hybrid", "str_physical", "int_caster"},
}


def check(ok, msg):
    if not ok:
        bad.append(msg)


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def main():
    import tools.handbuilt_stonetalon_east as SE
    from tools import ashenvale_engine as E
    from world.portal_manager import PortalManager
    import creature_sprites as CS

    # ---- the maps, and the tables
    import tools.handbuilt_stonetalon_west as SW
    pm = PortalManager()
    links = pm._links
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    walk_total = 0
    for name, mod in (("Stonetalon East", SE), ("Stonetalon West", SW)):
        with quiet():
            L = mod.build_layout()
        seen, walk, _ = E.reachable_report(L, mod.START)
        walk_total += walk
        check(seen == walk, f"{name}: {walk - seen} walkable tiles can't be reached")
        here = links.get(name, {})
        for xy, dest in mod.PORTALS.items():
            check(xy in here and here[xy][0] == dest, f"{name} {xy}: the door to {dest} isn't registered")
            back = links.get(dest, {})
            check(any(v[0] == name for v in back.values()), f"{dest} has no door back to {name}")
        for xy, dest in mod.LATER_PORTALS.items():
            check(xy not in here, f"{name} {xy}: a door to {dest}, which isn't built yet")
        t = enc.get(name)
        check(t is not None, f"{name} has no encounter table")
        if not t:
            continue
        check(set(t["subzones"]) == {s_[0] for s_ in mod.SUBZONES}, f"{name}'s subzones and tables differ")
        for c in t["open_zone"]["creatures"]:
            check(not creatures.get(c, {}).get("is_boss"), f"{c}: a rare in the open-zone table")
        for sub in list(t["subzones"].values()) + list(t.get("caves", {}).values()):
            for c in sub["creatures"]:
                check(c in creatures, f"{c}: in a table but not in creatures.json")
                spr = CS.sprite_for(c, creatures.get(c, {}).get("template"))
                check(spr and (ROOT / "assets/creatures" / f"{spr}.png").exists(), f"{c}: no sprite ({spr})")
    walk = walk_total

    # ---- the dungeon
    import tools.handbuilt_eldest_sequoia as ES
    with quiet():
        for key, build in (("trunk", ES.build_trunk_baked), ("crown", ES.build_crown_baked)):
            z, L = build()
            seen = L._reach()
            lost = [c for c in L.critical if c not in seen]
            check(not lost, f"{z.name}: {len(lost)} bosses, chests or doors can't be reached")
    check(links.get("Stonetalon West", {}).get((96, 70), ("",))[0] == ES.TRUNK, "the West has no door into the tree")
    check(links.get(ES.TRUNK, {}).get(ES.T_UP, ("",))[0] == ES.CROWN, "the trunk's top doesn't lead onto the crown")
    check(links.get(ES.CROWN, {}).get(ES.C_IN, ("",))[0] == ES.TRUNK, "the crown has no way back down the trunk")
    check(links.get(ES.CROWN, {}).get(ES.C_OUT, ("",))[0] == "Stonetalon West", "the crown's far end goes nowhere")
    into_crown = [z for z, d in links.items() for v in d.values() if v[0] == ES.CROWN and z != ES.TRUNK]
    check(not into_crown, f"a way into the crown that skips the trunk: {into_crown}")
    pools = json.loads((ROOT / "data/loot/stonetalon_boss_loot.json").read_text(encoding="utf-8"))
    for key in ("trunk", "crown"):
        for boss in ES.BOSSES[key]:
            check(boss in creatures, f"{boss}: not in creatures.json")
            check(len(pools.get(boss, [])) >= 5, f"{boss}: {len(pools.get(boss, []))} drops, not five")
    caves = enc.get("Stonetalon West", {}).get("caves", {})
    for m in (ES.TRUNK, ES.CROWN):
        check(m in caves, f"{m}: no encounter table")
    placed = {mm for f in (ES._trash_trunk, ES._trash_crown) for pk in f() for (_x, _y, mm, _l) in pk}
    for c in placed:
        check(c in creatures, f"{c}: placed in the dungeon but not in creatures.json")
        spr = CS.sprite_for(c, creatures.get(c, {}).get("template"))
        check(spr and (ROOT / "assets/creatures" / f"{spr}.png").exists(), f"{c}: no sprite ({spr})")

    # ---- the rares' loot, against every spec
    from entities.character import Character
    from entities.proficiency import can_equip
    from entities.item import Item
    loot = json.loads((ROOT / "data/loot/stonetalon_rare_loot.json").read_text(encoding="utf-8"))
    loot.update(json.loads((ROOT / "data/loot/stonetalon_boss_loot.json").read_text(encoding="utf-8")))
    items = [Item.from_dict(d) for k, v in loot.items() if not k.startswith("_") for d in v]
    specs = {k: v for k, v in json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8")).items()
             if isinstance(v, dict) and "class" in v}
    with quiet():
        chars = {sp["class"]: Character("QA", sp["class"], 30) for sp in specs.values()}
    check(len(chars) == 30, f"{len(chars)} classes in spec_gear.json, not 30")
    fewest = 99
    for sid, sp in specs.items():
        n = sum(1 for it in items if it.stat_template in TAKES[sp["stat_template"]]
                and can_equip(chars[sp["class"]], it)[0])
        fewest = min(fewest, n)
        check(n >= 1, f"{sid} ({sp['class']}): nothing among Stonetalon's rare and boss drops")
    idents = {k: d.get("identity") for k, v in loot.items() if not k.startswith("_") for d in v}
    by_ident = [(it, d.get("identity")) for it, d in zip(items, [d for k, v in loot.items()
                                                                if not k.startswith("_") for d in v])]
    combos = {(it.weapon_type if it.weapon_type else it.armor_type, it.stat_template) for it in items}
    for need in (("leather", "str_physical"), ("mail", "spi_healer"), ("shield", "int_caster"),
                 ("plate", "spi_healer")):
        check(need in combos, f"no {need[0]} {need[1]} piece among the rares")
    tank_ids = {"tank", "shield_tank", "tank_weapon", "bear", "bear_weapon", "tank_any"}
    for sid, sp in specs.items():
        if sp["role"] == "tank":
            check(any(i in tank_ids and can_equip(chars[sp["class"]], it)[0] for it, i in by_ident),
                  f"{sid} ({sp['class']}): no tank piece among Stonetalon's rare and boss drops")

    print(f"Stonetalon: {walk} walkable tiles over two zones, {len(SE.PORTALS) + len(SW.PORTALS)} doors live, "
          f"{len(SE.LATER_PORTALS) + len(SW.LATER_PORTALS)} waiting; {len(items)} rare and boss drops for "
          f"{len(specs)} specs of {len(chars)} classes (fewest any spec gets: {fewest})")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
