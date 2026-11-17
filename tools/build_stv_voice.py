#!/usr/bin/env python3
"""Compile tools/stv_quest_voice.py into the overlay that the game reads last for Stranglethorn's quests.

    PYTHONPATH=. python3 tools/build_stv_voice.py            # check only
    PYTHONPATH=. python3 tools/build_stv_voice.py --write    # check, then write the overlay

Writes data/quests/text/zzzzzzzz_voice_stranglethorn.json, which loads after every other overlay (they load in
name order), so these lines are what the player reads. The earlier overlays for these quests are left as they
were; nothing else changes. Refuses to write if a line fails the voice bar (tools/audit_quest_voice.findings), if
a quest id doesn't exist, or if a field runs past the dialog's 760-character cap.
"""
import contextlib
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

from stv_quest_voice import VOICE                     # noqa: E402

OUT = ROOT / "data/quests/text/zzzzzzzz_voice_stranglethorn.json"
CAP = 760


class _Q:
    def __init__(self, qid, d, a, t):
        self.quest_id, self.description, self.accept_text, self.turn_in_text = qid, d, a, t


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from audit_quest_voice import findings
    known = set()
    for stem in ("stranglethorn_north", "stranglethorn_central", "stranglethorn_south"):
        known |= {q["quest_id"] for q in json.loads((ROOT / f"data/quests/{stem}.json").read_text(encoding="utf-8"))["quests"]}
    problems = []
    for qid, (d, a, t) in VOICE.items():
        if qid not in known:
            problems.append(f"{qid}: no such quest")
        for name, text in (("D", d), ("A", a), ("T", t)):
            if len(text) > CAP:
                problems.append(f"{qid} {name}: {len(text)} characters, over {CAP}")
            if any(ord(ch) > 127 for ch in text):
                problems.append(f"{qid} {name}: non-ASCII character")
        for field, p in findings(_Q(qid, d, a, t)):
            problems.append(f"{qid} {field}: {p}")
    print(f"  {len(VOICE)} quests rewritten, {len(problems)} problem(s)")
    for p in problems:
        print("  PROBLEM " + p)
    if "--write" in sys.argv:
        if problems:
            print("  REFUSING TO WRITE while there are problems")
            return 1
        doc = {qid: {"description": d, "accept_text": a, "turn_in_text": t} for qid, (d, a, t) in sorted(VOICE.items())}
        OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  written: {OUT.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
