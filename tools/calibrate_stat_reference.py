#!/usr/bin/env python3
"""Write data/balance/stat_reference.json: what a geared character of each level HAS, per stat, so buffs and debuffs
can be sized as a share of it (combat/support_formula.py).

    PYTHONPATH=. python3 tools/calibrate_stat_reference.py [--step 10]

Kyle, 16 Nov 2026: "get into the support skills and them not actually benefiting from ranking up and being obsolete",
"Make sure support skills and buffs are actually properly done with proper skill levels too". Measured: Power Word:
Fortitude's top rank gave +3 Stamina, about 70 health on a level-60 tank with 4,400 (1.6%), the same at 60 as at 47;
165 of the 228 buffs and debuffs with flat stats had one rank and never grew at all.

Per level (1, then every STEP, then 60): every damage, tank and healer spec is built and geared at that level
(tools/sim_matrix.build), and for each stat the reference is the 75th percentile across them: the value a character
who USES that stat has (a Warrior's Intellect would drag a median down to nothing). Effective values, gear and talents
in, on the scale buffs are written in (spell and healing power on the old power scale: entities/power_scale.py lifts
a buff's value onto the item scale when it folds in). Then a smooth fit through each stat's ratio to the world curve,
as the healing reference does, so the table never dips.

And the monsters: the median trash creature of the level's armour and attack power, for debuffs that take them down.
"""
import argparse
import contextlib
import io
import json
import os
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

OUT = ROOT / "data/balance/stat_reference.json"
#: stat key -> how to read it off a built character
CHAR_KEYS = {
    "stamina": "effective_stamina", "strength": "effective_strength", "agility": "effective_agility",
    "intellect": "effective_intellect", "spirit": "effective_spirit", "attack_power": "attack_power",
    "spell_power": "spell_power", "healing_power": "healing_power", "armor": "armor", "mp5": "mp5",
}
#: written on the old power scale in a buff, so the reference is divided back down
LIFTED = {"spell_power", "healing_power"}


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def p75(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(0.75 * (len(xs) - 1))))] if xs else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=10)
    args = ap.parse_args()
    import sim_matrix as M
    from tools.calibrate_heal_reference import fit
    from entities import power_scale as PS
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        gen = LootGenerator()
        cm = CreatureManager()
    levels = sorted({1, 60, *range(args.step, 60, args.step)})
    specs = M.specs_for(["dps", "tank", "healer"])
    measured = {k: {} for k in CHAR_KEYS}
    monster = {"monster_armor": {}, "monster_attack_power": {}}
    for L in levels:
        vals = {k: [] for k in CHAR_KEYS}
        for spec, role in specs:
            random.seed(hash((spec, L)) & 0xFFFF)
            try:
                c = M.build(spec, role, L, "geared", gen)
            except Exception:                                   # noqa: BLE001
                continue
            for k, attr in CHAR_KEYS.items():
                v = float(getattr(c, attr, 0) or 0)
                if k in LIFTED:
                    v /= PS.LIFT[k]
                vals[k].append(v)
        for k in CHAR_KEYS:
            measured[k][L] = round(p75(vals[k]), 1)
        arm, ap_ = [], []
        for name in sorted(M.pool(cm, L))[:8]:
            with quiet():
                try:
                    m = cm.spawn_creature(name, level=L)
                except Exception:                               # noqa: BLE001
                    continue
            if m is None:
                continue
            arm.append(float(getattr(m, "armor", 0) or 0))
            ap_.append(float(getattr(m, "attack_power", 0) or 0))
        monster["monster_armor"][L] = round(statistics.median(arm), 1) if arm else 0.0
        monster["monster_attack_power"][L] = round(statistics.median(ap_), 1) if ap_ else 0.0
        print(f"  level {L:2d}: " + "  ".join(f"{k} {measured[k][L]:.0f}" for k in CHAR_KEYS)
              + f"  | monster armour {monster['monster_armor'][L]:.0f} AP {monster['monster_attack_power'][L]:.0f}",
              flush=True)
    table = {}
    for k, pts in {**measured, **monster}.items():
        good = {L: v for L, v in pts.items() if v > 0}
        if len(good) >= 2:
            table[k] = {str(L): v for L, v in fit(good).items()}
    data = {"_about": "What a geared character has at each level, per stat (the 75th percentile across every spec: "
                      "what one who uses the stat has), and the median trash monster's armour and attack power. "
                      "Written by tools/calibrate_stat_reference.py; read by combat/support_formula.py.",
            "measured": {k: {str(L): v for L, v in pts.items()} for k, pts in {**measured, **monster}.items()},
            "reference": table}
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
