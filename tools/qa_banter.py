#!/usr/bin/env python3
"""Banter is in character, in the party, and never assumes the companions know each other.

    PYTHONPATH=. python3 tools/qa_banter.py [--sample]

THE RULE THIS EXISTS FOR. Kyle, 2026-10-28: "These people are all independent and don't know each
other." Party banter is the single most likely place to break that, because banter is FUN to write
pairwise and the first thing anybody reaches for is "X, you were right about the door." That line
assumes X is in the party, that the two have met, and that there is a history. None of it is true, and
none of it would raise anything at runtime - the line would simply ship and quietly contradict the
lore every time it fired.

So the hard checks are: no line names another companion, no line implies a shared past, and no line
addresses a specific person other than the player.

The soft ones are coverage: a trigger only one person can answer will put the same voice in the
player's ear every time, and a character with no lines never speaks at all.

--sample fires each trigger a few times with a real party and prints what comes out, which is the only
way to see whether the thing is actually pleasant.
"""
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from world.banter_manager import get_banter_manager, TRIGGERS  # noqa: E402

#: Phrasings that assume a shared history with another companion.
SHARED_PAST = re.compile(
    r"\b(you were right|like last time|as usual|told you so|remember when|again\?|"
    r"same as (last|before)|you always|we have done this)\b", re.I)


def main():
    recruits = json.loads((ROOT / "data/npcs/recruits.json").read_text())["recruits"]
    first_names = {r["recruit_id"]: r["name"].split()[0] for r in recruits}
    all_names = set(first_names.values())

    bm = get_banter_manager()
    lines = [ln for v in bm.by_trigger.values() for ln in v]
    fails = []

    print(f"== {len(lines)} lines, {len(set(l.recruit_id for l in lines))} characters, "
          f"{len(bm.by_trigger)} triggers\n")

    print("== nobody names another companion")
    named = []
    for ln in lines:
        words = set(re.findall(r"[A-Za-z']+", ln.text))
        hits = (words & all_names) - {first_names.get(ln.recruit_id)}
        if hits:
            named.append((ln.recruit_id, sorted(hits), ln.text[:60]))
    print(f"  {len(named)} offending lines")
    for rid, hits, t in named:
        fails.append(f"{rid} names {hits}: {t!r}")

    print("\n== nobody implies a shared past")
    shared = [(ln.recruit_id, ln.text) for ln in lines if SHARED_PAST.search(ln.text)]
    print(f"  {len(shared)} offending lines")
    for rid, t in shared:
        fails.append(f"{rid} implies a shared history: {t[:70]!r}")

    print("\n== coverage")
    cov = bm.coverage()
    for trig in TRIGGERS:
        per = cov.get(trig, {})
        opens = [r for r, (o, _) in per.items() if o]
        replies = [r for r, (_, rp) in per.items() if rp]
        print(f"  {trig:<16}{len(opens):>3} can open, {len(replies):>3} can reply")
        if not opens:
            fails.append(f"{trig}: nobody can open it - the trigger can never fire")
        elif len(opens) < 3:
            print(f"      note: only {opens} - the same voice every time")
    silent = sorted(set(first_names) - set(l.recruit_id for l in lines))
    print(f"  {len(silent)} characters with no lines at all")
    for s in silent:
        print(f"      {s}")

    print("\n== it fires with a real party")
    from entities.character import Character
    from entities.party import Party
    from world.recruit_manager import get_recruit_manager
    rm = get_recruit_manager()
    recs = {}
    for attr in ("recruits", "by_zone", "_recruits"):
        v = getattr(rm, attr, None)
        if isinstance(v, dict):
            for _k, x in v.items():
                if isinstance(x, list):
                    for z in x:
                        recs[z.recruit_id] = z
                elif hasattr(x, "recruit_id"):
                    recs[x.recruit_id] = x
    party = Party(Character("Player", "Warrior"))
    for rid in ("dan_warrior", "ama_priest", "owen_cultist", "marta_tinker"):
        if rid in recs:
            party.members.append(recs[rid].build_character())
    fired = 0
    for trig in TRIGGERS:
        beat = bm.fire(trig, party, force=True)
        if beat:
            fired += 1
            bm.current = None
    print(f"  {fired} of {len(TRIGGERS)} triggers produced a beat with a 4-companion party")
    if fired < len(TRIGGERS):
        fails.append(f"only {fired}/{len(TRIGGERS)} triggers fired for a normal party")

    if "--sample" in sys.argv:
        print("\n== sample")
        random.seed(3)
        for trig in TRIGGERS:
            print(f"  [{trig}]")
            for _ in range(2):
                bm.current = None
                bm.recent_speakers = []
                beat = bm.fire(trig, party, force=True)
                if beat:
                    for _rid, name, text in beat.lines:
                        print(f"      {name}: {text}")
            print()

    print()
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
