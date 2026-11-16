#!/usr/bin/env python3
"""The Order of the Pale Flame and the Argent Dawn (docs/plaguelands_design.md). Idempotent: upserts both factions'
identity, leader, lore and rep sources into data/factions/factions.json and leaves any `rewards` already there alone
(the shelves come from tools/build_faction_rewards.py once their items are authored).

    PYTHONPATH=. python3 tools/build_plaguelands_factions.py

THE ORDER OF THE PALE FLAME. Kyle, 16 Nov 2026: "I want a new faction. One that is unique because the leader and top
fighters are FROM EARTH. They're Order of the Pale Flame and they recruited defects from The Scarlet Crusade and
they're more selective in who they kill, they don't go after all undead, only mindless ones. They're mix between Argent
dawn and Scarlet Crusade and you get rep by killing Scarlet fanatics." And: "The leader WAS part of the Scarlet Crusade
though! that is Important! He joined during the Integration and walked away with others."

Rep (Kyle's answers, 16 Nov):
  * Scarlet kills in the Scarlet Monastery pay, CAPPED AT HONORED ("YES" to the cap); Hearthglen and quests carry you
    on to Exalted. (The Monastery's four wings are in `dungeon_rep`; Hearthglen joins when its map exists.)
  * Open-world Scarlets pay "Little until honored": 5 a kill, capped at Honored, in the Plaguelands. (Tirisfal's
    Scarlets already pay the Forsaken, and a creature pays one faction.)
  * Stratholme's Scarlet half pays too (assumed, in the design doc).
  * Rewards are "Standard rep style": the TBC shelves every faction uses.

THE ARGENT DAWN. Kyle chose "Yes, both": Scourgestone turn-ins, the Argent Dawn Commission (Scourge kills pay rep only
while you wear it; built with Light's Hope's people), shoulder enchants, gear by standing. Quests and the Scourge
dungeons pay from the start.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PATH = ROOT / "data/factions/factions.json"

from tools import handbuilt_scarlet_monastery as SM  # noqa: E402
from tools import build_scarlet_monastery_content as SMC  # noqa: E402

#: Open-world Scarlets: a little each, until Honored
#: Tirisfal's Scarlets already pay the Forsaken, and a creature pays one faction (qa_factions), so the Order's
#: open-world rep starts at the Plaguelands' border.
OPEN_WORLD_SCARLETS = [
    # South WPL (Andorhal)
    "Scarlet Outrider", "Scarlet Field Chaplain",
    # North WPL (Northridge and Hearthglen Fields)
    "Scarlet Lumberjack", "Scarlet Sawyer", "Scarlet Woodsman Archer", "Scarlet Sentry", "Hearthglen Inquisitor",
    "Scarlet Crossbowman", "Scarlet War Hound",
    # East EPL (Tyr's Hand)
    "Tyr's Hand Crusader", "Tyr's Hand Abbot", "Tyr's Hand Marksman", "Tyr's Hand Houndmaster",
]
OPEN_WORLD_RARES = ["Crusader Brennic", "Foreman Harrow", "High Inquisitor Faulk", "Abbot Varenne"]
#: The Scarlet Monastery's Scarlets pay more a kill, and also stop at Honored (Kyle: "YES" to the cap). Its dead pay
#: nothing: the Order wants the Crusade's people, and the Argent Dawn's Scourge are the ones in the Plaguelands.
SM_SCARLETS = SMC.SCARLETS

PALE_FLAME = {
    "name": "The Order of the Pale Flame",
    "description": ("A holy order led by Earth transplants who walked out of the Scarlet Crusade. They hunt the "
                    "mindless dead and the Crusade's fanatics, and they leave the thinking dead alone."),
    "home_zone": "western_plaguelands_south",
    "home_name": "Sorrow Hill, Western Plaguelands",
    "leader": {
        "title": "Flamekeeper",
        "name": "Rory Callahan",
        "npc_id": "wpl_pf_flamekeeper",
        "location": "Sorrow Hill, beside Uther's Tomb",
        "line": ("I wore the red for a year. When I took it off, I kept the flame and scraped the colour out of it, "
                 "and that's the whole of what we are."),
    },
    "_lore_note": ("Kyle, 16 Nov 2026: 'the leader and top fighters are FROM EARTH' and 'The leader WAS part of the "
                   "Scarlet Crusade though! that is Important!'. A mix of the Argent Dawn and the Crusade."),
    "lore": [
        "In the first year of the Integration, the Scarlet Crusade was the only army in Lordaeron killing what was "
        "killing everyone. A lot of transplants joined it, because it was there and it was winning.",
        "Rory Callahan was one of them. He was an ironworker from Boston by way of Cork, and he was good at it. He "
        "lasted a year. He left the night the Crusade burned a camp of transplants for keeping company with the "
        "Forsaken, and the best of the people around him left with him.",
        "They kept the flame and scraped the red out of it. The Order of the Pale Flame hunts the mindless dead, the "
        "Cult of the Damned, and the Crusade's fanatics. It doesn't hunt the Forsaken, and some of its members hate "
        "that rule more than any other.",
        "The Argent Dawn calls them Scarlets with better manners. The Order calls the Argent Dawn slow. They share "
        "what they learn about Scholomance and Stratholme anyway, because neither can afford not to.",
    ],
    "quest_rep": {
        "_comment": "Per quest, by shape. Matches the other factions' rates.",
        "default": 225,
        "boss": 250,
        "capstones": {},
        "_comment_zones": ("A zone's quests pay one faction (qa_factions). The Order's are the West; the Argent "
                           "Dawn's are the East. The Order's chains that run into the East go in `also`."),
        "zones": ["western_plaguelands_south", "western_plaguelands_north"],
    },
    "kill_rep": {
        "_comment": [
            "Scarlet fanatics only. Open-world Scarlets pay a little and stop at Honored (Kyle: 'Little until",
            "honored'). The Scarlet Monastery pays more and also stops at Honored; Hearthglen and Stratholme's",
            "Scarlet half don't stop. [amount, cap tier] is a capped kill (world/faction_manager.py).",
        ],
        "creatures": {**{n: [5, "honored"] for n in OPEN_WORLD_SCARLETS},
                      **{n: [25, "honored"] for n in OPEN_WORLD_RARES},
                      **{n: [10, "honored"] for n in SM_SCARLETS}},
    },
    "dungeon_rep": {
        "_comment": "A dungeon boss kill pays 75. The Monastery's wings are capped at Honored.",
        "per_boss": 75,
        "dungeons": list(SM.WINGS),
        "caps": {w: "honored" for w in SM.WINGS},
    },
}

ARGENT_DAWN = {
    "name": "The Argent Dawn",
    "description": ("The order at Light's Hope that fights the Scourge without asking who its soldiers used to be. "
                    "Natives, transplants and a few Forsaken stand its walls."),
    "home_zone": "eastern_plaguelands_east",
    "home_name": "Light's Hope Chapel, Eastern Plaguelands",
    "leader": {
        "title": "Commander",
        "name": "Eligor Dawnbringer",
        "npc_id": "epl_lh_commander",
        "location": "Light's Hope Chapel",
        "line": ("We don't ask where you came from. We ask whether you'll stand on the wall tonight, and most people "
                 "say yes."),
    },
    "lore": [
        "The Argent Dawn was holding the line against the Scourge before the Integration, and it's still holding it. "
        "It takes anyone who'll stand on the wall, which these days means a lot of transplants.",
        "Light's Hope Chapel is the order's heart: a chapel on holy ground the dead can't cross, and the last place "
        "in the east where you can sleep without someone on watch.",
        "It trades in Scourgestones, the shards of necromancy the dead carry, and it pays well for them. It doesn't "
        "much like the Order of the Pale Flame, and it works with them every week.",
    ],
    "quest_rep": {
        "_comment": "Per quest, by shape. Matches the other factions' rates.",
        "default": 225,
        "boss": 250,
        "capstones": {},
        "zones": ["eastern_plaguelands_west", "eastern_plaguelands_east"],
    },
    "kill_rep": {
        "_comment": ["Scourge kills pay only while the Argent Dawn Commission is worn (built with Light's Hope's "
                     "people), so nothing is listed here."],
        "creatures": {},
    },
    "dungeon_rep": {
        "_comment": "A dungeon boss kill pays 75. Scholomance and Stratholme's undead half join when they exist.",
        "per_boss": 75,
        "dungeons": [],
    },
}


def main():
    raw = PATH.read_text(encoding="utf-8")
    d = json.loads(raw)
    fs = d["factions"]
    for fid, rec in (("pale_flame", PALE_FLAME), ("argent_dawn", ARGENT_DAWN)):
        old = fs.get(fid, {})
        merged = dict(rec)
        if "rewards" in old:
            merged["rewards"] = old["rewards"]
        fs[fid] = merged
    PATH.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"factions.json: The Order of the Pale Flame and the Argent Dawn ({len(fs)} factions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
