#!/usr/bin/env python3
"""Four quests that point down into The Dry Deep.

    python3 tools/build_dry_deep_quests.py [--apply]

Kyle, 13 Nov 2026: "The dry deep is basically a cave system that can have some quests pointing
there, but its more of a transition between abyssal sands and the deeper layer." So not a quest
hub - no new NPCs. Four quests from three people who already stand in the Sands and have every
reason to want somebody to go down: the Rope-Hand who lowers things into holes, the Chief Surveyor
who wants to know what the floor fell into, and the Teamster who lost a road down one of them.

ADDITIVE. tools/build_abyssal_quests.py writes the zone's other 32 quests and is NOT re-run here:
the overhaul has patched that file since (labels, stripped counts), and regenerating it would undo
that. This merges four quests into data/quests/abyssal_sands.json by quest_id and nothing else, so
it is safe to run twice. It borrows the Sands builder's own Q() so the rewards are made the same
way and at the same budget.

Writing rules (claude/quest_overhaul_tracker): no counts in the prose, every kill named, places
named, ASCII only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import build_abyssal_quests as B                # noqa: E402

OUT = ROOT / "data/quests/abyssal_sands.json"
DD = "the_dry_deep"


def explore(x, y, label, radius=7):
    o = B.explore(DD, x, y, radius)
    o["label"] = label
    return o


def boss(name):
    return {"type": "kill_boss", "target": name, "count": 1, "zone": DD}


def quests():
    q = []
    q.append(B.Q(
        "dd_down_the_wide_sink", "Down the Wide Sink", B.VIZZI, B.AB, 45, 45, "cameup",
        "Climb down the Wide Sink into the Dry Deep and walk to the Drained Sea.",
        [explore(37, 40, "under the Wide Sink"), explore(60, 48, "the Drained Sea", 9)],
        "I have put a line down every hole on this map. Most of them it comes back up wet with "
        "nothing and you learn nothing.\n\nThe Wide Sink is different. The line goes slack. There "
        "is a FLOOR down there, and the debris has slumped into a ramp a person can walk.\n\nGo "
        "down the Wide Sink. It is the big pit south-west of this camp. At the "
        "bottom you are in the Dry Deep. Keep going until the "
        "roof lifts and you cannot see the far wall. Peska calls that room the Drained Sea. Then "
        "come and tell me I am not imagining it.",
        "So it is one room. Not eleven holes. One enormous room with a roof that has fallen in "
        "eleven places.\n\nI have been lowering lamps into the same cavern for two years from "
        "different sides and writing each one down as a separate hole.",
        nxt="dd_up_a_different_hole"))

    q.append(B.Q(
        "dd_up_a_different_hole", "Up a Different Hole", B.ODD, B.AB, 46, 46, "fallen",
        "Walk the Dry Deep from shaft to shaft and find out which sinkholes join underground.",
        [explore(62, 29, "under Nineteen Mile Pit"), explore(50, 67, "under the Long Collapse"),
         explore(89, 70, "under the Underlight")],
        "Vizzi says it joins up down there. I want to know if she is right, because I lost a "
        "road down Nineteen Mile and I have always wondered where it went.\n\nGo down into the "
        "Dry Deep by any hole that has a ramp. Find the daylight under Nineteen Mile Pit, the "
        "daylight under the Long Collapse and the daylight under the Underlight. If you can "
        "walk between all of them without coming up, then it is not a field of pits at all. "
        "It is a roof.",
        "All of them. You walked from one to the next under the desert.\n\nThen my road did not "
        "fall into a hole. It fell into a country. That is somehow worse and I am glad to "
        "know it.",
        nxt="dd_what_eats_the_floor"))

    q.append(B.Q(
        "dd_what_eats_the_floor", "What Eats the Floor", B.PESKA, B.AB, 46, 46, "survey",
        "Kill Hollowing Oozes and Limestone Crawlers in the Dry Deep, where they eat the rock "
        "that holds the desert up.",
        [B.k("Hollowing Ooze", 8, zone=DD), B.k("Limestone Crawler", 6, zone=DD)],
        "If there is one cavern under all of this then the question I am paid to answer has "
        "changed. It is no longer whether the pits are finished. It is whether the ROOF is.\n\n"
        "The Hollowing Oozes eat limestone and the Limestone Crawlers nest in what the oozes "
        "leave. Up here they are a nuisance. Down in the Dry Deep they are working on the "
        "pillars.\n\nGo down and thin them, the Hollowing Oozes and the Limestone Crawlers "
        "both, and look at what they have been eating while you are there.",
        "Then they are at the pillars. I thought they would be.\n\nI can slow it. I cannot "
        "stop it. But a survey that says how long is a better survey than one that says "
        "nothing, and that is the first honest line I will have written in two years.",
        nxt="dd_the_weight_of_the_floor"))

    q.append(B.Q(
        "dd_the_weight_of_the_floor", "The Weight of the Floor", B.VIZZI, B.AB, 47, 47, "cameup",
        "Kill the Weight of the Floor, the thing that stands in the middle of the Drained Sea.",
        [boss("The Weight of the Floor")],
        "There is something standing in the Drained Sea. My lamps find it and then they go "
        "out.\n\nIt is made of the same rock as the roof. I think it IS roof, a piece that came "
        "down whole and did not lie still. Peska's people will not go past it and I do not "
        "blame them.\n\nKill the Weight of the Floor. Go back down the Wide Sink, south-west of this "
        "camp, into the Dry Deep. It stands in the middle of the Drained Sea, the biggest room "
        "down there, and you will not mistake it for anything else.",
        "It is down. I felt it through the rope from up here.\n\nThe way further in is open, "
        "then. I do not know what is further in. Nobody has had a reason to find out until "
        "today."))
    return q


def main():
    doc = json.loads(OUT.read_text())
    have = {q["quest_id"]: i for i, q in enumerate(doc["quests"])}
    new = quests()
    for q in new:
        text = " ".join(str(q.get(k, "")) for k in ("title", "description", "accept_text", "turn_in_text"))
        if not text.isascii():
            print(f"FAILED: {q['quest_id']} has non-ASCII text")
            return 1
    for q in new:
        if q["quest_id"] in have:
            doc["quests"][have[q["quest_id"]]] = q
        else:
            doc["quests"].append(q)
    print(f"{len(new)} Dry Deep quests; the file now holds {len(doc['quests'])}")
    if "--apply" in sys.argv:
        OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        print("written")
        # B.Q() budgets rewards in fractions; stored gear is whole numbers (qa_whole_number_gear).
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
