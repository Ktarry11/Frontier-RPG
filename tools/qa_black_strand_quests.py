#!/usr/bin/env python3
"""The Black Strand's quests are the shape Kyle asked for.

    PYTHONPATH=. python3 tools/qa_black_strand_quests.py

Kyle, 13 Nov 2026: "some good high quality quests around here", "Aim for 30 quests per zone if you
can", "Don't forget trash can start quests", "Don't use weird AI tics". And the standing rules:
towns are hubs (about 70% of a zone's quests), a giver does not carry too many, quest items drop
three times in four, one clear chain leaves the zone, and nobody stands at the place their quest
sends you. (That every quest can be FINISHED is tools/audit_quests.py's job - it plays each one
through the real engine - and is not repeated here.)

SEVEN CLAIMS:
  1. AT LEAST THIRTY QUESTS, levels 50-53.
  2. THE TOWN IS THE HUB: at least 70% are given in Onyxhollow.
  3. NOBODY CARRIES MORE THAN THREE.
  4. TRASH STARTS QUESTS: at least two begin from something a monster drops, and each drop names
     the quest it starts.
  5. QUEST ITEMS DROP THREE TIMES IN FOUR.
  6. THE WORK VARIES: kill, fetch, explore, deliver, talk, craft and a boss are all present, and a
     chain ends at an NPC in another zone.
  7. THE TEXT IS PLAIN SPEECH: contractions in every accept line, and none of the constructions
     that made the first draft read as written by a machine.
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TICS = {
    "it is not X, it is Y": re.compile(r"\b(is|was|are) not (a|an|the)? ?[\w' ]{2,40}[.,;:] (it|that|this|they) (is|was|are)\b", re.I),
    "stiff 'do not' / 'I am' with no contraction": re.compile(r"\b(I am|do not|does not|did not|it is|that is|you will|I will|cannot|I have) \w"),   # clause-final "I am." is fine
    "em dash": re.compile(r" - |—"),
    "'which is to say'": re.compile(r"which is to say|in other words|that is the whole of", re.I),
}


def main():
    bad = []
    quests = json.loads((ROOT / "data/quests/black_strand.json").read_text())["quests"]
    drops = json.loads((ROOT / "data/creatures/quest_drops.json").read_text())["drops"]
    by_item = {r["item_id"]: r for rows in drops.values() for r in rows}

    if len(quests) < 30:
        bad.append(f"{len(quests)} quests")
    if any(not (50 <= q["level_min"] and q["level_max"] <= 53) for q in quests):
        bad.append("a quest outside 50-53")

    givers = collections.Counter(q["giver_npc_id"] for q in quests)
    town = sum(n for g, n in givers.items() if g.startswith("oh_"))
    if town < 0.7 * len(quests):
        bad.append(f"only {town} of {len(quests)} are given in Onyxhollow")
    heavy = {g: n for g, n in givers.items() if n > 3}
    if heavy:
        bad.append(f"givers carrying more than three: {heavy}")

    starters = [q for q in quests if q["giver_npc_id"].startswith("item:")]
    if len(starters) < 2:
        bad.append(f"{len(starters)} quests start from a drop")
    for q in starters:
        rec = by_item.get(q["giver_npc_id"][5:])
        if not rec or rec.get("starts_quest_id") != q["quest_id"]:
            bad.append(f"{q['quest_id']}: its drop does not start it")

    kinds = collections.Counter(o["type"] for q in quests for o in q["objectives"])
    for need in ("kill", "fetch", "explore", "deliver", "dialogue", "craft", "kill_boss"):
        if not kinds[need]:
            bad.append(f"no {need} objective anywhere")
    for q in quests:
        for o in q["objectives"]:
            if o["type"] == "fetch":
                rec = by_item.get(o["target"])
                if not rec or rec["chance"] < 0.75:
                    bad.append(f"{q['quest_id']}: {o['target']} drops at {rec and rec['chance']}")
    if not any((q.get("turn_in_npc_id") or "").startswith("ab_") for q in quests):
        bad.append("no chain ends at an NPC outside the zone")

    for q in quests:
        acc = q["accept_text"]
        if not q["giver_npc_id"].startswith("item:") and "'" not in acc:
            bad.append(f"{q['quest_id']}: no contraction in the accept line")
        for name, rx in TICS.items():
            for key in ("accept_text", "turn_in_text"):
                m = rx.search(q[key])
                if m:
                    bad.append(f"{q['quest_id']} {key}: {name} - '{m.group(0)}'")

    print(f"{len(quests)} quests, {town} from Onyxhollow ({town / len(quests):.0%}), "
          f"{len(givers)} givers, {len(starters)} started by a drop; "
          + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nBlack Strand quests OK - thirty-plus, town-centred, varied, and written the way people talk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
