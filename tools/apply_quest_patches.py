"""Apply the quest overhaul's small corrections from tools/quest_patches/<stem>.json.

Most quests are well written and wrong about one thing: which way to walk, or what a place
is called. Rewriting the whole text to move one word risks losing the voice, so a patch says
only what changes:

    {"quest_id": {
        "accept_text": "...",                      # replaces the short line under the offer
        "title": "...",
        "sub": [["old sentence", "new sentence"]], # replaced inside the description
        "labels": ["place one", "place two"]       # names for its explore objectives, in order
    }}

Text goes to the overlay data/quests/text/zz_overhaul_<stem>.json (QuestManager lays it over
last); labels go onto the objectives in data/quests/<stem>.json. Safe to re-run: a "sub" whose
old text is gone and whose new text is present is taken as done; anything else is an error.

    python3 tools/apply_quest_patches.py [stem ...]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from world.quest_manager import QuestManager
    qm = QuestManager()
    live = qm.quests if hasattr(qm, "quests") else qm._quests
    stems = sys.argv[1:] or sorted(p.stem for p in (ROOT / "tools/quest_patches").glob("*.json"))
    bad = []
    for stem in stems:
        patches = json.loads((ROOT / f"tools/quest_patches/{stem}.json").read_text())
        qpath = ROOT / f"data/quests/{stem}.json"
        data = json.loads(qpath.read_text())
        by_id = {q["quest_id"]: q for q in data["quests"]}
        opath = ROOT / f"data/quests/text/zz_overhaul_{stem}.json"
        overlay = json.loads(opath.read_text()) if opath.exists() else {}
        relabelled = 0
        for qid, p in patches.items():
            if qid not in by_id:
                bad.append(f"{stem}: no quest {qid}")
                continue
            entry = overlay.setdefault(qid, {})
            for k in ("accept_text", "title", "turn_in_text"):
                if k in p:
                    entry[k] = p[k]
            if p.get("sub"):
                q = live[qid]
                text = entry.get("description") or (q.get("description") if isinstance(q, dict)
                                                    else getattr(q, "description", ""))
                for old, new in p["sub"]:
                    if text.count(old) == 1:
                        text = text.replace(old, new)
                    elif new not in text:
                        bad.append(f"{stem}: {qid}: cannot find {old!r}")
                entry["description"] = text
            if p.get("labels"):
                spots = [o for o in by_id[qid]["objectives"] if o.get("type") == "explore"]
                if len(spots) != len(p["labels"]):
                    bad.append(f"{stem}: {qid}: {len(p['labels'])} labels for {len(spots)} places")
                    continue
                for o, label in zip(spots, p["labels"]):
                    if o.get("label") != label:
                        o["label"] = label
                        relabelled += 1
            if not entry:
                del overlay[qid]
        for qid, entry in overlay.items():
            for k, v in entry.items():
                if not v.isascii() or len(v) > 2400:
                    bad.append(f"{stem}: {qid}.{k} is not plain ASCII or is too long")
        opath.write_text(json.dumps(overlay, indent=2) + "\n")
        if relabelled:
            qpath.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"{stem}: {len(patches)} quests patched, {relabelled} places named")
    for b in bad:
        print("  !!", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
