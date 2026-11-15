#!/usr/bin/env python3
"""Nobody hands out a pile of quests (backlog B [37]).

    PYTHONPATH=. python3 tools/qa_quest_givers.py

Kyle: "Some quest givers carry far too many quests... Two or three per giver, more givers."

TWO CLAIMS:

  1. THE MOVES HOLD. data/reference/quest_giver_moves.json hands quests from overloaded givers to
     the people standing around them. The zone quest files are generated, so a re-run of a
     tools/build_*_quests.py would quietly hand them back. tools/apply_giver_moves.py --check
     must find nothing to do, and every moved quest's new giver must exist.
  2. NO NEW PILES. No giver carries more than CEILING quests, except the ones listed in
     ALLOWED with the reason they stay. A story told by one person about the place they stand
     (Sanu's waterworks, Ulla's five-zone survey) is one voice on purpose; a giver who is just
     where quests got left is not.
"""
import collections
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from apply_giver_moves import apply, load_moves  # noqa: E402

CEILING = 7
ALLOWED = {
    "cb_waterkeeper": "Sanu's chain is about the oasis she stands in (Kyle, 14 Nov: Sanu stays)",
    "gv_surveyor": "Ulla's quests are her own experiments, the end of a five-zone survey; split, they lose the voice",
    "ab_surveyor": "Peska's quests are her survey argument (is a road possible?), one voice on purpose",
}


def npc_ids():
    ids = set()
    for f in ("ambient_npcs.json", "vendors.json", "trainers.json", "recruits.json"):
        p = ROOT / "data" / "npcs" / f
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for v in doc.values() if isinstance(doc, dict) else [doc]:
            for r in v if isinstance(v, list) else []:
                if isinstance(r, dict):
                    ids |= {r.get(k) for k in ("npc_id", "vendor_id", "trainer_id", "recruit_id") if r.get(k)}
    return ids


def main():
    bad = []
    todo, missing = apply(check=True)
    bad += [f"move not applied: {t}" for t in todo]
    bad += [f"moved quest does not exist: {m}" for m in missing]
    ids = npc_ids()
    for q, m in load_moves().items():
        if m["giver"] not in ids:
            bad.append(f"{q} moved to {m['giver']}, who is nobody")

    count = collections.Counter()
    for path in glob.glob(str(ROOT / "data" / "quests" / "*.json")):
        for q in json.loads(Path(path).read_text(encoding="utf-8")).get("quests", []):
            if q.get("giver_npc_id"):
                count[q["giver_npc_id"]] += 1
    for g, n in count.most_common():
        if n <= CEILING:
            break
        if g not in ALLOWED:
            bad.append(f"{g} gives {n} quests (ceiling {CEILING})")
    for g in ALLOWED:
        if count[g] <= CEILING:
            bad.append(f"{g} is on the allowed list with {count[g]} quests - take it off")

    print(f"{len(load_moves())} quests moved; busiest givers: "
          + ", ".join(f"{g} {n}" for g, n in count.most_common(6)))
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nquest givers OK - the moves hold and nobody new carries a pile.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
