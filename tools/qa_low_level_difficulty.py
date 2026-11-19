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

    # OPEN-WORLD RARES ARE THEIR OWN KIND (Kyle, 19 Nov 2026: "split the rares from boss and tune the difficulty",
    # "rares should be around 75-90% win rate"): a named creature in the open is the "rare" row (with its by_level
    # steps), the same creature in a cave is still a field boss, and either way its own boss_damage factor applies.
    # The old early_rare damper is gone: the rare row replaces it.
    if "early_rare" in D.table():
        bad.append("the early_rare row is back; the rare row replaced it")
    rare_row = D.table().get("rare") or {}
    if not rare_row.get("health") or not rare_row.get("damage"):
        bad.append(f"no rare row: {rare_row}")
    rare = "Rumblejaw"
    if rare not in cm.creatures or not cm.creatures[rare].get("is_boss"):
        bad.append(f"{rare} isn't a rare any more; pick another open-world rare under 20")
    else:
        for level in (12, 30, 50, 58):
            with contextlib.redirect_stdout(io.StringIO()):
                m = cm.spawn_creature(rare, level=level)
            m.location_type = "subzone"
            if D.kind_of(m) != "rare":
                bad.append(f"{rare} in the open at {level} is a {D.kind_of(m)}, not a rare")
            want = float(rare_row["damage"]) * D.boss_damage(rare) * D._by_level(rare_row.get("by_level") or [[1, 1, 1]], level, 2)
            if abs(m.damage_output_multiplier - want) > 0.02:
                bad.append(f"{rare} in the open at {level}: damage x{m.damage_output_multiplier:.2f}, wanted x{want:.2f}")
            m.location_type = "cave"
            cave = float((D.table().get("field_boss") or {}).get("damage", 1.0)) * D.boss_damage(rare)
            if D.kind_of(m) != "field_boss" or abs(m.damage_output_multiplier - cave) > 0.02:
                bad.append(f"{rare} in a cave at {level}: {D.kind_of(m)} x{m.damage_output_multiplier:.2f}, wanted a field boss x{cave:.2f}")
        checked += 1

    print(f"{checked} creatures spawned at 5, 9, 10 and 12")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - under level 10 a creature deals 20% less and has 15% less health; an open-world rare is its own row, a cave one a field boss")
    return 0


if __name__ == "__main__":
    sys.exit(main())
