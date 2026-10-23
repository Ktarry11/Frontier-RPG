"""Compile tools/quest_text_src/<zone>.txt -> data/quests/text/<zone>.json (loaded as an overlay by QuestManager).

Source format (blank line between quests):
    @ quest_id
    Title: optional new title
    D: journal/offer description (grey text)
    A: accept text (what the NPC says when offering)
    T: turn-in text (what the NPC says when you hand in)
Continuation lines are joined with a space. Plain ASCII only (the game font has no curly quotes or em dashes).
Run: python3 tools/build_quest_text.py [zone ...]   (no args = every source file). Also validates ids and lengths."""
import glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMITS = {"description": 760, "accept_text": 760, "turn_in_text": 760}
KEYS = {"Title": "title", "D": "description", "A": "accept_text", "T": "turn_in_text"}


def known_ids():
    ids = set()
    for p in glob.glob(os.path.join(ROOT, "data/quests/*.json")):
        ids |= {q["quest_id"] for q in json.load(open(p))["quests"]}
    return ids


def parse(path):
    out, cur, key = {}, None, None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("#") and cur is None:
            continue
        if line.startswith("@ "):
            cur = line[2:].strip(); out[cur] = {}; key = None; continue
        if not line.strip():
            key = None; continue
        m = re.match(r"^(Title|D|A|T):\s*(.*)$", line)
        if m and cur:
            key = KEYS[m.group(1)]; out[cur][key] = m.group(2).strip()
        elif key and cur:
            out[cur][key] += " " + line.strip()
    return out


def main(zones):
    ids = known_ids(); bad = 0
    files = [os.path.join(ROOT, "tools/quest_text_src", z + ".txt") for z in zones] if zones else sorted(glob.glob(os.path.join(ROOT, "tools/quest_text_src/*.txt")))
    for f in files:
        data = parse(f); zone = os.path.basename(f)[:-4]
        for qid, fields in data.items():
            if qid not in ids:
                print(f"  UNKNOWN quest id {qid} in {zone}"); bad += 1
            for k, v in fields.items():
                if not v.isascii():
                    print(f"  NON-ASCII in {qid}.{k}: {[c for c in v if not c.isascii()][:5]}"); bad += 1
                if k in LIMITS and len(v) > LIMITS[k]:
                    print(f"  TOO LONG {qid}.{k}: {len(v)}"); bad += 1
            for k in ("description", "accept_text", "turn_in_text"):
                if k not in fields:
                    print(f"  MISSING {k} in {qid}"); bad += 1
        os.makedirs(os.path.join(ROOT, "data/quests/text"), exist_ok=True)
        json.dump(data, open(os.path.join(ROOT, "data/quests/text", zone + ".json"), "w"), indent=1, ensure_ascii=True)
        print(f"{zone}: {len(data)} quests")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
