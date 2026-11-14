"""Does the quest text say what you are being sent to do?

Kyle's complaint about the later zones: "this isn't lore it's just confusion" - a speaker
talking round the job. This is the measurable half of that: for every kill / fetch / gather
objective, the offer text (description + accept) must NAME the thing - a distinctive word of
the creature's name, or of the item's name, or of the creature that carries the item.

    python3 tools/audit_quest_clarity.py            # table
    python3 tools/audit_quest_clarity.py <stem>     # every unnamed objective in that file
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
STOP = {"the", "of", "and", "a", "an", "old", "young", "great", "lesser", "greater", "elder", "dark",
        "wild", "mad", "lord", "lady", "captain", "sergeant", "chief", "boss", "master", "keeper"}


def stems(name):
    out = set()
    for w in re.findall(r"[a-z']+", str(name).lower().replace("_", " ")):
        w = w.replace("'", "")
        if len(w) > 3 and w not in STOP:
            out.add(w[:max(4, len(w) - 2)])       # "geomancers" ~ "geomancer" ~ "geomancy"
    return out


def main():
    from world.quest_manager import QuestManager
    qs = QuestManager().quests
    drops = json.load(open(ROOT / "data/creatures/quest_drops.json", encoding="utf-8"))["drops"]
    item_names, carriers = {}, {}
    for creature, rows in drops.items():
        for r in rows:
            item_names[r.get("item_id")] = r.get("name") or r.get("item_id")
            carriers.setdefault(r.get("item_id"), set()).add(creature)
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    print(f"{'file':24s}{'quests':>7s}{'unnamed':>9s}")
    total = 0
    for path in sorted(glob.glob(str(ROOT / "data/quests/*.json"))):
        stem = os.path.basename(path)[:-5]
        bad = []
        quests = json.load(open(path, encoding="utf-8"))["quests"]
        for q0 in quests:
            q = qs.get(q0["quest_id"])
            if q is None:
                continue
            g = lambda k: (q.get(k) if isinstance(q, dict) else getattr(q, k, "")) or ""
            text = re.sub(r"[^a-z ]", "", (g("description") + " " + g("accept_text") + " " + g("title")).lower().replace("'", ""))
            for o in q0["objectives"]:
                kind, tgt = o.get("type"), o.get("target")
                if kind in ("kill", "kill_boss"):
                    want = stems(tgt)
                    for alt in o.get("alt_targets") or []:
                        want |= stems(alt)
                elif kind in ("fetch", "gather"):
                    want = stems(item_names.get(tgt, tgt))
                    for c in carriers.get(tgt, ()):
                        want |= stems(c)
                else:
                    continue
                if want and not any(w in text for w in want):
                    bad.append((q0["quest_id"], kind, tgt, item_names.get(tgt, "")))
        total += len(bad)
        if not only or stem in only:
            print(f"{stem:24s}{len(quests):7d}{len(bad):9d}")
        if stem in only:
            for b in bad:
                print("   ", *b)
    print(f"{'TOTAL':24s}{'':7s}{total:9d}")


if __name__ == "__main__":
    main()
