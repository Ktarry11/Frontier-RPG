#!/usr/bin/env python3
"""A short combat cooldown must not be a 30-minute raid buff.

    PYTHONPATH=. python3 tools/qa_buff_scope.py

WHAT THIS CATCHES, and why nothing else could.

abilities.py:627-645 splits buffs into two archetypes, per Kyle:

    "raid"    -> real_time_seconds = BUFF_DURATION_SECONDS (30 real minutes)
    "combat"  -> real_time_seconds = None (turn-based via `duration`)

and it DEFAULTS TO "raid" FOR EVERY BUFF that does not say otherwise. The
consequence is the part that bites: StatusEffectMixin.tick_status_effects
(status_effects.py:962) explicitly skips any BUFF carrying a
real_time_seconds value - "'raid' scope - only tick_seconds() touches
this" - so for a raid-scope buff THE `duration` FIELD IS NEVER READ AT
ALL.

An ability authored as "duration: 1, cooldown: 18" therefore does not last
one turn. It lasts half an hour of real time, surviving every fight in
that window, and the 18-turn cooldown it was balanced around is paid once.
Felsworn's Illidan's Guile was exactly that. Chronomancer's two Continuum
spells were 60-turn "raid" buffs with no cooldown, so a player cast both on
turn one and kept them permanently - the opposite of CoA, where each has a
15-second cooldown, lasts seconds, and excludes the other.

Nothing existing could see it. The data is syntactically perfect: a real
duration, a real cooldown, real stat_mods. audit_talents checks talents,
not abilities. qa_ability_text checks that a description states a
mechanic - and these descriptions state the duration they will never
honour, which makes them actively misleading rather than empty. The only
way to notice is to compare the two fields against each other, which is
what this does.

THE RULE: a buff with a real cooldown AND a short stated duration is a
combat cooldown and must say buff_scope "combat". A genuine raid buff
(Fortitude, Mark of the Wild, Blessing of Kings) is cast out of combat,
has no meaningful cooldown, and is supposed to sit there - those are fine
and are what "raid" is for.

VERIFIED AGAINST THE REAL BREAKAGE before being trusted: run against
chronomancer.json as it stood on 6 Nov 2026 this reported both Continuum
spells; with the fix applied it reports neither, and the live effect comes
back with real_time_seconds None and duration 4. The negative control is
that it still finds 66 in the other classes, so it is not simply passing
everything.
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: A buff whose stated duration is longer than this is plausibly meant to
#: persist, so it is not judged here. Ten turns is already a long fight.
SHORT = 10

#: Deliberate exceptions, each with a reason. A raid buff that happens to
#: carry a duration and a cooldown is not a bug.
ALLOW = {
    # Mark of the Wild is a textbook raid buff - cast out of combat, sits
    # for the session. Its duration/cooldown fields are vestigial.
    "druid_mark_of_the_wild": "genuine out-of-combat raid buff",
}


def main():
    findings = []
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        for ability in json.loads(path.read_text()).get("abilities", []):
            if ability.get("effect_type") != "buff":
                continue
            aid = ability.get("ability_id", "?")
            if aid in ALLOW:
                continue
            # The engine's own default, which is the whole trap: an ability
            # that simply omits buff_scope gets "raid".
            scope = ability.get("buff_scope") or "raid"
            if scope != "raid":
                continue
            cooldown = ability.get("cooldown") or 0
            duration = ability.get("duration") or 0
            if cooldown > 0 and 0 < duration <= SHORT:
                findings.append((path.name, aid, cooldown, duration,
                                 "explicit" if ability.get("buff_scope")
                                 else "inherited the default"))

    if not findings:
        print("  0 SHORT COMBAT COOLDOWNS MASQUERADING AS RAID BUFFS\n\nPASS")
        return 0

    print(f"  {len(findings)} SHORT COMBAT COOLDOWNS ARE 'RAID' SCOPE")
    print("  Each lasts 30 real minutes and its `duration` is never read.\n")
    by_file = Counter(f for f, *_ in findings)
    for name, aid, cd, dur, how in findings:
        print(f"    {aid:48s} cooldown={cd:<3} duration={dur:<3} ({how})")
    print(f"\n  across {len(by_file)} classes: "
          f"{', '.join(f'{k[:-5]} {v}' for k, v in by_file.most_common())}")
    print("\n  Fix: set \"buff_scope\": \"combat\" so the turn duration is "
          "honoured,\n  or add to ALLOW with a reason if it really is a "
          "raid buff.")
    print("\nFAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
