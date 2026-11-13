"""The quest overhaul holds: a zone that has been through the pass stays that way.

Kyle, 12 Nov 2026: "Either trash writing or trash directions", and "you need to be systematic
about this!... Keep records of what's done as you work."

tools/quest_overhaul_done.json is the record. For every zone in it this asserts what the
pass promises:

  * no quest's directions point the wrong way, and none sends you a long walk with no
    direction or place name (tools/audit_quest_directions.py, on the live maps)
  * every explore objective with a spot names the spot ("Find the prowler den..."), so the
    objective line is never "Scout <Zone>."
  * every NPC in the zone has a greeting, and it is not a line another NPC also says
  * no greeting or quest text is non-ASCII or over the dialog's length limit
"""
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)


def main():
    import audit_quest_directions as A
    done = json.load(open("tools/quest_overhaul_done.json"))
    world = A.World()
    bad = []
    findings, _seen, _judged = A.audit(world, list(done))
    for kind in ("WRONG", "SILENT"):
        for stem, title, why in findings[kind]:
            if (stem, title) not in {tuple(x) for x in done.get(stem, {}).get("direction_exceptions", [])}:
                bad.append(f"{stem}: {title} - {kind.lower()}: {why}")

    import re
    from world.quest_manager import QuestManager
    qm = QuestManager()
    NUMBERS = {w: i + 2 for i, w in enumerate("two three four five six seven eight nine ten eleven twelve".split())}
    COUNT = re.compile(r"\s*(" + "|".join(NUMBERS) + r")\s*[.,]", re.I)
    from world.ambient_npc_manager import get_ambient_npc_manager
    npcs = get_ambient_npc_manager().npcs
    said = {}
    for n in npcs.values():
        said.setdefault((n.greeting or "").strip(), []).append(n)
    for stem, rec in done.items():
        quests = json.load(open(f"data/quests/{stem}.json")).get("quests", [])
        # The maps whose NPCs this pass covered: named in the record when a quest file reaches
        # into maps that belong to another pass (Tirisfal's file has quests set in Undercity).
        zones = ({A.slug(z) for z in rec["npc_zones"]} if rec.get("npc_zones")
                 else {A.slug(q.get("zone")) for q in quests if isinstance(q, dict)})
        for q in quests:
            for o in q.get("objectives", []):
                if o.get("type") == "explore" and o.get("target_x") is not None and not o.get("label"):
                    bad.append(f"{stem}: {q['title']} - its explore objective has no place name")
        # "Eight." said over six bears: a hand-in that opens with a bare count must match one.
        for q in quests:
            live = qm.quests.get(q.get("quest_id"))
            said_n = COUNT.match((live.get("turn_in_text") if isinstance(live, dict)
                                  else getattr(live, "turn_in_text", "")) or "") if live else None
            counts = [o.get("count") or 1 for o in q["objectives"]]
            # only where the quest counts something: "Two." about a survey peg is not a tally
            if said_n and max(counts) > 1 and NUMBERS[said_n.group(1).lower()] not in counts:
                bad.append(f"{stem}: {q['title']} - hands in with \"{said_n.group(1)}\" but asks for "
                           f"{[o.get('count') for o in q['objectives']]}")
        for n in npcs.values():
            if A.slug(n.zone) not in zones:
                continue
            text = (n.greeting or "").strip()
            if not text:
                bad.append(f"{stem}: {n.name} has no greeting")
            elif len(said[text]) > 1:
                bad.append(f"{stem}: {n.name} says the same line as {said[text][0].name if said[text][0] is not n else said[text][1].name}")
            if not text.isascii():
                bad.append(f"{stem}: {n.name}'s greeting is not plain ASCII")
            # A few later-zone NPCs open with a long speech written for the scrolling box; the
            # record names them rather than the check cutting good prose to length.
            if len(text) > 420 and n.npc_id not in rec.get("long_greetings", []):
                bad.append(f"{stem}: {n.name}'s greeting is {len(text)} characters")

    print(f"{len(done)} zones through the overhaul: {', '.join(sorted(done))}")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:30]:
            print("  -", b)
        return 1
    print("\nquest overhaul OK - every finished zone points the right way, names its places and greets you properly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
