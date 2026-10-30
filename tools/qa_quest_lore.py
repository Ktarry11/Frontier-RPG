#!/usr/bin/env python3
"""Does reading the quests teach you anything about this world?

    PYTHONPATH=. python3 tools/qa_quest_lore.py [--zone <file>] [--show]

Kyle, 2026-10-28: "Ensure quests are lore filled and alive... reading quests gives ideas about the world
itself."

WHAT THIS FOUND THE FIRST TIME IT RAN. The premise of the entire game appeared in 2% of its quests -
17 of 799 - and every one of those 17 was in a zone written in the last two days. Twenty quest files,
more than six hundred quests, did not acknowledge the Integration or the player's origin ONCE.

That is not restraint. claude/quest_writing_guide.md sets the target itself: "Players are Earth
transplants... NPCs know they came from 'that blue planet'. Use this as subtle flavor in roughly 10% of
quests only... Never make it the default tone." Ten percent is the design. Zero is a zone that was
written before the premise had any tooling and never revisited.

THE TARGET IS A BAND, NOT A FLOOR. Below about 6% the world forgets what happened to it; above about
18% every NPC is making the same observation and it stops landing. Both ends fail here.

WHAT COUNTS. A quest earns the mark by referring to the merge, to the people who came through it, or to
a native's view of either - not by containing a keyword. The patterns below are deliberately broad and
the --show flag prints the matches so a human can tell whether they are real.

Also checks the tired tics the writing guide names, because those are what make quests read as
generated even when the lore is right.
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

#: The band. Below LOW the world has amnesia; above HIGH every NPC is making the same remark.
#:
#: THE CEILING MOVED ON 2026-10-30, BECAUSE IT WAS STALE AND CONTRADICTED THE GUIDE IT CITES.
#:
#: This file's docstring still quotes claude/quest_writing_guide.md saying "roughly 10% of quests",
#: and 0.06-0.18 is the band you get by bracketing 10%. But the guide has not said 10% since
#: 2026-10-29, when Kyle replaced it: "Target: roughly 30% of quests. Kyle's call, 2026-10-29. This
#: replaces the 10% figure this guide carried until then." The band was never moved with it.
#:
#: The proof it was wrong rather than merely strict: at 0.18 this tool failed stranglethorn_south at
#: EXACTLY 30% - the number the guide names as the target - and reported it as "over-egged". A check
#: that fails content for hitting its own documented target is not a strict check, it is a broken one.
#:
#: 0.40 is "roughly 30%" read generously. It is deliberately NOT loose enough to pass everything:
#: stranglethorn_north still fails at 50%, which is correct and is the case Kyle himself called out -
#: the first Stranglethorn passes landed at 61-70% and read as zones whose single subject was the
#: Integration. The ceiling exists for exactly that and still catches it.
#:
#: THE FLOOR IS DELIBERATELY NOT MOVED. Raising it to match a 30% target would retroactively fail
#: nineteen finished zones that sit between 0% and 9%, which is a real content question (most of them
#: genuinely are silent) but it is Kyle's call about rewriting finished work, not a threshold to
#: change in passing while fixing the ceiling.
LOW, HIGH = 0.06, 0.40

#: ZONES THE INTEGRATION ACTUALLY HAPPENED TO ARE EXEMPT FROM THE CEILING. The first run of this tool
#: flagged the Aspen Wilderness at 24% as "over-egged" - a zone which IS a mountain range that arrived
#: three years ago, in quests about people trying to get down it. Of course it talks about the merge;
#: that is the subject. The ceiling is for Azeroth zones the event did not touch, where a native
#: remarking on it every fifth quest would be the tell.
INTEGRATION_ZONES = {"aspen", "southern_needles", "underdark", "underdark_dungeons"}

#: Referring to the merge, to the people it brought, or to a native's view of either.
#: WIDENED AFTER IT LIED. The first version wanted "three years AGO" and missed "Three years of you
#: lot walking in off nowhere", which is as direct a reference to the merge as exists - sixteen newly
#: written lines scored zero and the tool reported no change. The phrasings below are the ones the
#: writing actually uses. "three years" is safe on its own: per claude/integration_timeline.md that
#: exact span is the Integration's, while a native's tenure is written as any other number.
LORE = re.compile(
    r"integration|came (across|through)|crossed over|the day the (ground|world) changed|"
    r"since it happened|three years|that blue planet|other world|transplant|"
    r"(newly )?woken|the ones who (came|arrived)|you lot|not from (here|the plain|these)|"
    r"wasn'?t here|was not here|before the change|after the change|"
    r"somewhere flatter|out of nowhere|off nowhere|where you'?re from", re.I)

#: Named by claude/quest_writing_guide.md as the tics that make quest text read as filler.
TICS = {
    "Take your pick": re.compile(r"take your pick", re.I),
    "Thank you, friend": re.compile(r"thank you,? (friend|stranger)", re.I),
    '"kill N of X" phrasing': re.compile(r"\b(kill|slay|cull|thin)\s+(a\s+)?(dozen|\d+|ten|twelve|eight|six)\b", re.I),
}


def load():
    overlay = {}
    for f in sorted((ROOT / "data/quests/text").glob("*.json")):
        for qid, v in json.loads(f.read_text()).items():
            if isinstance(v, dict):
                overlay[qid] = v
    rows = []
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        data = json.loads(f.read_text())
        qs = data.get("quests", [])
        for q in (qs if isinstance(qs, list) else list(qs.values())):
            o = overlay.get(q["quest_id"], {})
            blob = " ".join(str(o.get(k) or q.get(k) or "")
                            for k in ("description", "accept_text", "turn_in_text"))
            rows.append((f.stem, q, blob))
    return rows


def main():
    rows = load()
    only = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    if only:
        rows = [r for r in rows if r[0] == only]
    show = "--show" in sys.argv

    hit = defaultdict(int)
    tot = defaultdict(int)
    examples = defaultdict(list)
    for zone, q, blob in rows:
        tot[zone] += 1
        m = LORE.search(blob)
        if m:
            hit[zone] += 1
            examples[zone].append((q["quest_id"], m.group(0)))

    total_hit = sum(hit.values())
    print(f"== the world's own story, across {len(rows)} quests")
    print(f"   {total_hit} mention the Integration or the people it brought "
          f"({100 * total_hit / max(1, len(rows)):.0f}%)   target {LOW:.0%}-{HIGH:.0%}\n")

    print(f"{'file':<26}{'n':>4}{'lore':>6}{'rate':>7}   verdict")
    fails = []
    for zone in sorted(tot, key=lambda z: hit[z] / tot[z]):
        n, h = tot[zone], hit[zone]
        rate = h / n
        # A ceiling on a 14-quest file is noise: three hits is 21% and means nothing. Floors still
        # apply at any size, because a zone with no mention at all is a zone with no mention at all.
        if rate < LOW:
            verdict = "SILENT - nothing here knows what happened to the world"
            fails.append(f"{zone}: {h}/{n} ({rate:.0%}) - below the {LOW:.0%} floor")
        elif rate > HIGH and zone not in INTEGRATION_ZONES and n >= 20:
            verdict = "over-egged - every other NPC is making the same remark"
            fails.append(f"{zone}: {h}/{n} ({rate:.0%}) - above the {HIGH:.0%} ceiling")
        elif rate > HIGH:
            verdict = "high, and correct - the merge is this zone's subject"
        else:
            verdict = "ok"
        print(f"{zone:<26}{n:>4}{h:>6}{rate:>6.0%}   {verdict}")
        if show and examples[zone]:
            for qid, frag in examples[zone][:4]:
                print(f"        {qid:<28}{frag!r}")

    print("\n== tired phrasing (claude/quest_writing_guide.md)")
    for name, pat in TICS.items():
        hits = [(z, q["quest_id"]) for z, q, b in rows if pat.search(b)]
        rate = len(hits) / max(1, len(rows))
        print(f"  {name:<24}{len(hits):>4}  ({rate:.1%})")
        # RATE, NOT PRESENCE. The guide says "vary closers", not "never say this" - and the lines
        # using these turned out to be good ones: "Take your pick of the leftover axes. They're not
        # good, but they're mine." Flagging any use at all would mean degrading real prose to satisfy
        # a grep. It is a tic when it is the DEFAULT closer, so the bar is 8%.
        if rate > 0.08:
            fails.append(f"{name!r} is the default closer in {rate:.0%} of quests")
        if show:
            for z, qid in hits[:6]:
                print(f"        {z}/{qid}")

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
