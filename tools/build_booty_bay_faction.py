#!/usr/bin/env python3
"""Add the Booty Bay Port Authority to data/factions/factions.json. Idempotent.

    PYTHONPATH=. python3 tools/build_booty_bay_faction.py

WHY A SEVENTH FACTION AND NOT JUST STEAMWHEEDLE. The roster already has the Cartel - Gazlowe, home
Ratchet, lands at Friendly - and in WoW, Booty Bay IS Steamwheedle. Splitting them is a deliberate
deviation, so it needs a reason, and claude/stranglethorn_design.md gives it: the port outgrew the
company. When the land road south turned to rock, Booty Bay stopped being one of four franchises and
became the only deep-water harbour that still connects anything to anything. Gazlowe signs the
manifests in Ratchet. Revilgaz decides what actually sails.

That buys three things a duplicate goblin faction would not:
  * a port authority behaving like a government, which is a different animal from a trading company -
    it sets its own tariffs, keeps its own guard, and the only law is the Baron's;
  * a rivalry you can quest in, because Ratchet and Booty Bay want the same cargo and a player can run
    errands for either;
  * an explanation of the player's own arrival: you get there on a goblin boat, and the first thing you
    owe anyone in Stranglethorn is a landing fee.

STANDING: Honored on its own quests - more than Darkspear's beach, less than a capital. Per the roster's
invariant, Exalted needs more than questing, and there is nothing authored yet that takes it there.

ZONE OWNERSHIP, one zone one faction, enforced:
  Booty Bay           -> this faction
  Grom'gol            -> Orgrimmar (a Horde base camp; Orgrimmar already owns the Horde zones)
  the three wildernesses -> unclaimed, like Astranaar. Neither power holds the jungle between the two
    doors, and that is the point of the place: whichever way you come in, somebody owns the door and
    nobody owns the road.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KEY = "booty_bay_authority"

ENTRY = {
    "name": "The Booty Bay Port Authority",
    "description": "A goblin harbour that stopped being a franchise and started behaving like a government.",
    "home_zone": "booty_bay",
    "home_name": "Booty Bay, southern Stranglethorn",
    "leader": {
        "title": "Baron",
        "name": "Baron Revilgaz",
        "npc_id": "bootybay_baron",
        "location": "The lower shelf, Booty Bay",
        "line": "The Cartel will tell you this is their port. Let them. They are four thousand miles "
                "away and I am standing on it.",
    },
    "_lore_note": "Shown on the faction's detail panel. Written from the harbour's side of the argument, "
                  "because the harbour is the one winning it.",
    "lore": [
        "There is no road into Stranglethorn. The range closed the land route and never opened it again, "
        "which left two ways in: an airship berth the Horde flew in over the top, and this cove.",
        "That made Booty Bay the only deep-water harbour still joining anything to anything, and a "
        "harbour in that position stops taking instructions. The Baron did not declare anything. He "
        "simply began deciding which hulls left on which tide, and after the third season nobody was "
        "asking Ratchet.",
        "The Steamwheedle Cartel has not formally lost the port and will say so at length. Factor Weezel "
        "still signs the manifests, still files them, and still gets a polite reply. The replies do not "
        "change what sails.",
        "What the Authority sells is the same thing the Cartel always sold - a pier where two enemies "
        "can tie up and nothing happens - except that here it is enforced rather than negotiated. The "
        "bruisers are the law, the Baron is the court, and the tariff is not up for discussion. People "
        "complain about the landing fee until the first time they need the harbour to hold.",
    ],
    "quest_rep": {
        "_comment": "Honored is the ceiling on quests alone. Everything below is authored in Booty Bay "
                    "and the southern jungle - the Authority does not pay for work done north of the "
                    "Gurbashi, because north of the Gurbashi is Orgrimmar's problem.",
        "default": 250,
        "boss": 275,
        "capstones": {},
        "zones": ["booty_bay", "stranglethorn_south"],
        "also": [],
    },
    "kill_rep": {
        "_comment": "What costs the harbour money. Bloodsail on the water above all - a pirate in the "
                    "shallows is a hull that does not arrive - plus the naga sitting on the drowned "
                    "terraces the Authority would very much like to salvage. Jungle wildlife pays "
                    "nothing: it has never cost anyone a cargo.",
        "creatures": {},
    },
    "rewards": {
        "_comment": "No gates authored yet. The system supports them; the content is not written.",
    },
    "dungeon_rep": {
        "_comment": "A dungeon BOSS kill pays 75. Trash pays nothing, so the unit of progress is a boss. "
                    "The Authority takes bets on the Gurbashi and has a direct interest in who wins.",
        "per_boss": 75,
        "dungeons": ["Gurbashi Arena"],
    },
}


def main():
    path = ROOT / "data/factions/factions.json"
    data = json.loads(path.read_text())
    entry = dict(ENTRY)
    existing = data["factions"].get(KEY)
    if existing:
        # Preserve kill_rep creatures filled in by the content pass - this script is the lore and the
        # ladder, not the bestiary, and rerunning it must not wipe what the content builder wrote.
        entry["kill_rep"] = {**entry["kill_rep"], **{"creatures": existing["kill_rep"]["creatures"]}}
    data["factions"][KEY] = entry
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"factions: {len(data['factions'])} total, "
          f"{'updated' if existing else 'added'} {KEY}")


if __name__ == "__main__":
    main()
