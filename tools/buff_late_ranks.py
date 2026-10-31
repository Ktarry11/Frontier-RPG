#!/usr/bin/env python3
"""Raise the late ranks of the classes the balance sim says fall behind.

    PYTHONPATH=. python3 tools/buff_late_ranks.py --factor 1.25 --dry-run
    PYTHONPATH=. python3 tools/buff_late_ranks.py --factor 1.25

Kyle: "Can we fix up these 5 classes slightly by buffing them a bit so they are a bit more in
line?"

WHY ONLY THE LATE RANKS. The five are not weak classes - they are weak LATE classes. Against the
median turns-to-kill they sit at roughly 1.0 up to level 30 (Runemaster is actually AHEAD at 10,
0.78) and then fall off a cliff: Runemaster 2.55, 2.58, 2.69 at 40, 50 and 60. A flat buff would
make them too strong at the levels where they are already fine and still short where they are
not, so this touches ranks at level_req >= MIN_LEVEL only.

WHAT THIS IS NOT. It is not a diagnosis. Five structural explanations were tested against the
data and every one came back negative:

  - missing final ranks (the first guess, and Kyle's): every class tops out at 54-58, and the
    five are indistinguishable from the leaders
  - peak ability damage: Starcaller's best hits for 378 against Warlock's 335, and Starcaller
    lags while Warlock leads
  - rank-over-rank growth past 36: the five have some of the BEST in the game - Tinker 1.265 is
    the highest - while Warlock leads on 1.141
  - cooldown pressure on damage abilities: medians interleave, 1.5 to 4.0 in both groups
  - damage value available from talents: correlates loosely and then Cultist leads the game on
    the lowest total in it

So the gap is emergent from how the rotation actually plays, not from a number sitting in a
file, and this is empirical compensation measured against sim_class_balance rather than a fix
for a known cause. That distinction belongs in the commit and in this docstring, because a
future reader finding a 1.25 here deserves to know nobody ever found the reason.
"""
import argparse
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

#: The five sim_class_balance reports as "far behind", and their ability files.
CLASSES = ["runemaster", "knight_of_xoroth", "starcaller", "paladin", "tinker"]

#: Ranks below this are left alone - that is where these classes are already on the median.
MIN_LEVEL = 36

#: Only damage. Buffing their healing or buffs would change what the classes ARE, and the sim
#: measures turns-to-kill, so a healing change would not even show up in what we are correcting.
DAMAGE_TYPES = ("damage", "spell_damage", "dot", "spell_dot")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factor", type=float, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for cls in CLASSES:
        path = ROOT / "data/abilities" / f"{cls}.json"
        if not path.exists():
            print(f"  !! no ability file for {cls}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
        block = data.get("abilities", data)
        abilities = block if isinstance(block, list) else list(block.values())
        touched = ranks = 0
        for a in abilities:
            if not isinstance(a, dict) or a.get("effect_type") not in DAMAGE_TYPES:
                continue
            hit = False
            for r in (a.get("ranks") or []):
                if (r.get("level_req") or 0) < MIN_LEVEL:
                    continue
                ev = r.get("effect_value")
                if not isinstance(ev, (int, float)) or ev <= 0:
                    continue
                r["effect_value"] = int(round(ev * args.factor))
                ranks += 1
                hit = True
            touched += hit
        if not args.dry_run:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"  {cls:18s} {touched:3d} abilities, {ranks:4d} ranks at level {MIN_LEVEL}+ "
              f"x{args.factor}")
    print(f"\n{'would apply' if args.dry_run else 'applied'} x{args.factor} to "
          f"{len(CLASSES)} classes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
