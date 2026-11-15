#!/usr/bin/env python3
"""Engineering works: every recipe is learnable, every consumable it makes does something, and the trade reaches 60.

    PYTHONPATH=. python3 tools/qa_engineering.py

Kyle, 15 Nov 2026: "I think you should just full on fix and audit engineering". The audit found:
  - 24 of its 27 consumables did nothing. Consumable.use had no branch for "explosive" or "gadget" (every bomb and
    every gadget returned False), and its six shots granted no stats while the bow's arrows grant attack power;
  - its bombs and shot stopped at level 29 / skill 150;
  - Tideglass Seal (a Brine Flask ingredient) had no source and no skill-up range: nobody could learn it.
This holds every one of those down.
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
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)

bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)


def main():
    R = json.loads((ROOT / "data/crafting/recipes.json").read_text(encoding="utf-8"))["professions"]["engineering"]["recipes"]
    ct = json.loads((ROOT / "data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    made = {}
    for rid, r in R.items():
        check(r.get("source") in ("trainer", "vendor", "drop", "quest"), f"{rid}: no recipe source ({r.get('source')!r})")
        check(isinstance(r.get("skill_range"), list) and len(r["skill_range"]) == 4, f"{rid}: no skill-up range")
        o = r.get("output") or {}
        if o.get("kind") == "consumable":
            made[o["consumable_id"]] = r

    from entities.consumable_manager import get_consumable_manager
    from world.creature_manager import CreatureManager
    from entities.character import Character
    mgr = get_consumable_manager()
    with contextlib.redirect_stdout(io.StringIO()):
        cm = CreatureManager()
    hero = Character("Tester", "Hunter", 60)
    hero.current_health = hero.health

    by_id = {c["consumable_id"]: c for cat in ct.values() if isinstance(cat, list) for c in cat
             if isinstance(c, dict) and c.get("consumable_id")}
    top = {"explosive": 0, "ammo": 0}
    for cid in made:
        c = mgr.get_consumable(cid)
        check(c is not None, f"{cid}: made by engineering but not defined")
        if c is None:
            continue
        kind = c.consumable_type
        hero.consumable_cooldown = 0
        hero.ammo_buff = hero.gadget_buff = None
        log = []
        if kind == "explosive":
            with contextlib.redirect_stdout(io.StringIO()):
                foes = [cm.spawn_creature("Mottled Boar", level=60) for _ in range(2)]
            for f in foes:
                f.max_health = f.current_health = 10 ** 6
            check(not c.use(hero, [], enemies=[]), f"{cid}: a bomb went off with nothing to throw it at")
            ok = c.use(hero, log, enemies=foes)
            check(ok and all(f.current_health < 10 ** 6 for f in foes), f"{cid}: did not hit every enemy ({log})")
            top["explosive"] = max(top["explosive"], c.required_level)
        elif kind == "ammo":
            ok = c.use(hero, log)
            check(ok and (c.stat_bonuses or {}).get("attack_power", 0) > 0, f"{cid}: ammo grants nothing")
            top["ammo"] = max(top["ammo"], c.required_level)
        elif kind == "gadget":
            ok = c.use(hero, log)
            check(ok, f"{cid}: a gadget that does nothing")
        elif kind == "revive":
            check((c.effect_value or 0) > 0, f"{cid}: a revive that restores nothing")
        else:
            check(False, f"{cid}: engineering made an unexpected kind {kind!r}")
    check(top["explosive"] >= 55, f"engineering's best bomb is for level {top['explosive']}: the trade stops short of 60")
    check(top["ammo"] >= 55, f"engineering's best shot is for level {top['ammo']}: the trade stops short of 60")

    print(f"{len(R)} engineering recipes, {len(made)} consumables, bombs to level {top['explosive']}, shot to "
          f"{top['ammo']}")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
