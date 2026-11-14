#!/usr/bin/env python3
"""The Abyssal Sands is written in plain speech, and stays that way.

    PYTHONPATH=. python3 tools/qa_abyssal_voice.py

Kyle, 13 Nov 2026: "Don't use weird AI tics." The zone was rewritten that day by
tools/rewrite_abyssal_voice.py. This reads what the GAME reads (the quest file, the NPC records,
the dialogue topics), not the tool, so a later edit to the data is caught too.

FOUR CLAIMS:
  1. None of the banned constructions (the Black Strand's list) in any quest text, greeting, topic
     or quest-item tooltip.
  2. No word in capitals for stress.
  3. Every accept line has a contraction in it.
  4. Nobody says the pits are four years old. The Integration was three years ago.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.qa_black_strand_quests import TICS                      # noqa: E402
from tools.rewrite_abyssal_voice import GREETINGS, ITEM_TEXT, _walk  # noqa: E402
from world.quest_dialogue_abyssal import QUEST_TOPICS             # noqa: E402


def main():
    texts, accepts = {}, {}
    for q in json.loads((ROOT / "data/quests/abyssal_sands.json").read_text(encoding="utf-8"))["quests"]:
        if not q["quest_id"].startswith("ab_"):
            continue
        for f in ("description", "accept_text", "turn_in_text"):
            texts[f"{q['quest_id']}.{f}"] = q[f]
        accepts[q["quest_id"]] = q["accept_text"]
    for name in ("vendors", "ambient_npcs"):
        for rec in _walk(json.loads((ROOT / "data/npcs" / f"{name}.json").read_text(encoding="utf-8"))):
            nid = rec.get("npc_id") or rec.get("vendor_id")
            if nid in GREETINGS:
                texts[f"greeting {nid}"] = rec["greeting"]
    for rec in _walk(json.loads((ROOT / "data/creatures/quest_drops.json").read_text(encoding="utf-8"))):
        if rec.get("item_id") in ITEM_TEXT:
            texts[f"item {rec['item_id']}"] = rec["description"]
    for quest, topics in QUEST_TOPICS.items():
        for tid, t in topics.items():
            texts[f"topic {quest}/{tid}"] = t["response"]

    bad = []
    for key, t in texts.items():
        for name, rx in TICS.items():
            m = rx.search(t)
            if m:
                bad.append(f"{key}: {name}: ...{t[max(0, m.start() - 30):m.end() + 20]!r}")
        m = re.search(r"\b[A-Z]{3,}\b", t)
        if m:
            bad.append(f"{key}: a word in capitals: {m.group(0)}")
        if re.search(r"\bfour years\b", t, re.I):
            bad.append(f"{key}: says four years; the Integration was three years ago")
        if not t.isascii():
            bad.append(f"{key}: not ASCII")
    for qid, t in accepts.items():
        if not re.search(r"\w'(s|re|ve|ll|d|t|m)\b", t):
            bad.append(f"{qid}: no contraction in the accept line")
    greet = sum(k.startswith("greeting") for k in texts)
    if len(accepts) != 32 or greet != 8:
        bad.append(f"expected 32 quests and 8 greetings, read {len(accepts)} and {greet}")

    print(f"{len(accepts)} quests, {greet} greetings, {len(texts)} pieces of text read")
    for b in bad:
        print("  FAIL", b)
    print("\nAbyssal Sands voice OK - plain speech throughout." if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
