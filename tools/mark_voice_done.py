#!/usr/bin/env python3
"""Record that a zone has been through the plain-voice pass, so tools/qa_quest_overhaul.py holds it there.

    PYTHONPATH=. python3 tools/mark_voice_done.py crossroads [more stems...]

Adds a "voice" entry to the zone's record in tools/quest_overhaul_done.json (indent 1, the file's own layout). A
zone that hasn't had the direction-and-greeting overhaul yet goes in tools/quest_voice_done.json instead, so the
voice bar holds it without claiming the rest.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "tools/quest_overhaul_done.json"
VOICE_ONLY = ROOT / "tools/quest_voice_done.json"
WHAT = ("Every flagged quest rewritten in plain voice (tools/voice/<stem>.py, overlay zzzzzzzz_voice_<stem>.json, "
        "built by tools/build_zone_voice.py), talk topics too where the zone has them: who, what's wrong, why, what "
        "to do and where, no dashes, fragments, aphorisms or missing contractions. Kyle: 'audit and fix the quests "
        "with the voice and tone we want'.")


def main():
    doc = json.loads(DONE.read_text(encoding="utf-8"))
    only = json.loads(VOICE_ONLY.read_text(encoding="utf-8")) if VOICE_ONLY.exists() else {}
    for stem in sys.argv[1:]:
        if stem in doc:
            doc[stem]["voice"] = {"date": "2026-11-17", "what": WHAT}
            print(f"  {stem}: voice recorded in quest_overhaul_done.json")
        else:
            only[stem] = {"date": "2026-11-17", "what": WHAT}
            print(f"  {stem}: voice recorded in quest_voice_done.json (no direction overhaul yet)")
    DONE.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    VOICE_ONLY.write_text(json.dumps(dict(sorted(only.items())), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
