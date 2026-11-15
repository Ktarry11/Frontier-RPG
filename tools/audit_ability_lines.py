#!/usr/bin/env python3
"""Every damage and healing ability's authored value against the main-spell line, adjusted for what it is.

    PYTHONPATH=. python3 tools/audit_ability_lines.py [--verbose] [--class Rogue]

The class pass (15 Nov 2026) found kit values authored far off the line - Magma Fissure at 6x a Fireball rank per
target on an AoE, Zap tripling in 14 levels, Illumination at 3x a spammable heal - which the rank curve then
multiplied. The line is the authored main nuke (44 at level 1, +3.636% of that a level) or main heal (54 at 1).

An ability's EXPECTED size relative to the line:
  x the cooldown weight and AoE share the coefficients use (combat/ability_scaling.cooldown_weight / area_share)
  x its cast speed (a slow 1.5-turn spell is 1.5x, a quick 0.6-turn one 0.65x)
  x 1.5 for a DoT or HoT (its value is the total over its duration; Classic runs ~1.3-1.6x a nuke)
  BUILDERS AND SPENDERS (Kyle, 15 Nov: "a lot of coa classes are builder and spenders ... think like combo points and
  rage"): a spender (pays a built resource - combo, static, life force, deathfire... - or a secondary_cost) may run to
  2.5x; a builder (generates one) is expected near 0.8x.
  Emergency buttons (cooldown 10+: Lay on Hands, battle rezzes, pet revives) are not judged.
Reports abilities above 2.2x or below 0.4x of what they should be.
"""
import argparse
import glob
import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
DAMAGE = {"damage", "spell_damage", "ranged_damage", "damage_and_heal", "damage_and_restore_mana"}
HEAL = {"heal"}
OVER_TIME = {"dot", "spell_dot", "hot"}
BUILT = {"combo", "static", "life_force", "deathfire", "souls", "insanity", "felfury", "focus", "archery_points",
         "vitality", "rage"}
SKIP = {"_universal.json", "asher_unique.json"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--class", dest="only")
    args = ap.parse_args()
    from combat import ability_scaling as S
    from combat.abilities import cast_speed_value
    rows = []
    for f in sorted(glob.glob("data/abilities/*.json")):
        if os.path.basename(f) in SKIP:
            continue
        cls = os.path.basename(f)[:-5]
        if args.only and cls != args.only.lower().replace(" ", "_"):
            continue
        d = json.load(open(f, encoding="utf-8"))
        L = d if isinstance(d, list) else d.get("abilities", d)
        for e in (L.values() if isinstance(L, dict) else L):
            if not isinstance(e, dict) or not e.get("ranks") or e["ability_id"].endswith("_attack"):
                continue
            t = e.get("effect_type")
            if t not in DAMAGE | HEAL | OVER_TIME:
                continue
            if (e.get("cooldown") or 0) >= 10:
                continue
            heal = t in HEAL or t == "hot"
            base = 54 if heal else 44
            w = S.cooldown_weight(e.get("cooldown") or 0) * S.area_share(e.get("target_type"), e.get("max_targets"),
                                                                        e.get("heal_scope"))
            w *= cast_speed_value(e.get("cast_speed"))
            if t in OVER_TIME:
                w *= 1.5           # a DoT or HoT total: Classic runs ~1.3-1.6x a nuke (Corruption vs Shadow Bolt)
            res = (e.get("resource_type") or "").lower()
            role = "spender" if (e.get("secondary_cost") or res in BUILT and any((r.get("cost") or 0) > 0 for r in e["ranks"])
                                 and not e.get("generates")) else ("builder" if e.get("generates") else "")
            if role == "spender":
                w *= 2.0
            elif role == "builder":
                w *= 0.8
            ratios = []
            for r in e["ranks"]:
                v = r.get("effect_value") or 0
                if v:
                    ratios.append(v / (base * (1 + 0.03636 * (r["level_req"] - 1))) / w)
            if not ratios:
                continue
            rows.append((statistics.median(ratios), cls, e["ability_id"], t, e.get("cooldown") or 0,
                         e.get("cast_speed") or "", role, [(r["level_req"], r.get("effect_value")) for r in e["ranks"]][-2:]))
    hi = sorted([r for r in rows if r[0] > 2.2], reverse=True)
    lo = sorted([r for r in rows if r[0] < 0.4])
    print(f"{len(rows)} damage and healing abilities judged; median {statistics.median(r[0] for r in rows):.2f}x of "
          f"expected")
    print(f"\n{len(hi)} ABOVE 2.2x of what they should be:")
    for r in hi[: (None if args.verbose else 40)]:
        print(f"  {r[0]:5.2f}  {r[2]:<40} {r[3]:<14} cd{r[4]} {r[5]:<5} {r[6]:<8} {r[7]}")
    print(f"\n{len(lo)} BELOW 0.4x:")
    for r in lo[: (None if args.verbose else 25)]:
        print(f"  {r[0]:5.2f}  {r[2]:<40} {r[3]:<14} cd{r[4]} {r[5]:<5} {r[6]:<8} {r[7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
