"""
Every quest's objective line reads as a sentence, built from the LIVE objective objects.

Kyle's screenshots, 10 Nov: "Objectivetype.Kill Boss: Void Handmaiden.",
"Objectivetype.Fetch: moor adder gland.", "Objectivetype.Gather: herb bruiseweed."

QuestDialogScreen._objective_lines compared the objective's type against strings; in the live
game it is an Enum, so no branch ever matched and every objective fell through to a generic
line that printed the enum. It had only ever been exercised with dicts. So this suite uses the
real QuestManager's real quests, never a hand-made dict:

  - no line may contain "Objectivetype" or come from the generic fallback
  - no line may show a raw id (an underscore, or an all-lowercase item name)
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from world.quest_manager import get_quest_manager
    from ui.screens.quest_dialog_screen import QuestDialogScreen

    qm = get_quest_manager()
    quests = list(qm.quests.values())
    if len(quests) < 100:
        print(f"FAIL only {len(quests)} quests loaded - the rig is not seeing the game's quests")
        return 1

    screen = QuestDialogScreen.__new__(QuestDialogScreen)   # the method needs no pygame state
    screen.npc = None

    leaked, generic, raw = [], [], []
    lines_seen = 0
    kinds = {}
    for q in quests:
        try:
            lines = screen._objective_lines(q)
        except Exception as exc:
            print(f"FAIL {q.quest_id}: _objective_lines raised {type(exc).__name__}: {exc}")
            return 1
        for obj, line in zip([o for o in q.objectives
                              if getattr(o.objective_type, "value", o.objective_type) != "story"], lines):
            lines_seen += 1
            kind = getattr(obj.objective_type, "value", obj.objective_type)
            kinds[kind] = kinds.get(kind, 0) + 1
            if "objectivetype" in line.lower():
                leaked.append((q.quest_id, line))
            elif re.match(r"^[A-Z][A-Za-z ]*: ", line):
                generic.append((q.quest_id, line))
            if "_" in line:
                raw.append((q.quest_id, line))
            elif kind in ("fetch", "gather", "deliver"):
                # "Collect 8 moor adder gland." - a display name starts with a capital.
                words = re.sub(r"^(Collect|Deliver)( \d+)? ", "", line).rstrip(".")
                if words and words == words.lower():
                    raw.append((q.quest_id, line))

    print(f"{len(quests)} quests, {lines_seen} objective lines, by kind: "
          f"{dict(sorted(kinds.items()))}")
    bad = 0
    for label, rows in (("prints the enum", leaked), ("fell to the generic line", generic),
                        ("shows a raw id", raw)):
        if rows:
            bad += len(rows)
            print(f"\nFAIL {len(rows)} line(s) - {label}:")
            for qid, line in rows[:12]:
                print(f"   {qid}: {line}")
            if len(rows) > 12:
                print(f"   ... and {len(rows) - 12} more")
    if bad:
        return 1
    print("quest objective lines OK - every one is a sentence with display names.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
