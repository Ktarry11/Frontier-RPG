#!/usr/bin/env python3
"""A rate-scaled buff delivers its rate, through BOTH readers of stat_mods.

    PYTHONPATH=. python3 tools/qa_scaling_stat_mods.py [--list]

=============================================================================
WHAT THIS GUARDS
=============================================================================

Several personal-kit abilities are written as a RATE, not a flat value:

    Dan,      "takes 6% less damage FOR EACH ALLY still alive"
    Owen,     "deals 1% more damage FOR EVERY 2% of health missing"
    Pasang,   "takes 4% less FOR EACH TURN the buff has been up"
    Nicolas,  "1% more dealt and 1% less taken per 3% missing"

StatusEffect.scaling keeps the magnitude per-unit in stat_mods and supplies
the count separately. Two things can go wrong and neither is visible in the
data:

1. THE COUNT IS IGNORED and the per-unit number is delivered flat. Dan
   mitigates 6% instead of 24% - a quarter of his tooltip, in the quiet
   direction. This is exactly what the abandoned regex pass produced, and
   what the conventions doc calls the failure that survives hand-checking.

2. ONLY ONE READER APPLIES IT. A status effect's stat_mods have two
   consumers - StatusEffectMixin.get_status_stat_mod and the derived-stat
   pool loop in Character._recalculate_derived_stats - and they have ALREADY
   drifted once over `stacks`: the pool did not multiply by it while
   get_status_stat_mod always did, so every stacking buff whose payload was
   a plain stat was silently capped at one stack. Both now route through
   _status_mods_for, and this checks that they agree.

So each claim below is measured at two different counts, and a key that
lands in the derived pool (armor) is checked through the recalc as well as
through the direct read.

CAP IS A CAP ON THE MULTIPLIER, not on the final percentage. Pasang's "up to
24%" at -4 per turn is cap 6. Authoring cap 24 there would give -96%, which
is a damage immunity - the same class of bug the conventions doc records as
"two permanent damage immunities" in one session.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
KITS = ROOT / "data" / "npcs" / "personal_kits.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    from combat.status_effects import StatusEffect, EffectType
    from entities.character import Character

    findings, measured = [], []

    # ---- 1. the primitive itself, at two counts per source ----------------
    def fresh():
        return Character("Probe", "Warrior", 60)

    # living_allies
    c = fresh()
    e = StatusEffect("s", "S", EffectType.BUFF, 4,
                     stat_mods={"physical_damage_taken_pct": -6},
                     scaling={"source": "living_allies", "cap": 4},
                     source_name="S")
    mates = [Character(f"M{i}", "Priest", 60) for i in range(3)]
    e.scaling_party = [c] + mates
    c.apply_status_effect(e)
    got4 = c.get_status_stat_mod("physical_damage_taken_pct")
    mates[0].current_health = 0
    mates[1].current_health = 0
    got2 = c.get_status_stat_mod("physical_damage_taken_pct")
    measured.append(("living_allies", "4 alive", got4, -24))
    measured.append(("living_allies", "2 alive", got2, -12))
    if abs(got4 - -24) > 0.01:
        findings.append(f"living_allies with 4 alive gave {got4}, want -24")
    if abs(got2 - -12) > 0.01:
        findings.append(f"living_allies with 2 alive gave {got2}, want -12")

    # missing_health_pct, with a divisor
    c = fresh()
    c.apply_status_effect(StatusEffect(
        "s2", "S2", EffectType.BUFF, 4, stat_mods={"damage_dealt_pct": 1},
        scaling={"source": "missing_health_pct", "divisor": 2, "cap": 50},
        source_name="S"))
    c.current_health = c.health
    full = c.get_status_stat_mod("damage_dealt_pct")
    c.current_health = max(1, int(c.health * 0.5))
    half = c.get_status_stat_mod("damage_dealt_pct")
    measured.append(("missing_health_pct", "full health", full, 0))
    measured.append(("missing_health_pct", "at 50%", half, 25))
    if abs(full) > 0.01:
        findings.append(f"missing_health_pct at full health gave {full}, want 0")
    if abs(half - 25) > 1.0:
        findings.append(f"missing_health_pct at 50% gave {half}, want ~25")

    # the cap must bind
    c.current_health = 1
    capped = c.get_status_stat_mod("damage_dealt_pct")
    measured.append(("missing_health_pct", "at 1 hp (capped)", capped, 50))
    if capped > 50.01:
        findings.append(f"cap did not bind: {capped} exceeds 50")

    # turns_active
    c = fresh()
    e3 = StatusEffect("s3", "S3", EffectType.BUFF, 6,
                      stat_mods={"physical_damage_taken_pct": -4},
                      scaling={"source": "turns_active", "cap": 6},
                      source_name="S")
    c.apply_status_effect(e3)
    t0 = c.get_status_stat_mod("physical_damage_taken_pct")
    e3.duration = 0
    t6 = c.get_status_stat_mod("physical_damage_taken_pct")
    measured.append(("turns_active", "0 turns", t0, 0))
    measured.append(("turns_active", "6 turns", t6, -24))
    if abs(t0) > 0.01:
        findings.append(f"turns_active at 0 elapsed gave {t0}, want 0")
    if abs(t6 - -24) > 0.01:
        findings.append(f"turns_active at 6 elapsed gave {t6}, want -24")

    # ---- 2. an UNSCALED effect must be completely unaffected --------------
    c = fresh()
    c.apply_status_effect(StatusEffect("p", "Plain", EffectType.BUFF, 4,
                                       stat_mods={"armor": 100},
                                       source_name="S"))
    plain = c.get_status_stat_mod("armor")
    measured.append(("(unscaled)", "+100 armor", plain, 100))
    if plain != 100:
        findings.append(f"an unscaled effect changed: +100 armor read as {plain}")

    # ---- 3. BOTH readers must agree - the drift this replaces -------------
    c = fresh()
    base = c.armor
    e4 = StatusEffect("a", "Scaled Armor", EffectType.BUFF, 4,
                      stat_mods={"armor": 50},
                      scaling={"source": "turns_active", "cap": 4},
                      source_name="S")
    c.apply_status_effect(e4)
    e4.duration = 1  # 3 turns elapsed of 4
    c._recalculate_derived_stats()
    direct = c.get_status_stat_mod("armor")
    pooled = c.armor - base
    measured.append(("both readers", "armor via get_status_stat_mod", direct, 150))
    measured.append(("both readers", "armor via derived pool", pooled, 150))
    if abs(direct - pooled) > 0.01:
        findings.append(f"the two readers disagree: direct read {direct} vs "
                        f"derived pool {pooled} - they must apply scaling "
                        f"identically")

    # ---- 4. every authored scaling spec in the data is well formed --------
    doc = json.loads(KITS.read_text(encoding="utf-8"))
    authored = 0
    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            spec = a.get("scaling")
            if not spec:
                continue
            authored += 1
            who = f"{kit.get('name')} / {a.get('name')}"
            src = spec.get("source")
            if src not in StatusEffect.SCALING_SOURCES:
                findings.append(f"{who}: scaling source {src!r} is not one of "
                                f"{StatusEffect.SCALING_SOURCES}")
            if not a.get("stat_mods"):
                findings.append(f"{who}: has scaling but no stat_mods to scale")
            for k, v in (a.get("stat_mods") or {}).items():
                if isinstance(v, (int, float)) and abs(v) > 25:
                    findings.append(
                        f"{who}: {k}={v} looks like a TOTAL, not a per-unit "
                        f"rate - a scaled stat_mod is authored per unit")
            cap = spec.get("cap")
            if cap is not None and cap > 100:
                findings.append(f"{who}: cap {cap} caps the MULTIPLIER, not a "
                                f"percentage - this is almost certainly wrong")

    print(f"  {len(measured)} measurement(s) across "
          f"{len(StatusEffect.SCALING_SOURCES)} scaling sources")
    print(f"  {authored} ability/abilities in the data author a scaling spec\n")

    if args.list:
        print(f"  {'source':22}{'condition':28}{'got':>10}{'want':>8}")
        for src, cond, got, want in measured:
            print(f"  {src:22}{cond:28}{got:>10.1f}{want:>8}")
        print()

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for f in findings:
            print(f"    {f}")
        print("\nFAIL")
        return 1

    print("  rate-scaled buffs deliver their rate, both readers agree, and "
          "unscaled\n  effects are untouched")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
