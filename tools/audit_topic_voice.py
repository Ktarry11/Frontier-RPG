#!/usr/bin/env python3
"""Score the talk-quest topics (world/quest_dialogue_<zone>.py) against the voice bar.

    PYTHONPATH=. python3 tools/audit_topic_voice.py              # findings per topic file
    PYTHONPATH=. python3 tools/audit_topic_voice.py crossroads   # every finding in that file

The same bar as tools/audit_quest_voice.py (Kyle, 17 Nov 2026), applied to what a talk quest's NPC says when you
pick a topic. Labels are the player's line, so only the response is judged for fragments.
"""
import contextlib
import importlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from audit_quest_voice import APHORISM
    from tools.build_tempest_quests import voice_problems


def topic_findings(suffix):
    mod = importlib.import_module(f"world.quest_dialogue_{suffix}")
    out = []
    for qid, topics in getattr(mod, "QUEST_TOPICS", {}).items():
        for tid, t in topics.items():
            text = t.get("response", "") or ""
            for p in voice_problems(text):
                out.append((qid, tid, p))
            for name, rx in APHORISM.items():
                m = rx.search(text)
                if m:
                    out.append((qid, tid, f"{name}: '{m.group(0).strip()}'"))
            if any(ord(c) > 127 for c in text + t.get("label", "")):
                out.append((qid, tid, "non-ASCII"))
    return out


def main():
    suffixes = sorted(p.stem[len("quest_dialogue_"):] for p in (ROOT / "world").glob("quest_dialogue_*.py"))
    args = sys.argv[1:]
    for s in suffixes:
        if args and s not in args:
            continue
        fs = topic_findings(s)
        print(f"{s:28s} {len(fs):4d} findings")
        if args:
            for qid, tid, p in fs:
                print(f"    {qid} / {tid}: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
