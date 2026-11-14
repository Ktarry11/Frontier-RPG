#!/usr/bin/env python3
"""The Royal Hive's quests, given in Onyxhollow. Idempotent. 54-56.

    PYTHONPATH=. python3 tools/build_royal_hive_quests.py

Dungeon quests are given in town (standing rule), and the hive is under Onyxhollow's own cavern,
so the five people who have reason to care about it give one each: the Thane, whose queen quest
it follows on from; the Gate-Captain; the geomancer, whose pillars are being eaten; the
Forgemaster, who wants the resin; and the Ashkeeper, who wants the nursery shut.

Written plain (Kyle, 13 Nov 2026: "NO ONE talks like this"): what's wrong, where to go, what to
bring back, and a turn-in that thanks you and stops.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                                      # noqa: E402
from tools.tempest_quest_kit import Q, boss, explore, fetch           # noqa: E402
from tools.build_tempest_quests import voice_problems                 # noqa: E402

OUT = ROOT / "data/quests/royal_hive.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
RH = "the_royal_hive"
BS = "the_black_strand"
THANE, YRSA, VIGDIS = "oh_thane", "oh_gate_captain", "oh_geomancer"
GARRUN, TORVALD = "oh_forgemaster", "oh_shrine_keeper"

tirisfal_gear.THEMES.update({
    "royalhive": (["Royal-Hive", "Consort's", "Resin-Sealed", "Broodward", "Hivebane"],
                  ["Cut from silithid chitin and riveted in Onyxhollow.",
                   "There's a seam of amber resin set into it.",
                   "It came up out of the Royal Hive in someone's pack.",
                   "Forged in Onyxhollow from what the hive left behind."]),
})

FETCH_DROPS = {
    "Resin Weaver": [("rh_royal_resin", "Royal Resin",
                      "Clear amber resin, still soft. It hardens in a few hours.")],
}


def build():
    q = []
    q.append(Q("rh_under_the_cell", "Under the Cell", THANE, 55, 56, "royalhive",
               "Go down through the floor of the Royal Cell and kill Hive-Mother Ahn'thera and "
               "Royal Consort Zhir'ak in the Royal Chamber.",
               [boss("Hive-Mother Ahn'thera", RH)],
               "The queen you killed in the Royal Cell wasn't the only one. The digging under "
               "the wall started again three days later.\n\nVigdis put her ear to the floor of "
               "the cell and heard more hive underneath. There's a way down at the narrow end of "
               "the cell, behind the throne. Whatever raised Zil'kesh is down there, and the "
               "scouts I sent say there are two of them, a queen and the one that guards "
               "her.\n\nThe Royal Cell is in the far south-east of the cavern, through the back "
               "of the Chitin Reach. Go down and kill them both. Hive-Mother Ahn'thera is the "
               "queen.",
               "Then the hive has nobody left to lead it.\n\nThe digging stopped this morning. "
               "I had Rurik sit by the wall all night to be sure. Thank you. Take what Aldis has "
               "put aside for you.",
               zone=RH, requires_quests=["bst_the_royal_cell"]))

    q.append(Q("rh_the_warden", "The Warden at the Door", YRSA, 54, 54, "royalhive",
               "Kill Hive-Warden Kasz'ar in the Drone Galleries of the Royal Hive.",
               [boss("Hive-Warden Kasz'ar", RH)],
               "Before anyone goes deeper into that hive, the thing guarding its first chamber "
               "has to go.\n\nMy scouts got as far as the Drone Galleries, the big chamber just "
               "past the way in. Something with a shell like a wall stands in the middle of it, "
               "and the drones gather round it. They call it Hive-Warden Kasz'ar.\n\nThe way in "
               "is the hole at the narrow end of the Royal Cell, in the far south-east of the "
               "cavern. Be ready for its shell to close up when it's hurt.",
               "That means my scouts can get further in now.\n\nThank you. This is from the gate "
               "stores.",
               zone=RH))

    q.append(Q("rh_eating_the_pillars", "What's Under the Pillars", VIGDIS, 55, 55, "royalhive",
               "Find the Deep Burrows in the Royal Hive and kill Tunnel-King Ruzzak.",
               [explore(52, 112, "the Deep Burrows in the Royal Hive", RH),
                boss("Tunnel-King Ruzzak", RH)],
               "Three of the pillars holding up the cavern roof have been bored hollow from "
               "underneath.\n\nThe borings run down into the Royal Hive, to a chamber the scouts "
               "call the Deep Burrows. Something big is digging there, and I think it's going "
               "for the pillars on purpose. They call it Tunnel-King Ruzzak.\n\nGo down through "
               "the Royal Cell, in the far south-east of the cavern, and through the hive to the "
               "Deep Burrows. When it burrows, stop hitting it until it comes back up. It "
               "turns the blows into shell.",
               "The pillars have stopped ringing hollow.\n\nThat's the first good news I've had "
               "about the roof since the ground shook three years ago. Thank you.",
               zone=RH))

    q.append(Q("rh_amber_for_the_forge", "Resin for the Forge", GARRUN, 54, 54, "royalhive",
               "Collect Royal Resin from the Resin Weavers in the Royal Hive.",
               [fetch("rh_royal_resin", 6)],
               "Hive resin sets harder than glass and doesn't crack in the heat, and I want to "
               "try it as a lining for the crucibles.\n\nThe Resin Weavers in the Royal Hive "
               "make it fresh. The ones on the edge of the Strand only carry the old stuff. Go "
               "down through the Royal Cell in the far south-east of the cavern and take the "
               "resin off the Weavers inside.\n\nBring it back soft, before it sets.",
               "It's still soft, which is what I needed.\n\nI'll line a crucible with it tonight and see how it "
               "holds. Here, this came off my anvil last week.",
               zone=RH))

    q.append(Q("rh_the_nursery", "The Nursery", TORVALD, 54, 55, "royalhive",
               "Kill The Brood Nurse in the Brood Chambers of the Royal Hive.",
               [boss("The Brood Nurse", RH)],
               "The scouts found the room where the hive raises its young, off to the west of "
               "the Drone Galleries.\n\nThere's a creature in there that tends the eggs and "
               "feeds the larvae. If it lives, the hive will grow back whatever we do to it. "
               "The scouts call it The Brood Nurse.\n\nGo down through the Royal Cell in the "
               "far south-east of the cavern, and take the side tunnel west from the first big "
               "chamber. Kill the larvae when she wakes them, or they'll keep her alive.",
               "Then nothing new will hatch down there.\n\nThe hive has taken miners from this town "
               "every year since the ground shook three years ago. I'll light the shrine for "
               "them tonight. Thank you for doing this.",
               zone=RH))
    return q


def main():
    quests = build()
    bad = []
    for q in quests:
        for key in ("accept_text", "turn_in_text", "description"):
            bad += [f"{q['quest_id']} {key}: {p}" for p in voice_problems(q[key])]
        if not q["accept_text"].isascii() or not q["turn_in_text"].isascii():
            bad.append(f"{q['quest_id']}: non-ASCII text")
        for o in q["objectives"]:
            if o["type"] == "kill_boss" and o["target"] not in q["accept_text"]:
                bad.append(f"{q['quest_id']}: never names {o['target']}")
    if bad:
        print("FAILED:")
        for b in bad:
            print("  -", b)
        return 1
    OUT.write_text(json.dumps({"quests": quests}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    for cre, rows in FETCH_DROPS.items():
        have = {r["item_id"]: r for r in dd["drops"].get(cre, [])}
        for iid, nm, desc in rows:
            have[iid] = {"item_id": iid, "name": nm, "category": "quest", "description": desc,
                         "chance": 0.75}
        dd["drops"][cre] = list(have.values())
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True,
                   stdout=subprocess.DEVNULL)
    print(f"{len(quests)} Royal Hive quests -> {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
