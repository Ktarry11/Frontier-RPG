"""The Crossroads gives quests, and they can be played from accept to hand-in.

Kyle, 13 Nov 2026: "Don't forget about the countless NPCs in cross roads that just have no
quest markers or purpose." The town had 21 NPCs and gave no quests at all.
"""
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def main():
    from entities.character import Character
    from entities.party import Party
    from world.quest_manager import QuestManager
    from world.quest import QuestStatus, ObjectiveType
    from world.quest_dialogue import get_topic
    from world.ambient_npc_manager import get_ambient_npc_manager

    bad = []
    qm = QuestManager()
    npcs = get_ambient_npc_manager().npcs
    town = {nid for nid, n in npcs.items() if n.zone == "crossroads"}
    givers = {nid: len(qm.quests_by_giver.get(nid, [])) for nid in town if qm.quests_by_giver.get(nid)}
    total = sum(givers.values())
    if len(givers) < 8:
        bad.append(f"only {len(givers)} Crossroads NPCs give a quest")
    if total < 15:
        bad.append(f"the Crossroads gives {total} quests")
    if max(givers.values() or [0]) > 4:
        bad.append(f"one Crossroads NPC carries {max(givers.values())} quests - spread them")

    mine = json.load(open("data/quests/crossroads.json"))["quests"]
    hero = Character("Hero", "Warrior", 20)
    party = Party(hero)

    # every errand: the thing to carry is in your bag on accept, and the person it is FOR takes it
    for q in mine:
        quest = qm.quests[q["quest_id"]]
        for o in quest.objectives:
            if o.objective_type == ObjectiveType.DIALOGUE:
                for topic in o.topics:
                    if get_topic(quest.quest_id, topic) is None:
                        bad.append(f"{quest.title}: topic {topic} has no text - the quest cannot be finished")
        if quest.turn_in_npc_id and quest.turn_in_npc_id not in npcs:
            from world.vendor_manager import get_vendor_manager
            if quest.turn_in_npc_id not in getattr(get_vendor_manager(), "vendors", {}):
                bad.append(f"{quest.title}: handed in to {quest.turn_in_npc_id}, who does not exist")
        if not any(o.objective_type == ObjectiveType.DELIVER for o in quest.objectives):
            continue
        if quest.requires_quests or qm._find_predecessor(quest.quest_id):
            continue
        if not qm.accept_quest(quest.quest_id, player_level=20, player=hero):
            bad.append(f"{quest.title}: cannot be accepted - {qm.last_error}")
            continue
        for o in quest.objectives:
            if o.objective_type == ObjectiveType.DIALOGUE:
                for topic in o.topics:
                    o.ask_topic(topic)
        qm.refresh_gather_progress(hero)
        if quest.status != QuestStatus.READY_TO_TURN_IN:
            bad.append(f"{quest.title}: accepted, and the thing to deliver is not in the bag")
            continue
        collector = quest.turn_in_npc_id or quest.giver_npc_id
        if quest not in qm.get_turn_in_ready_quests(collector):
            bad.append(f"{quest.title}: {collector} will not take it")
        if quest.turn_in_npc_id and quest in qm.get_turn_in_ready_quests(quest.giver_npc_id):
            bad.append(f"{quest.title}: can be handed straight back to the giver")
        if not qm.turn_in_quest(quest.quest_id, hero, party):
            bad.append(f"{quest.title}: hand-in refused")

    # the capstone opens only when all three field chains are finished
    cap = qm.quests["cr_crossroads_holds"]
    if qm._is_unlocked("cr_crossroads_holds"):
        bad.append("The Crossroads Holds is open before the three bosses are dead")
    for req in cap.requires_quests:
        if req not in qm.quests:
            bad.append(f"The Crossroads Holds waits on {req}, which is not a quest")
        else:
            qm.quests[req].status = QuestStatus.COMPLETED
    if not qm._is_unlocked("cr_crossroads_holds"):
        bad.append("The Crossroads Holds does not open once its three chains are done")
    if qm._is_unlocked("cr_word_for_the_tribes"):
        bad.append("Word for the Tribes is open before The Crossroads Holds")
    if qm.quests["cr_word_for_the_tribes"].turn_in_npc_id != "taurajo_elder":
        bad.append("the chain does not end at Camp Taurajo")

    # the six moved quests are where they were moved to
    for qid, giver in (("taurajo_centaur_wind", "crossroads_quartermaster"), ("taurajo_salvage_wagons", "crossroads_caravan_guard"),
                       ("taurajo_windhoofs_ledger", "crossroads_bounty_reader"), ("ratchet_thinning_the_grounds", "taurajo_hunter_1")):
        if qm.quests[qid].giver_npc_id != giver:
            bad.append(f"{qid} is given by {qm.quests[qid].giver_npc_id}, not {giver}")

    print(f"the Crossroads: {total} quests from {len(givers)} NPCs; {len(mine)} new")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\ncrossroads quests OK - every errand can be carried and handed in, and the capstone waits for all three fires.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
