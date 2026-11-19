#!/usr/bin/env python3
"""The first ten levels are gentler: every creature under level 10 deals 20% less damage and has 15% less health.

    PYTHONPATH=. python3 tools/qa_low_level_difficulty.py

Kyle, 16 Nov 2026: "We should also tone down the difficulty before lvl 10 by about 20% overall. Any enemies below
lvl 10 should deal 20% less damage and have 15% less HP." It's the "low_level" row of
data/balance/monster_difficulty.json, multiplied onto whichever row the creature already falls under
(world/difficulty.factor). This spawns real creatures through the creature manager, the way the game does, and
checks the numbers on both sides of the line.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    from world import difficulty as D
    from world.creature_manager import CreatureManager
    from entities.monster import Monster
    bad = []
    low = D.table().get("low_level") or {}
    if (low.get("below_level"), low.get("damage"), low.get("health")) != (10, 0.8, 0.85):
        bad.append(f"the low_level row is {low}, not below 10 at 0.8 damage and 0.85 health")

    with contextlib.redirect_stdout(io.StringIO()):
        cm = CreatureManager()
    checked = 0
    for name, lvl in (("Mottled Boar", None), ("Scorpid Worker", None), ("Dustwind Jackal", None)):
        d = cm.creatures.get(name)
        if not d:
            bad.append(f"{name} isn't in the bestiary any more; pick another Valley creature")
            continue
        for level in (5, 9, 10, 12):
            with contextlib.redirect_stdout(io.StringIO()):
                m = cm.spawn_creature(name, level=level)
            if m is None:
                continue
            raw = Monster(m.name, m.monster_type, level, kit=m.kit_id)
            row = D.table().get(D.kind_of(m)) or {}
            want_h, want_d = float(row.get("health", 1.0)), float(row.get("damage", 1.0))
            if level < 10:
                want_h, want_d = want_h * 0.85, want_d * 0.8
            got_h = m.max_health / raw.max_health
            if abs(got_h - want_h) > 0.02:
                bad.append(f"{name} at {level}: health x{got_h:.2f}, wanted x{want_h:.2f}")
            got_d = m.damage_output_multiplier
            if abs(got_d - want_d) > 1e-6:
                bad.append(f"{name} at {level}: damage x{got_d:.2f}, wanted x{want_d:.2f}")
            checked += 1
    if checked < 8:
        bad.append(f"only {checked} spawns could be checked")

    # EARLY RARES (Kyle, 18 Nov 2026: "Rares below lvl 20 are still a bit overtuned", then "only start to ramp back up
    # past lvl 35"): an open-world rare deals 40% through 35 and its full row from 45; the same creature in a cave is a cave boss and isn't touched.
    early = D.table().get("early_rare") or {}
    if (early.get("damage"), early.get("through_level"), early.get("full_level")) != (0.4, 35, 45):
        bad.append(f"the early_rare row is {early}, not 0.4 through 35 and full from 45")
    rare = "Rumblejaw"
    if rare not in cm.creatures or not cm.creatures[rare].get("is_boss"):
        bad.append(f"{rare} isn't a rare any more; pick another open-world rare under 20")
    else:
        row = float((D.table().get("field_boss") or {}).get("damage", 1.0)) * D.boss_damage(rare)
        for level, want in ((12, 0.4), (30, 0.4), (35, 0.4), (40, 0.7), (45, 1.0), (50, 1.0)):
            with contextlib.redirect_stdout(io.StringIO()):
                m = cm.spawn_creature(rare, level=level)
            got = m.damage_output_multiplier / row
            if abs(got - want) > 0.02:
                bad.append(f"{rare} in the open at {level}: x{got:.2f} of its row, wanted x{want:.2f}")
            m.location_type = "cave"
            if abs(m.damage_output_multiplier / row - 1.0) > 0.02:
                bad.append(f"{rare} in a cave at {level} was softened too")
        checked += 1

    print(f"{checked} creatures spawned at 5, 9, 10 and 12")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - under level 10 a creature deals 20% less and has 15% less health; an open-world rare deals 40% through 35, full from 45")
    return 0


if __name__ == "__main__":
    sys.exit(main())
