#!/usr/bin/env python3
"""Compile a zone's rewritten quest text (tools/voice/<stem>.py) into the overlay the game reads last for it.

    PYTHONPATH=. python3 tools/build_zone_voice.py crossroads            # check only
    PYTHONPATH=. python3 tools/build_zone_voice.py crossroads --write    # check, then write
    PYTHONPATH=. python3 tools/build_zone_voice.py --all --write         # every module in tools/voice/

Kyle, 17 Nov 2026: "audit and fix the quests with the voice and tone we want since we have the proper style now".
The same pass Stranglethorn had (tools/build_stv_voice.py), for every other zone.

A module holds VOICE = {quest_id: (description, accept_text, turn_in_text)}. A field left as None keeps the text the
game shows now. The quest as it will read (new fields over the live ones) has to clear the voice bar
(tools/audit_quest_voice.findings) in all three fields, stay ASCII and stay under the dialog's 760-character cap;
otherwise nothing is written. Output: data/quests/text/zzzzzzzz_voice_<stem>.json, which loads after every other
overlay (they load in name order), so these lines are what the player reads.
"""
import contextlib
import importlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

CAP = 760
FIELDS = ("description", "accept_text", "turn_in_text")


class _Q:
    def __init__(self, qid, d, a, t):
        self.quest_id, self.description, self.accept_text, self.turn_in_text = qid, d, a, t


def build(stem, qm, findings, write):
    mod = importlib.import_module(f"voice.{stem}")
    voice = mod.VOICE
    known = {q["quest_id"] for q in json.loads((ROOT / f"data/quests/{stem}.json").read_text(encoding="utf-8"))["quests"]}
    out = ROOT / f"data/quests/text/zzzzzzzz_voice_{stem}.json"
    # the live text, without this zone's own overlay (so a re-run judges the module, not last run's output)
    old = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    problems, doc = [], {}
    for qid, fields in voice.items():
        if qid not in known:
            problems.append(f"{qid}: not a quest in {stem}.json")
            continue
        live = qm.quests[qid]
        merged = []
        for f, new in zip(FIELDS, fields):
            cur = getattr(live, f, "") or ""
            if new is None and f in old.get(qid, {}):
                problems.append(f"{qid} {f}: kept as None, but the old overlay rewrote it; spell it out")
            merged.append(cur if new is None else new)
        for f, text in zip(FIELDS, merged):
            if len(text) > CAP:
                problems.append(f"{qid} {f}: {len(text)} characters, over {CAP}")
            if any(ord(ch) > 127 for ch in text):
                problems.append(f"{qid} {f}: non-ASCII character")
        for f, p in findings(_Q(qid, *merged)):
            problems.append(f"{qid} {f}: {p}")
        doc[qid] = {f: v for f, v in zip(FIELDS, fields) if v is not None}
    print(f"  {stem}: {len(voice)} quests rewritten, {len(problems)} problem(s)")
    for p in problems:
        print("    PROBLEM " + p)
    if write and not problems:
        out.write_text(json.dumps(dict(sorted(doc.items())), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"    written: {out.relative_to(ROOT)}")
    elif write:
        print("    REFUSING TO WRITE while there are problems")
    return len(problems)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        args = sorted(p.stem for p in (ROOT / "tools/voice").glob("*.py") if p.stem != "__init__")
    with contextlib.redirect_stdout(io.StringIO()):
        from world.quest_manager import QuestManager
        from audit_quest_voice import findings
        qm = QuestManager()
    bad = sum(build(s, qm, findings, "--write" in sys.argv) for s in args)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
