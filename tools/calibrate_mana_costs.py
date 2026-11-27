#!/usr/bin/env python3
"""Set every class's mana costs so its main spell lasts ~20 turns from a full bar.

    PYTHONPATH=. python3 tools/calibrate_mana_costs.py            # print the table it would write
    PYTHONPATH=. python3 tools/calibrate_mana_costs.py --write    # write data/balance/mana_costs.json

Kyle, 15 Nov 2026: "I don't want to see a caster spam their abilities and have 0 chance to run out of mana.
Same with a Healer." ... "more of a TBC Era game where thinking was required". He chose: a geared caster or
healer spamming their main spell runs dry in ~20 turns (about 5-6 normal pulls a bar, and partway through a long
boss); costs normalized per class, keeping each class's own ratios; and TBC's five-second rule for spirit
(Character.CASTING_SPIRIT_REGEN).

MEASURED BEFORE: turns of spam from a full bar ran from 5.5 (Starcaller Warden) to never (Holy Priest,
Discipline, Elemental, Heretic) - classic fillers cheap (Fireball 99 at 60), CoA fillers 2-3x that.

HOW. For each class that spends mana, at levels 10-60, every spec that uses mana is built geared (greens below
20, blues from 20, itemized for the spec - tools/sim_matrix.py) with the cost table OFF, and its main spell found:
  damage specs   the spammable (cooldown 0-1) single-target damage spell the sim rotation leads with
  healer specs   the biggest spammable direct heal (its smaller, cheaper heals then last longer - the choice)
The multiplier that makes that spell last TARGET turns, counting regen at the casting rate, is
    (pool / TARGET + regen while casting) / cost

DAMAGE ROWS USE THE REAL ROTATION (15 Nov 2026, second pass). A Mage's rotation is mostly its main spell, so the
main spell's cost was a fair stand-in; a Hunter's is Aimed, Arcane and Multi-Shot, all dearer than Steady Shot, and
it ran dry in ~10 turns and spent the rest of the fight on Shoot (half the median damage spec). So a damage spec
now runs its own rotation (tools/sim_dps_parity.damage_per_turn, the engine loop with pets) for ROTATION_TURNS with
the bar refilled each turn, and the cost it measures is what that rotation spends per turn on average.
and the class's value at that level is the median across its specs. Damage and heals get separate rows.
Levels in between are interpolated by combat/ability_scaling.mana_cost_multiplier at the rank's level.
"""
import argparse
import contextlib
import io
import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

TARGET = 14
#: Kyle, 27 Nov 2026: mana "should be a meaningful consideration during prolonged encounters". Measured with the
#: combat pass in: geared healers lasted 20-60 casts of their main heal (Moon Priest 58, Heretic 53, Brewing 49),
#: damage specs 9-17 turns of their rotation. Damage now runs dry in ~14 turns of nonstop casting, a main heal in ~12.
#: The table is the whole tightening: combat/mana_economy's HEAL_TIGHTEN and DAMAGE_TIGHTEN are 1.0.
HEAL_DEFAULT_TARGET = 12
#: PER-CLASS HEAL TARGETS (Kyle, 15 Nov 2026): "Healing wave should be more expensive than holy light ... holy
#: pally gets illumination. So they usually last longer anyways. This allows shamans to not cast as much to save
#: mana." Restoration's Healing Wave heals ~2x a Holy Light (its talents stack +39% on it), so it is priced for 16
#: casts from a full bar instead of 20 - 25% dearer as a share of the bar. Its smaller heals move with it.
HEAL_TARGET = {"shaman": 10}
SAMPLES = 4
ROTATION_TURNS = 20
LEVELS = [10, 20, 30, 40, 50, 60]
OUT = ROOT / "data/balance/mana_costs.json"
DAMAGE = {"damage", "spell_damage", "ranged_damage", "damage_and_restore_mana"}
HEALS = {"heal"}


