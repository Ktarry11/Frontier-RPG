#!/usr/bin/env python3
"""Score every zone's quest text against the voice bar, as the player reads it (overlays applied).

    PYTHONPATH=. python3 tools/audit_quest_voice.py                 # the league table, worst first
    PYTHONPATH=. python3 tools/audit_quest_voice.py stranglethorn   # every finding in files matching that
    PYTHONPATH=. python3 tools/audit_quest_voice.py --max 0 stranglethorn_north stranglethorn_central
                                                                    # exit 1 if any named file has a finding

Kyle, 17 Nov 2026: "Can you start to do a quest writing pass while we wait for art. Like I'm seeing issues in
STV with writing too. You have the template for what is good writing."

THE BAR is claude/quest_writing_guide.md and the 10 Nov playtest notes: a giver says who they are, what is wrong,
why it matters to them and what to do, in plain speech. This script measures what a machine can:

  * the tics tools/build_tempest_quests.voice_problems catches: "it is not X, it is Y", missing contractions,
    dashes, filler, "kill N of X", and fragments of one or two words;
  * refrains: a closer or address that turns up again and again across a zone ("friend", "Thank you", "Take
    your pick", "mon" in a speaker who isn't a troll is not checked: voice is a reader's call);
  * aphorism shapes the playtest named: "the difference between", "the gap between", "is the kind of", "X is
    one thing. Y is another", a line ending on a moral;
  * empty fields and turn-ins that are only thanks.

It does not judge whether a line is good. It finds the lines that certainly aren't, so a rewrite starts with them.
"""
import collections
import contextlib
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from tools.build_tempest_quests import voice_problems

FIELDS = ("description", "accept_text", "turn_in_text")

APHORISM = {
    "aphorism: the difference/gap between": re.compile(r"\bthe (difference|gap|distance) between\b", re.I),
    "aphorism: is the kind of": re.compile(r"\bis the (kind|sort) of (thing|man|woman|place|person)\b", re.I),
    "aphorism: X is one thing": re.compile(r"\bis one thing\b", re.I),
    "aphorism: and that's the point/whole": re.compile(r"\b(and )?that'?s the (whole )?(point|trick|thing)\b", re.I),
    "aphorism: some things": re.compile(r"^\s*some (things|men|people)\b|\. Some (things|men|people) ", re.I),
}
REFRAINS = {
    "friend": re.compile(r"\bfriend\b", re.I),
    "thank you": re.compile(r"\bthank(s| you)\b", re.I),
    "take your pick": re.compile(r"\btake your pick\b", re.I),
    "stranger": re.compile(r"\bstranger\b", re.I),
    "outsider": re.compile(r"\boutsider\b", re.I),
}
THANKS_ONLY = re.compile(r"^\W*(thank(s| you)|good work|well done|excellent|perfect)[^.!?]{0,30}[.!?]?\W*$", re.I)


def load():
    """{source file stem: [quest]} with the overlay text the game shows."""
    with contextlib.redirect_stdout(io.StringIO()):
        from world.quest_manager import QuestManager
        qm = QuestManager()
    by_file = {}
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        try:
            ids = [q["quest_id"] for q in json.loads(path.read_text(encoding="utf-8")).get("quests", [])
                   if isinstance(q, dict) and q.get("quest_id")]
        except (ValueError, OSError):
            continue
        qs = [qm.quests[i] for i in ids if i in qm.quests]
        if qs:
            by_file[path.stem] = qs
    return by_file


def findings(q):
    out = []
    for f in FIELDS:
        text = getattr(q, f, "") or ""
        if not text.strip():
            out.append((f, "empty"))
            continue
        for p in voice_problems(text):
            out.append((f, p))
        for name, rx in APHORISM.items():
            m = rx.search(text)
            if m:
                out.append((f, f"{name}: '{m.group(0).strip()}'"))
        if f == "turn_in_text" and THANKS_ONLY.match(text):
            out.append((f, "turn-in is only thanks"))
    return out


def refrains(qs):
    """{refrain: count} where a refrain shows up in more than a fifth of a zone's quests."""
    c = collections.Counter()
    for q in qs:
        text = " ".join(getattr(q, f, "") or "" for f in FIELDS)
        for name, rx in REFRAINS.items():
            if rx.search(text):
                c[name] += 1
    return {k: v for k, v in c.items() if v >= max(3, len(qs) // 5)}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cap = None
    if "--max" in sys.argv:
        cap = int(sys.argv[sys.argv.index("--max") + 1])
        args = [a for a in args if a != str(cap)]
    by_file = load()
    if not args:
        rows = []
        for stem, qs in by_file.items():
            n = sum(len(findings(q)) for q in qs)
            bad_q = sum(1 for q in qs if findings(q))
            rows.append((n / len(qs), stem, len(qs), bad_q, n, refrains(qs)))
        print(f"{'file':34s} {'quests':>6s} {'flagged':>7s} {'findings':>8s} {'per q':>6s}  refrains")
        for per, stem, nq, bq, n, ref in sorted(rows, reverse=True):
            print(f"{stem:34s} {nq:6d} {bq:7d} {n:8d} {per:6.2f}  {ref or ''}")
        return 0
    total = 0
    for stem, qs in by_file.items():
        if not any(a in stem for a in args):
            continue
        n = 0
        for q in qs:
            fs = findings(q)
            if fs:
                n += len(fs)
                print(f"{stem} | {q.quest_id} | {q.title}")
                for f, p in fs:
                    print(f"    {f:12s} {p}")
        ref = refrains(qs)
        print(f"== {stem}: {n} findings in {len(qs)} quests; refrains {ref or 'none'}\n")
        total += n + sum(ref.values())
    if cap is not None and total > cap:
        print(f"FAIL: {total} > {cap}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
