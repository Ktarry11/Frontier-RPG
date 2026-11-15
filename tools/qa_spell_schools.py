#!/usr/bin/env python3
"""Every damage spell names its school.

    PYTHONPATH=. python3 tools/qa_spell_schools.py

Found in the deep dive (15 Nov 2026, tools/sim_school_exposure.py): 19 spells had no damage_school - the Shadow
Priest's whole kit (Shadow Word: Pain, Mind Flay, Vampiric Touch, Mind Sear), Corruption, Unstable Affliction,
Moonfire, Insect Swarm, Flame Shock, Consecration - so they landed as generic 'magic'. A Shadow Priest measured
0% Shadow damage, and no school talent (Shadow Weaving, Darkness, +Fire damage...) ever touched them.
"""
import glob
import json
import os
import sys

SPELLS = {"spell_damage", "spell_dot", "damage_and_heal", "damage_and_restore_mana"}


def main():
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    bad = []
    for f in sorted(glob.glob("data/abilities/*.json")):
        if os.path.basename(f) in ("_universal.json", "asher_unique.json"):
            continue
        d = json.load(open(f, encoding="utf-8"))
        L = d if isinstance(d, list) else d.get("abilities", d)
        for e in (L.values() if isinstance(L, dict) else L):
            if isinstance(e, dict) and e.get("effect_type") in SPELLS and not e.get("damage_school"):
                bad.append(e["ability_id"])
    if bad:
        print(f"FAIL: {len(bad)} damage spells name no school: {bad}")
        return 1
    print("OK: every damage spell names its school")
    return 0


if __name__ == "__main__":
    sys.exit(main())
