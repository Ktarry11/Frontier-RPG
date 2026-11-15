#!/usr/bin/env python3
"""Lift the DoTs and HoTs authored at a tenth to a third of a normal one up to a meaningful size.

    PYTHONPATH=. python3 tools/fix_weak_over_time.py            # show
    PYTHONPATH=. python3 tools/fix_weak_over_time.py --apply

Found in the class pass (15 Nov 2026, tools/audit_ability_lines.py): ~35 damage- and heal-over-time abilities - most
of them CoA spenders - carry a TOTAL (the engine spreads effect_value across the ticks: abilities.py, the dot branch)
of 0.1-0.4x what a DoT or HoT of their level, cooldown and cast speed should total (Classic: a DoT's total runs
~1.3-1.6x a nuke). They read like CoA's per-tick tooltip numbers entered as totals: Vampiric Touch 48 at level 50,
Venomancer's Expulsion 34 at 54. As buttons they were nearly worthless - the sims, which now value a DoT at its
total, rarely cast them.

Each one under FLOOR of expected is scaled to TARGET of expected, every rank by the same factor (so its rank steps
are kept), capped at MAX_FACTOR. The spec auras rebalance each spec's total afterwards; this is about every button
being worth pressing. Physical strikes are not touched (their weapon damage is added on top of effect_value).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
FLOOR, TARGET, MAX_FACTOR = 0.40, 0.70, 6.0
OVER_TIME = {"dot", "spell_dot", "hot"}
BUILT = {"combo", "static", "life_force", "deathfire", "souls", "insanity", "felfury", "focus", "archery_points",
         "vitality", "rage"}


def expected_ratio(e):
    import statistics
    from combat import ability_scaling as S
    from combat.abilities import cast_speed_value
    heal = e.get("effect_type") == "hot"
    base = 54 if heal else 44
    w = S.cooldown_weight(e.get("cooldown") or 0) * S.area_share(e.get("target_type"), e.get("max_targets"),
                                                                e.get("heal_scope"))
    w *= cast_speed_value(e.get("cast_speed")) * 1.5
    res = (e.get("resource_type") or "").lower()
    if e.get("secondary_cost") or (res in BUILT and any((r.get("cost") or 0) > 0 for r in e["ranks"]) and not e.get("generates")):
        w *= 2.0
    elif e.get("generates"):
        w *= 0.8
    rs = [(r.get("effect_value") or 0) / (base * (1 + 0.03636 * (r["level_req"] - 1))) / w
          for r in e["ranks"] if r.get("effect_value")]
    return statistics.median(rs) if rs else None


def main():
    apply = "--apply" in sys.argv
    n = 0
    for f in sorted((ROOT / "data/abilities").glob("*.json")):
        if f.name in ("_universal.json", "asher_unique.json"):
            continue
        doc = json.loads(f.read_text(encoding="utf-8"))
        L = doc if isinstance(doc, list) else doc.get("abilities", doc)
        changed = False
        for e in (L.values() if isinstance(L, dict) else L):
            if not isinstance(e, dict) or e.get("effect_type") not in OVER_TIME or not e.get("ranks"):
                continue
            if (e.get("cooldown") or 0) >= 10 or e.get("_over_time_lifted"):
                continue
            r = expected_ratio(e)
            if r is None or r >= FLOOR:
                continue
            factor = min(MAX_FACTOR, TARGET / r)
            before = [(x["level_req"], x.get("effect_value")) for x in e["ranks"]][-1]
            for x in e["ranks"]:
                if x.get("effect_value"):
                    x["effect_value"] = max(1, round(x["effect_value"] * factor))
            e["_over_time_lifted"] = round(factor, 2)
            e.setdefault("_tuning", []).append(
                f"15 Nov 2026, class pass: every rank x{factor:.2f} - its total was {r:.2f}x what a "
                f"{e['effect_type']} of its level, cooldown and cast speed should total (a CoA per-tick number entered "
                f"as a total?). tools/fix_weak_over_time.py")
            after = [(x["level_req"], x.get("effect_value")) for x in e["ranks"]][-1]
            print(f"  {e['ability_id']:42} {r:4.2f}x -> x{factor:4.2f}   top {before} -> {after}")
            n += 1
            changed = True
        if apply and changed:
            f.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{n} over-time abilities {'lifted' if apply else 'would be lifted'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