def main_spell(char, role):
    from tools.sim_class_balance import plan
    heals, attacks, _s, _d = plan(char)

    def mana(a):
        return getattr(getattr(a, "resource_type", None), "value", "") == "mana" and (a.cost or 0) > 0

    if role == "healer":
        pool = [a for a in heals if mana(a) and a.effect_type in HEALS and (a.cooldown or 0) <= 1
                and getattr(a, "target_type", None) not in ("party",)]
        return max(pool, key=lambda a: getattr(a, "heal_value", 0) or a.effect_value, default=None)
    pool = [a for a in attacks if mana(a) and a.effect_type in DAMAGE and (a.cooldown or 0) <= 1
            and getattr(a, "target_type", None) != "enemy_aoe"]
    return pool[0] if pool else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--heal-only", action="store_true",
                    help="recompute only the heal rows; the damage rows are kept from the current file")
    args = ap.parse_args()
    from combat import ability_scaling as S
    S.USE_MANA_TABLE = False
    import sim_matrix as M
    import sim_role_balance as R
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    import sim_dps_parity as P
    from world.creature_manager import CreatureManager
    with contextlib.redirect_stdout(io.StringIO()):
        cm = CreatureManager()

    rows = {}
    detail = []
    for spec, role in M.specs_for(["dps", "healer"]):
        kind = "heal" if role == "healer" else "damage"
        if args.heal_only and kind == "damage":
            continue
        slug = spec.rsplit("_", 1)[0]
        # the class slug is the spec minus its last word, except where the spec name has two words
        cls = R.class_of(spec).lower().replace(" ", "_")
        for lv in LEVELS:
            # gear is rolled, so a spec's pool and regen are averaged over SAMPLES builds
            pools, regens, a, cost = [], [], None, 0
            if kind == "damage":
                costs = []
                for i in range(SAMPLES):
                    st = {}
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            P.damage_per_turn(spec, lv, ROTATION_TURNS, gen, cm, fight_seed=i, gear_seed=100 + i,
                                              mana_stats=st)
                    except Exception as e:                          # noqa: BLE001
                        print(f"  {spec} L{lv}: {type(e).__name__}: {e}")
                        break
                    if not st.get("pool") or not st.get("spent_per_turn"):
                        break
                    pools.append(st["pool"])
                    regens.append(st["regen"])
                    costs.append(st["spent_per_turn"])
                if not pools:
                    continue
                cost = statistics.mean(costs)
                a = type("Rotation", (), {"name": "rotation"})()
            else:
                for _ in range(SAMPLES):
                    with contextlib.redirect_stdout(io.StringIO()):
                        c = M.build(spec, role, lv, "geared", gen)
                    if not getattr(c, "mana", 0):
                        break
                    a = main_spell(c, role)
                    if a is None:
                        break
                    cost = a.talented_cost(c)
                    pools.append(c.mana)
                    regens.append(c.mana_per_turn(casting=True))
            if not pools or a is None or cost <= 0:
                continue
            pool, regen = statistics.mean(pools), statistics.mean(regens)
            target = HEAL_TARGET.get(cls, HEAL_DEFAULT_TARGET) if kind == "heal" else TARGET
            f = (pool / target + regen) / cost
            rows.setdefault(cls, {}).setdefault(kind, {}).setdefault(lv, []).append(f)
            detail.append((cls, kind, spec, lv, round(pool), round(regen), a.name, cost, round(f, 2)))
    table = {}
    if args.heal_only and OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8")).get("classes", {})
        for cls, kinds in old.items():
            if "damage" in kinds:
                table.setdefault(cls, {})["damage"] = kinds["damage"]
    for cls, kinds in sorted(rows.items()):
        table.setdefault(cls, {})
        for kind, by_lv in kinds.items():
            table[cls][kind] = [[lv, round(statistics.median(v), 3)] for lv, v in sorted(by_lv.items())]
    print(f"{'class':<18}{'kind':<7}" + "".join(f"{lv:>7}" for lv in LEVELS))
    for cls, kinds in table.items():
        for kind, pts in kinds.items():
            d = dict(pts)
            print(f"{cls:<18}{kind:<7}" + "".join(f"{d.get(lv, ''):>7}" for lv in LEVELS))
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({
            "_about": "Mana cost multiplier per class, by level, for damage spells and heals. Written by "
                      "tools/calibrate_mana_costs.py so each class's main spell lasts ~%d turns from a full bar "
                      "(geared, five-second rule). Read by combat/ability_scaling.mana_cost_multiplier." % TARGET,
            "target_turns": TARGET,
            "heal_target_turns": HEAL_TARGET,
            "classes": table}, indent=1), encoding="utf-8")
        print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
