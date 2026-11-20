#!/usr/bin/env python3
"""The Aetherians: the sky's faction, the scholar houses of Aurelion. Idempotent.

    PYTHONPATH=. python3 tools/build_aetherians_faction.py

docs/worldtree_brief.md, "The factions" and "Twenty questions". Kyle, 19 Nov 2026: "The Aetherians, Masters of the Upper
Sky", with the split he approved: reputation is with the scholar houses (and the survey that makes first contact), and
the Ascendancy, their military, is the enemy. Kyle, 20 Nov 2026: Aurelion is ruled by a council of the houses, and the
Ascendancy is getting too strong for the council to control; the houses disagree about what's killing their world.

The faction's home is Aurelion, which isn't built yet, so for now its standing comes from the Sunward Crown's survey
quests (tools/build_sunward_crown_quests.py writes the `also` list, which this keeps), and its leader, the council's
First Speaker, has no figure in the world until Aurelion is built. The quartermaster's shelf comes with Aurelion (the
TBC shelf like the others': Friendly supplies, Honored recipes, Revered ilvl 67 blues, Exalted ilvl 73 epics and the
mount), with a direction and never a cage: arcane, crystal and engineering, cloth and plate leaning.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FID = "aetherians"
FACTIONS = ROOT / "data/factions/factions.json"

ENTRY = {
    "name": "The Aetherians",
    "description": ("The scholar houses of Aurelion, the Masters of the Upper Sky, and the survey the House of the "
                    "Patient Lens sent down to the World Tree."),
    "home_zone": "aurelion",
    "home_name": "Aurelion, the city of the Aetherians, above the cloud",
    "leader": {
        "title": "First Speaker of the Council",
        "name": "Aldren Sorvaine",
        "location": "The Council Hall in Aurelion",
        "line": ("The houses have argued for a hundred years about what the ground is worth. We're about to find out, "
                 "because we can't hold up the sky without it."),
    },
    "_lore_note": ("Kyle, 19-20 Nov 2026: the Aetherian split (rep with the scholar houses, the Ascendancy is the "
                   "enemy), Aurelion ruled by a council of houses, the houses divided on what's killing their world. "
                   "docs/worldtree_brief.md. The leader has no npc_id until Aurelion is built."),
    "lore": [
        "Above the clouds there's a world nobody on the ground knew about, and the Aetherians have ruled the upper sky "
        "for as long as their records go back. They're tall and pale, with crystal growing along their arms and light "
        "in their eyes, and their cities float on engines of crystal older than any kingdom below.",
        "Since the world changed, their sky has been dying. The engines are failing, islands are falling, and the "
        "council of the scholar houses can't agree on why. Some houses say the World Tree is draining the sky and "
        "should be studied before anyone touches it. The Ascendancy, their army, says the tree is the only thing still "
        "rising and should simply be taken.",
        "The House of the Patient Lens sent a survey down to the tree to talk to the people living on it. It's the "
        "first time in their history the Aetherians have come down to meet the ground, and most of them still think "
        "the ground is primitive. The ones who've met it are starting to change their minds.",
    ],
    "quest_rep": {
        "_comment": "Per quest, paid by giver (tools/build_sunward_crown_quests.py).",
        "default": 200,
        "boss": 250,
        "capstones": {},
        "zones": ["sunward_crown", "lenswatch"],
        "also": [],
    },
}


def main():
    fd = json.loads(FACTIONS.read_text(encoding="utf-8"))
    old = fd["factions"].get(FID) or {}
    entry = json.loads(json.dumps(ENTRY))
    entry["quest_rep"]["also"] = list((old.get("quest_rep") or {}).get("also") or [])
    if "rewards" in old:
        entry["rewards"] = old["rewards"]
    fd["factions"][FID] = entry
    FACTIONS.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{ENTRY['name']}: written ({len(entry['quest_rep']['also'])} quests pay it)")


if __name__ == "__main__":
    main()
