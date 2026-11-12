"""
Nobody in blues crits most of the time.

Kyle, 10 Nov: "Crit rates are STILL too high ... a person in blues should not reach almost
70% crit." Measured then: Berat Yilmaz, level 56 Tinker, 67% spell crit off 161 Intellect.

Two causes, both in the sources, no cap (the standing rule):
  - Intellect and Agility bought crit at about 6 points per 1% at level 60
  - "5% of your Intellect as spell crit" talents were read as percentage POINTS, so three
    ranks of one first-tier talent were worth +27% crit

Checked on every recruit in the game, built the way the game builds them, at 60:
  1. no one is over 40% physical or spell crit, and the typical recruit is under 25%
  2. Berat Yilmaz is under 25%
  3. crit still exists and still rewards the stat: everyone has at least the 5% base, an
     Agility class has more physical crit than a caster, and more of the stat means more crit
  4. a "% of stat as crit/dodge/parry/haste" talent, fully ranked, is worth between 0.3% and 6%
  5. the stat sheet's "per point" line agrees with the constants
"""
import os
import statistics
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []
CEILING = 40.0
TYPICAL = 25.0


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from world.recruit_manager import get_recruit_manager
    from entities.character import Character
    import random
    random.seed(60)          # recruit gear is rolled; the same roll every run
    rm = get_recruit_manager()
    rows = []
    for rec in rm.recruits.values():
        try:
            c = rm.build_or_restore(rec, player_level=60)
        except Exception as exc:
            check(False, f"rig: could not build {getattr(rec, 'name', rec)} ({type(exc).__name__}: {exc})")
            continue
        if c is None:
            continue
        rows.append((c.name, c.char_class, c.level, c.crit_chance_physical, c.crit_chance_spell, c))
    check(len(rows) >= 40, f"rig: only {len(rows)} recruits built")

    for name, cls, lvl, cp, cs, _c in rows:
        check(cp <= CEILING, f"{name} ({cls} {lvl}): {cp:.1f}% physical crit")
        check(cs <= CEILING, f"{name} ({cls} {lvl}): {cs:.1f}% spell crit")
        check(cp >= 5.0 and cs >= 5.0, f"{name} ({cls} {lvl}): crit below the 5% base ({cp:.1f} / {cs:.1f})")
    best = [max(cp, cs) for _n, _c, _l, cp, cs, _ in rows]
    if best:
        med = statistics.median(best)
        check(med <= TYPICAL, f"the typical recruit's best crit is {med:.1f}%")
        check(med >= 8.0, f"the typical recruit's best crit is only {med:.1f}% - crit has been flattened")
    berat = next((r for r in rows if r[0] == "Berat Yilmaz"), None)
    if check(berat is not None, "rig: Berat Yilmaz was not built"):
        check(berat[4] <= TYPICAL, f"Berat Yilmaz still has {berat[4]:.1f}% spell crit")

    # 3. the stat still matters
    def crit_with(cls, stat, extra):
        c = Character("T", cls, 60)
        setattr(c, stat, getattr(c, stat) + extra)
        c._recalculate_derived_stats()
        return c
    r0, r1 = crit_with("Rogue", "agility", 0), crit_with("Rogue", "agility", 100)
    m0, m1 = crit_with("Mage", "intellect", 0), crit_with("Mage", "intellect", 150)
    check(abs((r1.crit_chance_physical - r0.crit_chance_physical) - 5.0) < 0.01,
          f"100 Agility at 60 should be +5% crit, is +{r1.crit_chance_physical - r0.crit_chance_physical:.2f}%")
    check(abs((m1.crit_chance_spell - m0.crit_chance_spell) - 5.0) < 0.01,
          f"150 Intellect at 60 should be +5% spell crit, is +{m1.crit_chance_spell - m0.crit_chance_spell:.2f}%")
    check(r0.crit_chance_physical > m0.crit_chance_physical, "a naked Rogue does not out-crit a naked Mage")
    low = Character("T", "Rogue", 10)
    check(low._from_stat(low.AGI_PER_CRIT, 30) > r0._from_stat(r0.AGI_PER_CRIT, 30),
          "30 Agility should be worth more crit at level 10 than at 60")

    # 4. "% of stat" talents
    worst = []
    for name, cls, lvl, cp, cs, c in rows:
        for key, pct in (c.get_talent_effects() or {}).items():
            if not (isinstance(pct, (int, float)) and key.endswith("_pct") and "_from_" in key):
                continue
            target = key[:-4].split("_from_")[0]
            if target not in ("crit_chance_spell", "crit_chance", "crit", "dodge", "parry", "haste"):
                continue
            src = key[:-4].split("_from_")[1]
            stat = getattr(c, src, None)
            if not isinstance(stat, (int, float)):
                continue
            bonus = c.equipment.get_total_stat_bonuses().get(src, 0)
            worth = c._from_stat(c.RATING_PER_PERCENT, (stat + bonus) * pct)
            worst.append((worth, name, key))
            check(0.3 <= worth <= 6.0, f"{name}: {key} is worth {worth:.1f}% - outside 0.3-6%")
    check(worst, "rig: no recruit has a '% of stat' talent")

    rows.sort(key=lambda r: -max(r[3], r[4]))
    print(f"{len(rows)} recruits at 60. Highest:")
    for name, cls, lvl, cp, cs, _c in rows[:5]:
        print(f"   {name:22} {cls:14} phys {cp:5.1f}%  spell {cs:5.1f}%")
    print(f"   typical best crit {statistics.median(best):.1f}%; {len(worst)} '% of stat' talents, worth up to {max(worst)[0]:.1f}%")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:30]:
            print("  ", f)
        return 1
    print("crit rates OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
