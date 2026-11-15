#!/usr/bin/env python3
"""Bring the damage and healing abilities authored far above their line back to the strong end of it.

    PYTHONPATH=. python3 tools/fix_strong_outliers.py            # show
    PYTHONPATH=. python3 tools/fix_strong_outliers.py --apply

The other half of tools/fix_weak_over_time.py (class pass, 15 Nov 2026). tools/audit_ability_lines.py found ~22
abilities at 2.2-4.8x of what an ability of their level, cooldown, AoE share, cast speed and builder/spender role
should be. Most are CoA AoEs hitting EACH target harder than a single-target nuke (Starcall, Obliteration Beam,
Umbral Blade, Forked Lightning, Facemelter) - in WoW an AoE hits each target for about half a nuke, and with
dungeon packs of 4-5 (14 Nov) an AoE at 2x per target flattens every pack - plus a no-cooldown builder at 2.9x
(Seismic Crash) and a few party heals. Each over CEILING is scaled to TARGET, every rank alike (rank steps kept); the
spec auras rebalance the spec's total.
"""
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
CEILING, TARGET = 2.2, 1.6
EXEMPT = {"hunter_revive_pet"}     # a pet resurrection, not a combat heal
DAMAGE = {"damage", "spell_damage", "ranged_damage", "damage_and_heal", "damage_and_restore_mana"}
OVER_TIME = {"dot", "spell_dot", "hot"}
BUILT = {"combo", "static", "life_force", "deathfire", "souls", "insanity", "felfury", "focus", "archery_points",
         "vitality", "rage"}


def ratio(e):
    from combat import ability_scaling as S
    from combat.abilities import cast_speed_value
    t = e.get("effect_type")
    heal = t in ("heal", "hot")
    base = 54 if heal else 44
    w = S.cooldown_weight(e.get("cooldown") or 0) * S.area_share(e.get("target_type"), e.get("max_targets"),
                                                                e.get("heal_scope"))
    w *= cast_speed_value(e.get("cast_speed"))
    if t in OVER_TIME:
        w *= 1.5
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
            if not isinstance(e, dict) or not e.get("ranks") or e.get("ability_id") in EXEMPT:
                continue
            t = e.get("effect_type")
            if t not in DAMAGE | OVER_TIME | {"heal"} or (e.get("cooldown") or 0) >= 10 or e["ability_id"].endswith("_attack"):
                continue
            r = ratio(e)
            if r is None or r <= CEILING:
                continue
            factor = TARGET / r
            before = [(x["level_req"], x.get("effect_value")) for x in e["ranks"]][-1]
            for x in e["ranks"]:
                if x.get("effect_value"):
                    x["effect_value"] = max(1, round(x["effect_value"] * factor))
            e.setdefault("_tuning", []).append(
                f"15 Nov 2026, class pass: every rank x{factor:.2f} - it sat at {r:.2f}x of what an ability of its "
                f"level, cooldown, AoE share, cast speed and role should be (tools/fix_strong_outliers.py)")
            after = [(x["level_req"], x.get("effect_value")) for x in e["ranks"]][-1]
            print(f"  {e['ability_id']:40} {r:4.2f}x -> x{factor:4.2f}   top {before} -> {after}")
            n += 1
            changed = True
        if apply and changed:
            f.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{n} abilities {'brought down' if apply else 'would come down'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
