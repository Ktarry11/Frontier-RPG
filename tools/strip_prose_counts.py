"""Take objective counts and stock closers out of quest prose.

Kyle's standing rule: no count numbers in quest prose - the objective line carries the number,
and a number written twice drifts ("Eight." said over six bears). Most of them sit in two
formula sentences, which this rewrites; anything else is left for a hand pass and listed.

    "Ten, in the hollow proper."          ->  "In the hollow proper."
    "Ten of them, along the tideline."    ->  "Along the tideline."
    "Eight horns off the foothill rams"   ->  "Horns off the foothill rams"
    "Ten. Good."                          ->  "Good."
    "Eight down, and they are still..."   ->  "Done, and they are still..."
    "Six, and hung properly."             ->  "All of them, and hung properly."
    "All six."                            ->  "All of them."
    "Eight should do it"                  ->  "That should do it"
    hand-in ending "Take this." / "Thank you."  ->  the line before it

Only a number equal to one of the quest's own objective counts is touched. Changes go to the
overlay data/quests/text/zz_overhaul_<stem>.json. Safe to re-run.

    python3 tools/strip_prose_counts.py [--apply] [stem ...]
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

WORDS = "two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen".split()
NUM = {w: i + 2 for i, w in enumerate(WORDS)}
CLOSER = re.compile(r"\s*(Take this\.|Thank you\.|Take this\. You've earned it\.|You've earned it\.)\s*$")
START = r"(?:(?<=^)|(?<=[.!?]\s)|(?<=\n)|(?<=- ))"
KEEP_AFTER = {"of", "down", "should", "would", "will", "and", "is", "are", "was", "were", "more", "or",
              "fewer", "years", "year", "months", "month", "days", "day", "weeks", "nights", "times",
              "hours", "miles", "feet", "men", "to", "a", "the", "in", "on", "at", "for", "that"}


SKIP_NOUNS = {"hands", "islands", "regulars", "house", "people", "different", "dead", "between", "seasons",
              "winters", "attempts", "generations", "names", "fewer", "true", "still", "matched", "sound"}


def fix(text, counts):
    text = re.sub(r"([?!.]) \.", r"\1", text)
    if not counts:
        return text
    alt = "|".join(w for w in WORDS if NUM[w] in counts)
    if not alt:
        return text
    N = f"(?:{alt})"
    cap = lambda s: s[:1].upper() + s[1:]
    f = re.I
    # a sentence that is only the number: "Ten." / "Ten!"
    text = re.sub(START + N + r"[.!]\s+", "", text, flags=f)
    text = re.sub(START + N + r"[.!]$", "", text, flags=f)
    # "Ten of them, in the fields" / "Ten, in the hollow"
    text = re.sub(START + N + r"(?: of (?:them|these|those))?, (?!and\b)(\w)", lambda m: m.group(1).upper(), text, flags=f)
    text = re.sub(START + N + r" down, and ", "Done, and ", text, flags=f)
    text = re.sub(START + N + r" down\.", "Done.", text, flags=f)
    text = re.sub(START + N + r"(?: of (?:them|these|those))?, and ", "All of them, and ", text, flags=f)
    text = re.sub(START + N + r" (should|would|will|ought to) do", r"That \1 do", text, flags=f)
    text = re.sub(r"\b([Aa])ll " + N + r"\b(?! of)", r"\1ll of them", text, flags=f)
    text = re.sub(r"\b([Aa])ll " + N + r" of (them|these|those)\b", r"\1ll of \2", text, flags=f)
    # "Eight horns off the rams" at the start of a sentence -> "Horns off the rams"
    def lead(m):
        return m.group(0) if m.group(1).lower() in KEEP_AFTER else cap(m.group(1))
    text = re.sub(START + N + r" ([a-z][a-z'-]*)", lead, text, flags=f)
    text = re.sub(START + N + r" of (them|these|those)\b", lambda m: cap(m.group(1)), text, flags=f)
    # second round: the lists. "Eight of their binders, five plates, four tags" -> "Their binders, plates, tags"
    text = re.sub(START + N + r" of (the|their|those|these)\b", lambda m: cap(m.group(1)), text, flags=f)
    text = re.sub(START + N + r" (should|would|will|ought to) ", r"That \1 ", text, flags=f)
    text = re.sub(r"\b" + N + r" of (the|their|those|these|them)\b", r"\1", text, flags=f)
    def item(m):
        return m.group(0) if m.group(2).lower() in KEEP_AFTER | SKIP_NOUNS else m.group(1) + m.group(2)
    text = re.sub(r"(, |\band |\bme |\bbring |\btake |\bwant |\bneed |\bget |\bcut |\bmill |\bdig |\bfind )"
                  + N + r" ([a-z][a-z'-]*)", item, text, flags=f)
    # a fragment left without its number reads better as an order
    text = re.sub(START + r"Them (off|out of|on|in|at|along|round|while) ", r"Clear them \1 ", text)
    text = re.sub(START + r"Them and ", "Those, and ", text)
    text = re.sub(r"([?!.]) \.", r"\1", text)
    return re.sub(r"[ \t]+\n", "\n", text).strip()


def main():
    from world.quest_manager import QuestManager
    qs = QuestManager().quests
    apply = "--apply" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    changed_total = 0
    for path in sorted(glob.glob(str(ROOT / "data/quests/*.json"))):
        stem = os.path.basename(path)[:-5]
        if only and stem not in only:
            continue
        opath = ROOT / f"data/quests/text/zz_overhaul_{stem}.json"
        overlay = json.loads(opath.read_text()) if opath.exists() else {}
        n = 0
        for q0 in json.load(open(path))["quests"]:
            q = qs.get(q0["quest_id"])
            if q is None:
                continue
            counts = {o.get("count") for o in q0["objectives"] if (o.get("count") or 1) > 1}
            for k in ("description", "accept_text", "turn_in_text"):
                old = (q.get(k) if isinstance(q, dict) else getattr(q, k, "")) or ""
                new = fix(old, counts)
                if k == "turn_in_text":
                    stripped = CLOSER.sub("", new)
                    if len(stripped) >= 25:
                        new = stripped
                if new != old and len(new) >= 20 and new.isascii():
                    n += 1
                    if not apply and only:
                        print(f"--- {q0['quest_id']}.{k}\n  - {old[:300]!r}\n  + {new[:300]!r}")
                    overlay.setdefault(q0["quest_id"], {})[k] = new
        if n and apply:
            opath.write_text(json.dumps(overlay, indent=2) + "\n")
        changed_total += n
        print(f"{stem}: {n} fields {'rewritten' if apply else 'would change'}")
    print(f"total {changed_total}")


if __name__ == "__main__":
    main()
