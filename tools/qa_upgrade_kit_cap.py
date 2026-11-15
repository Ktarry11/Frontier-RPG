#!/usr/bin/env python3
"""No upgrade kit makes a legendary.

    PYTHONPATH=. python3 tools/qa_upgrade_kit_cap.py

Kyle, 15 Nov 2026: "A kit can't upgrade past epic! Hard no." A crafted epic's first kit used to lift it to
legendary (world/upgrade_manager._next_rarity had no ceiling). This kits every crafted epic that has a kit, twice,
and checks it stays epic and still gets its stat bumps; checks a rare still goes to epic and an uncommon to rare;
and that a save holding a kit-made legendary loads back as epic.
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


def main():
    from entities.character import Character
    from entities.item import Item
    from world import crafted_items
    from world.gathering_manager import get_gathering_node_manager
    from world.recipe_manager import _load_all_recipes
    from world.upgrade_manager import get_kit_for_item, upgrade_item, next_rarity_for
    gm = get_gathering_node_manager()
    with contextlib.redirect_stdout(io.StringIO()):
        hero = Character("Tester", "Warrior", 60)
    bad, seen = [], {"epic": 0, "rare": 0, "uncommon": 0}
    step = {"uncommon": "rare", "rare": "epic", "epic": "epic"}
    for rid, (_prof, r) in _load_all_recipes().items():
        if not crafted_items.is_gear(r):
            continue
        item = crafted_items.build(r)
        start = item.rarity
        kit = get_kit_for_item(item)
        if start not in seen or kit is None:
            continue
        if next_rarity_for(start) != step[start]:
            bad.append(f"{rid}: the kit button would say {start} -> {next_rarity_for(start)}")
        stat0 = sum({**item.primary_stats, **item.secondary_stats}.values())
        for n in (1, 2):
            hero.add_material(gm.make_material_instance(kit))
            if upgrade_item(hero, item, kit) is None:
                bad.append(f"{rid}: kit {n} refused")
                break
        if item.rarity != step[start]:
            bad.append(f"{rid} ({item.name}): {start} kitted twice became {item.rarity}")
        if sum({**item.primary_stats, **item.secondary_stats}.values()) <= stat0:
            bad.append(f"{rid}: two kits gave no stats")
        seen[start] += 1
    saved = crafted_items.build(next(r for _p, r in _load_all_recipes().values()
                                     if crafted_items.is_gear(r))).to_dict()
    saved.update(rarity="legendary", is_crafted=True, upgrade_count=1)
    if Item.from_dict(saved).rarity != "epic":
        bad.append("a save's kit-made legendary didn't load back as epic")
    if not seen["epic"]:
        bad.append("no crafted epic with a kit was tested")
    print(f"kitted twice: {seen}")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad[:40]:
            print("  - " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
