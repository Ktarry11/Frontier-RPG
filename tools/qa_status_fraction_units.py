#!/usr/bin/env python3
"""Buffs that raise max health or cut damage taken are written as FRACTIONS, not percent points.

    PYTHONPATH=. python3 tools/qa_status_fraction_units.py

15 Nov 2026, found by the role sim: a Witch Hunter Black Knight's health went 727 -> 4,363 in one fight. Its
talent proc Blade of the Misbegotten ("+5% maximum health per stack, stacking 3 times") carried
max_health_pct 5.0, and a status effect's max_health_pct is read as a fraction - so each stack was +500%.
Guardian Vanguard's Resilient had 8.0 (+800%). Most _pct keys on a status effect are percentage POINTS
(claude/talent_design_palette.md, "THREE unit conventions"); these three are fractions.

  1. No status payload anywhere (abilities, talent procs, kits, consumables, items) has max_health_pct,
     max_mana_pct or damage_taken_pct at 1 or more, except the deliberate full immunity below.
  2. A Black Knight's health after a real fight is within 1.5x of where it started.
"""
import contextlib
import glob
import io
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)

FRACTION = {"max_health_pct", "max_mana_pct", "damage_taken_pct"}
#: -1.0 damage_taken_pct is a full immunity window, on purpose (a 20-turn cooldown, Blessed ally only)
ALLOWED = {("sun_cleric_blessing_of_purity", "damage_taken_pct", -1.0)}


def main():
    bad = []
    hits = []

    def walk(x, ctx):
        if isinstance(x, dict):
            name = x.get("ability_id") or x.get("talent_id") or ctx
            sm = x.get("stat_mods")
            if isinstance(sm, dict):
                for k, v in sm.items():
                    if k in FRACTION and isinstance(v, (int, float)) and abs(v) >= 1 and (name, k, v) not in ALLOWED:
                        hits.append(f"{name}: {k} {v}")
            for k, v in x.items():
                if k != "stat_mods":
                    walk(v, name)
        elif isinstance(x, list):
            for v in x:
                walk(v, ctx)
    files = (glob.glob("data/abilities/*.json") + glob.glob("data/talents/*.json") + glob.glob("data/consumables/*.json")
             + glob.glob("data/items/*.json") + ["data/npcs/personal_kits.json", "data/races/racials.json"])
    for f in sorted(files):
        walk(json.load(open(f, encoding="utf-8")), f)
    print(f"1. fraction keys at 1 or more in status payloads: {len(hits)}")
    bad += hits

    import sim_role_balance as R
    from entities.loot_generator import LootGenerator
    from sim_class_balance import dress
    with contextlib.redirect_stdout(io.StringIO()):
        c, _ = R.build("witch_hunter_black_knight", 40, LootGenerator(), dress, role="tank")
        start = c.health
        R.tank_axes(c, 40, LootGenerator(), dress, 2)
    print(f"2. Black Knight health over a fight: {start} -> {c.health}")
    if c.health > start * 1.5:
        bad.append(f"Black Knight's health grew {start} -> {c.health} in a fight")

    if bad:
        print("\nFAILED:")
        for b in bad:
            print("  -", b)
        return 1
    print("\nstatus fraction units OK - no buff multiplies health or damage taken by mistake.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
