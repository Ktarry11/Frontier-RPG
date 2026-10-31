#!/usr/bin/env python3
"""The buff panels must show real buffs and hide passive talents.

Kyle, 2026-10-31: "im not sure if this is a bug that was fixed when i go to
recruit players i left behind. they have all the possible buffs which pushes
everything down." His screenshot: a level 60 Holy priest joining with Desperate
Prayer / Blessed Recovery / Inspiration / Blessed Resilience / Spirit of
Redemption listed as ACTIVE EFFECTS at 999999t each, burying the panel.

Those are her TALENTS, not buffs. Character._sync_talent_procs gives every
proc-carrying talent node a permanent synthetic BUFF to hang the proc on.

NEGATIVE CONTROL IS THE POINT OF THIS TEST. A filter that drops everything
would pass a "no talents shown" assertion for free, so this also applies a real
buff and requires it to SURVIVE. Both halves, or the check is worthless.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from combat.status_effects import (StatusEffect, EffectType, is_displayable_buff,
                                   TALENT_PROC_PREFIX)
from entities.character import Character


def main():
    c = Character("QA Priest", "priest", level=60)
    if hasattr(c, "auto_spend_talents"):
        c.auto_spend_talents()
    if hasattr(c, "_sync_talent_procs"):
        c._sync_talent_procs()

    all_fx = list(c._effects())
    talents = [e for e in all_fx
               if str(getattr(e, "effect_id", "")).startswith(TALENT_PROC_PREFIX)]
    shown = [e for e in all_fx if is_displayable_buff(e)]

    print(f"  level 60 priest, talents auto-spent")
    print(f"  {len(all_fx)} effects on her, {len(talents)} of them synthetic talent procs")
    print(f"  buff panel would show {len(shown)}")

    ok = True

    if not talents:
        print("\n  INCONCLUSIVE - this build grants no talent procs, so the bug")
        print("  Kyle hit cannot be reproduced here. Not a pass.")
        return 1

    leaked = [e.name for e in shown
              if str(getattr(e, "effect_id", "")).startswith(TALENT_PROC_PREFIX)]
    if leaked:
        ok = False
        print(f"\n  FAIL - passive talents still in the buff panel: {leaked}")
    else:
        print(f"\n  ok - all {len(talents)} talent procs hidden "
              f"({', '.join(e.name for e in talents[:4])}...)")

    # NEGATIVE CONTROL: a real buff must still come through.
    c.apply_status_effect(StatusEffect(
        effect_id="qa_real_buff", name="Power Word: Fortitude",
        effect_type=EffectType.BUFF, duration=10,
        stat_mods={"stamina": 20}, source_name="QA", real_time_seconds=1800))
    shown2 = [e.name for e in c._effects() if is_displayable_buff(e)]
    if "Power Word: Fortitude" not in shown2:
        ok = False
        print("  FAIL (control) - a REAL buff was filtered out too. The filter")
        print("  is hiding everything, which would have made the test above pass")
        print("  for the wrong reason.")
    else:
        print("  ok (control) - a real buff still shows")

    # And a real DEBUFF.
    c.apply_status_effect(StatusEffect(
        effect_id="qa_real_debuff", name="Curse of Agony",
        effect_type=EffectType.DEBUFF, duration=4,
        stat_mods={}, source_name="QA"))
    if "Curse of Agony" not in [e.name for e in c._effects() if is_displayable_buff(e)]:
        ok = False
        print("  FAIL (control) - a real debuff was filtered out")
    else:
        print("  ok (control) - a real debuff still shows")

    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
