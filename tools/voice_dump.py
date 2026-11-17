#!/usr/bin/env python3
"""Everything a rewrite needs for one zone file, as the game shows it now: giver, hand-in, objectives, the text.

    PYTHONPATH=. python3 tools/voice_dump.py crossroads [--all]

Only quests with voice findings are printed unless --all. Pair it with tools/quest_targets.py for directions.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    stem = sys.argv[1]
    with contextlib.redirect_stdout(io.StringIO()):
        from world.quest_manager import QuestManager
        from audit_quest_voice import findings
        qm = QuestManager()
    people = {}
    for f in ("ambient_npcs.json", "vendors.json", "trainers.json", "recruits.json"):
        p = ROOT / "data/npcs" / f
        if p.exists():
            doc = json.loads(p.read_text(encoding="utf-8"))
            for n in next(v for v in doc.values() if isinstance(v, list)):
                i = n.get("npc_id") or n.get("vendor_id") or n.get("trainer_id") or n.get("recruit_id")
                people.setdefault(i, n)
    for q in json.loads((ROOT / f"data/quests/{stem}.json").read_text(encoding="utf-8"))["quests"]:
        live = qm.quests.get(q["quest_id"])
        if live is None:
            continue
        fs = findings(live)
        if not fs and "--all" not in sys.argv:
            continue
        g = people.get(q.get("giver_npc_id"), {})
        t = people.get(q.get("turn_in_npc_id") or q.get("giver_npc_id"), {})
        obj = "; ".join(f"{o['type']} {o.get('count', 1)} {o.get('target')}" + (f" '{o['label']}'" if o.get("label") else "")
                        for o in q["objectives"])
        print(f"### {q['quest_id']} | {q['title']} | L{q.get('level_min')} | pre {q.get('prerequisite_quest') or q.get('requires_quests') or '-'}")
        print(f"giver {q.get('giver_npc_id')} = {g.get('name')} ({g.get('race')} {g.get('gender')})"
              f" | hand-in {t.get('name')} | {obj}")
        print("findings: " + "; ".join(f"{f[:1].upper()}:{p}" for f, p in fs))
        for f in ("description", "accept_text", "turn_in_text"):
            print(f"[{f[:1].upper()}] " + (getattr(live, f, "") or "").replace("\n\n", " // "))
        print()


if __name__ == "__main__":
    main()
