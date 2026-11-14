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
        "I've had a rope down every hole on this map. Mostly it comes back up and tells me "
        "nothing.\n\nThe Wide Sink's different. The line goes slack partway, so there's a floor "
        "down there, and the rubble has slid into a ramp you could walk down.\n\nI'd like "
        "somebody to walk it. The Wide Sink is the big pit south-west of this camp. At the bottom "
        "you'll be in what we've been calling the Dry Deep. Keep going until you reach a cavern "
        "so big your lamp won't find the far wall. Peska named it the Drained Sea off my lamp "
        "readings. Then come back and tell me what's really down there.",
        "So it's all one cave. I've been lowering lamps into the same cavern from different "
        "sides for two years and logging every one as its own hole.\n\nPeska is going to make "
        "me redraw the whole map. Thanks for going down. This is yours.",
        nxt="dd_up_a_different_hole"))

    q.append(B.Q(
        "dd_up_a_different_hole", "Up a Different Hole", B.ODD, B.AB, 46, 46, "fallen",
        "Walk the Dry Deep from shaft to shaft and find out which sinkholes join underground.",
        [explore(62, 29, "under Nineteen Mile Pit"), explore(50, 67, "under the Long Collapse"),
         explore(89, 70, "under the Underlight")],
        "Vizzi says the holes all join up underneath. I want to know if that's true, because I "
        "lost a cart and a team down Nineteen Mile and I never found out where they ended "
        "up.\n\nGo down into the Dry Deep by any pit with a ramp. See if you can walk to the "
        "bottom of Nineteen Mile Pit, the Long Collapse and the Underlight without coming back "
        "up. You'll know each one by the daylight coming down the shaft.",
        "All three, and you never came up once.\n\nThen I know where my team ended up, and I "
        "can get down there myself to see to them. I've wanted to for a long time. Thank you.",
        nxt="dd_what_eats_the_floor"))

    q.append(B.Q(
        "dd_what_eats_the_floor", "What Eats the Floor", B.PESKA, B.AB, 46, 46, "survey",
        "Kill Hollowing Oozes and Limestone Crawlers in the Dry Deep, where they are eating "
        "the rock that holds the desert up.",
        [B.k("Hollowing Ooze", 8, zone=DD), B.k("Limestone Crawler", 6, zone=DD)],
        "If it's one cavern under all of this, then I've been asking the wrong question. I've "
        "been trying to work out whether the pits have stopped opening. What I should be asking "
        "is how long the roof will last.\n\nThe Hollowing Oozes dissolve limestone and the "
        "Limestone Crawlers nest in the holes the oozes leave. Up here that's a nuisance. Down "
        "in the Dry Deep they're eating the pillars that hold the roof up.\n\nGo down and "
        "kill as many of both as you can, and have a look at the pillars while you're there.",
        "That's about what I expected. They're well into the pillars.\n\nI can't stop it, but "
        "I can slow it down, and now I can put a number of years in the survey. That's more "
        "than I've been able to write in two years out here.",
        nxt="dd_the_weight_of_the_floor"))

    q.append(B.Q(
        "dd_the_weight_of_the_floor", "The Weight of the Floor", B.VIZZI, B.AB, 47, 47, "cameup",
        "Kill the Weight of the Floor, the thing that stands in the middle of the Drained Sea.",
        [boss("The Weight of the Floor")],
        "There's something standing in the Drained Sea. Every lamp I lower near it gets "
        "smashed.\n\nFrom what I could see it's made of the same stone as the roof. I think a "
        "piece of the roof came down in one lump and then got up. Peska's crew won't go near it "
        "and I can't survey past it.\n\nWe've been calling it the Weight of the Floor. Go back "
        "down the Wide Sink, south-west of this camp, into the Dry Deep. It's in the middle of "
        "the Drained Sea, the biggest cavern down there. Kill it if you can.",
        "I felt that through the rope from up here. It's dead, then.\n\nThere's a passage on "
        "the east side of the Sea that goes further down. I've never had a lamp past it. If you "
        "go looking, I'd like to hear what you find."))
    return q


def main():
    doc = json.loads(OUT.read_text(encoding="utf-8"))
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
        OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written")
        # B.Q() budgets rewards in fractions; stored gear is whole numbers (qa_whole_number_gear).
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
