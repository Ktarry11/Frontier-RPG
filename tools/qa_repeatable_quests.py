#!/usr/bin/env python3
"""Repeatable turn-ins work end to end: take one, hand in a stack, gain standing, and it's on offer again.

    PYTHONPATH=. python3 tools/qa_repeatable_quests.py

The Argent Dawn's Scourgestones and the Pale Flame's Crusader's Insignia (tools/build_plaguelands_rewards.py) are
handed in by the stack as often as you have them (world/quest_manager.py turns a repeatable quest back to NOT_STARTED
when it's turned in). Also holds that no repeatable quest is a chain's predecessor or names a next quest, because a
repeatable never stays COMPLETED and would lock its chain forever.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    import json
    import pygame
    pygame.init()
    from entities.character import Character
    from entities.party import Party
    from entities.loot_item import add_loot_item, count_loot_items
    from world.quest_manager import QuestManager
    from world.quest import QuestStatus
    from world.faction_manager import get_faction_manager

    bad = []
    qm = QuestManager()
    reps = [q for q in qm.quests.values() if getattr(q, "repeatable", False)]
    if not reps:
        print("FAIL - no repeatable quests loaded")
        return 1
    ids = {q.quest_id for q in reps}
    for q in qm.quests.values():
        for r in (q.requires_quests or []):
            if r in ids:
                bad.append(f"{q.quest_id} requires {r}, which is repeatable and never stays completed")
    for q in reps:
        if q.next_quest_id:
            bad.append(f"{q.quest_id} is repeatable and names a next quest")

    with contextlib.redirect_stdout(io.StringIO()):
        hero = Character(name="QA", char_class="Warrior", level=60)
        party = Party(hero)
    fm = get_faction_manager()
    drops = json.loads((ROOT / "data/creatures/quest_drops.json").read_text(encoding="utf-8"))["drops"]
    dropped = {r["item_id"]: r for rows in drops.values() for r in rows}
    for q in reps:
        obj = q.objectives[0]
        if obj.target not in dropped:
            bad.append(f"{q.quest_id}: nothing drops {obj.target}")
            continue
        if dropped[obj.target].get("category") == "quest":
            bad.append(f"{q.quest_id}: {obj.target} is a quest item, so it stops dropping once you have enough")
        row = dropped[obj.target]
        for round_ in (1, 2):
            if not qm.accept_quest(q.quest_id, player_level=60, player=hero):
                bad.append(f"{q.quest_id}: couldn't be taken (round {round_})")
                break
            add_loot_item(hero, obj.target, row["name"], category=row.get("category", "quest"), amount=obj.count)
            qm.refresh_gather_progress(hero)
            fid, amt = fm.quest_reward({"quest_id": q.quest_id, "zone": q.zone})
            before = fm.factions[fid].standing if fid else 0
            if not qm.turn_in_quest(q.quest_id, hero, party):
                bad.append(f"{q.quest_id}: couldn't be handed in with a full stack (round {round_})")
                break
            gained = (fm.factions[fid].standing if fid else 0) - before
            if not fid or gained <= 0:
                bad.append(f"{q.quest_id}: paid no standing (round {round_})")
            if count_loot_items(hero, obj.target) != 0:
                bad.append(f"{q.quest_id}: the stack wasn't taken")
            if q.status != QuestStatus.NOT_STARTED:
                bad.append(f"{q.quest_id}: not on offer again after turn-in ({q.status})")
        print(f"  {q.quest_id:34} {fid}: +{amt} a stack of {obj.count}")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print(f"PASS - {len(reps)} repeatable turn-ins taken, handed in and offered again twice each")
    return 0


if __name__ == "__main__":
    sys.exit(main())
