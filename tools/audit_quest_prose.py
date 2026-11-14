"""Count the writing tics Kyle has named, per quest file, so the rewrite goes worst-first.

    python3 tools/audit_quest_prose.py            # table
    python3 tools/audit_quest_prose.py <stem>     # every hit in that file

  count     a number word in the prose that matches an objective's count ("Eleven of them")
            - standing rule: no counts in quest prose; the objective line carries the number
  aphorism  a distinction explained back at the player: "There is a difference", "That is the
            whole of it", "X is not Y. It is Z.", "which is its own problem"
  closer    a hand-in that ends on a stock line: "Take this.", "Thank you.", "You've earned it."
  stage     a bracketed stage direction in dialogue
  weary     a speaker narrating their own tiredness or mood
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

NUM = {w: i + 2 for i, w in enumerate(
    "two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen".split())}
APHORISM = re.compile(
    r"there is a difference|that is the (whole|entire) (of|job|post|story|report|point)|that is the job"
    r"|is not an? [a-z' -]{2,30}\. (it|that|he|she|they) (is|are) |which is (its own|the other|a different|the part|the thing)"
    r"|and that is (the|a|what|where|why|how)|make of that what you|i (am|was) aware (of )?how that sounds"
    r"|i know how that sounds|those are (two )?different|that is not a figure of speech|which tells you", re.I)
CLOSER = re.compile(r"(take this\.|thank you\.|you(?:'ve| have) earned it\.|take your pick\.?)\s*$", re.I)
WEARY = re.compile(r"sleeps? much|i have stopped (asking|arguing|finding|trying|being|pretending)|i am tired of|i no longer|"
                   r"i have not slept|i do not sleep", re.I)


def hits(q0, q):
    g = lambda k: (q.get(k) if isinstance(q, dict) else getattr(q, k, "")) or ""
    text = "\n".join(g(k) for k in ("description", "accept_text", "turn_in_text"))
    out = []
    counts = {o.get("count") for o in q0["objectives"] if (o.get("count") or 1) > 1}
    for m in re.finditer(r"\b(" + "|".join(NUM) + r")\b", text, re.I):
        if NUM[m.group(1).lower()] in counts:
            out.append(("count", text[max(0, m.start() - 30):m.end() + 40].replace("\n", " ")))
    for m in APHORISM.finditer(text):
        out.append(("aphorism", text[max(0, m.start() - 50):m.end() + 30].replace("\n", " ")))
    if CLOSER.search(g("turn_in_text")):
        out.append(("closer", g("turn_in_text")[-60:].replace("\n", " ")))
    for m in re.finditer(r"\[[^\]]*\]", text):
        out.append(("stage", m.group(0)[:80]))
    for m in WEARY.finditer(text):
        out.append(("weary", text[max(0, m.start() - 40):m.end() + 30].replace("\n", " ")))
    return out


def main():
    from world.quest_manager import QuestManager
    qs = QuestManager().quests
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    kinds = ["count", "aphorism", "closer", "stage", "weary"]
    print(f"{'file':24s}{'quests':>7s}" + "".join(f"{k:>10s}" for k in kinds) + f"{'any':>7s}")
    total = dict.fromkeys(kinds, 0)
    for path in sorted(glob.glob(str(ROOT / "data/quests/*.json"))):
        stem = os.path.basename(path)[:-5]
        quests = json.load(open(path, encoding="utf-8"))["quests"]
        row, dirty = dict.fromkeys(kinds, 0), 0
        for q0 in quests:
            q = qs.get(q0["quest_id"])
            if q is None:
                continue
            h = hits(q0, q)
            dirty += bool(h)
            for k, ctx in h:
                row[k] += 1
                if stem in only:
                    print(f"   {k:9s} {q0['quest_id']:34s} ...{ctx}...")
        for k in kinds:
            total[k] += row[k]
        if not only or stem in only:
            print(f"{stem:24s}{len(quests):7d}" + "".join(f"{row[k]:10d}" for k in kinds) + f"{dirty:7d}")
    print(f"{'TOTAL':24s}{'':7s}" + "".join(f"{total[k]:10d}" for k in kinds))


if __name__ == "__main__":
    main()
