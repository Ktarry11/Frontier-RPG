#!/usr/bin/env python3
"""The four quests that point into The Dry Deep can actually be finished.

    PYTHONPATH=. python3 tools/qa_dry_deep_quests.py

Kyle, 13 Nov 2026: the Dry Deep "can have some quests pointing there". A quest that points into
another map is the easiest kind to break: the place has to exist THERE, under the key the game
passes when you walk or kill there, not under the name on the door.

FOUR CLAIMS:
  1. EVERY PLACE A QUEST NAMES IS A TILE YOU CAN STAND ON, in the Dry Deep, reachable from a shaft.
  2. WALKING THERE AND KILLING THERE FINISHES THEM - played through the quest manager with the
     same zone key movement and combat pass, in chain order.
  3. EVERY KILL IS SOMETHING THE CAVE SPAWNS, and the boss is a boss.
  4. THE CAVE HAS ITS CHESTS AND BOSS MARKERS, and nothing in it is walled off.
"""
import contextlib
import io
import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from tools import handbuilt_dry_deep as D
    from world.quest_manager import QuestManager
    from world.quest import QuestStatus
    from world.zone_keys import zone_slug

CHAIN = ["dd_down_the_wide_sink", "dd_up_a_different_hole", "dd_what_eats_the_floor",
         "dd_the_weight_of_the_floor"]


def main():
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        zone, _L = D.build_dry_deep_baked()
        qm = QuestManager()
    key = zone_slug(zone.name)
    start = (D.PORTAL[0], D.PORTAL[1] + 2)
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < D.W and 0 <= n[1] < D.H and n not in seen and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)

    defs = {d["quest_id"]: d for d in json.load(open("data/quests/abyssal_sands.json"))["quests"]}
    table = json.load(open("data/creatures/encounters.json"))["zones"]["The Abyssal Sands"]["caves"]["The Dry Deep"]["creatures"]
    creatures = json.load(open("data/creatures/creatures.json"))
    creatures = creatures.get("creatures", creatures)

    for i, qid in enumerate(CHAIN):
        d = defs.get(qid)
        if d is None or qid not in qm.quests:
            bad.append(f"{qid} is not in the game")
            continue
        if i + 1 < len(CHAIN) and d.get("next_quest_id") != CHAIN[i + 1]:
            bad.append(f"{qid} does not lead on to {CHAIN[i + 1]}")
        qm.accept_quest(qid, player_level=60)
        quest = qm.quests[qid]
        if quest.status != QuestStatus.ACTIVE:
            bad.append(f"{qid} cannot be accepted after the one before it")
            continue
        for o in d["objectives"]:
            if o["type"] == "explore":
                if o["target"] != key:
                    bad.append(f"{qid}: explores '{o['target']}', the cave's key is '{key}'")
                p = (o["target_x"], o["target_y"])
                if p not in seen:
                    bad.append(f"{qid}: {o.get('label')} at {p} cannot be stood on")
                if not o.get("label"):
                    bad.append(f"{qid}: an explore objective has no name")
                qm.record_position_reached(key, *p)
            else:
                if o.get("zone") != key:
                    bad.append(f"{qid}: kills in '{o.get('zone')}', the cave's key is '{key}'")
                if o["target"] not in table:
                    bad.append(f"{qid}: the cave does not spawn {o['target']}")
                is_boss = bool(creatures.get(o["target"], {}).get("is_boss"))
                if (o["type"] == "kill_boss") != is_boss:
                    bad.append(f"{qid}: {o['target']} boss flag does not match the objective")
                for _ in range(o.get("count", 1)):
                    qm.record_kill(o["target"], key, is_boss=is_boss)
        if quest.status != QuestStatus.READY_TO_TURN_IN:
            bad.append(f"{qid} is not finished by doing what it asks")
        quest.status = QuestStatus.COMPLETED

    kinds = {}
    for row in zone.interaction_layer:
        for k in row:
            if k:
                kinds[k] = kinds.get(k, 0) + 1
    if kinds.get("chest", 0) != len(D.CHESTS) or kinds.get("boss_marker", 0) != len(D.BOSSES):
        bad.append(f"chests / boss markers on the map: {kinds}")
    for c in list(D.CHESTS) + list(D.BOSSES.values()):
        if not any((c[0] + dx, c[1] + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            bad.append(f"{c} cannot be reached")

    print(f"{len(CHAIN)} quests played through in '{key}'; {kinds}")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nDry Deep quests OK - every one can be walked to and finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
