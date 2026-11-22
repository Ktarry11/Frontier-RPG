"""QA guard for the towns' people (22 Nov 2026).

Kyle, 22 Nov 2026, on how many people a town needs: "Small towns can be 15-20, medium can be 25-30, and capitals can be
50+", counted on top of the quest givers, trainers and services ("Nope that's perfect!"). Then: "Ensure they're spread
out within reason, some clumps are logical but not a big mass of 50 people." And on openers: "Does every npc start
with 'I do x'", after which no town's townsfolk may open more than about a third of their lines with "I".

Three checks, run from tools/qa_quest_overhaul.py so they can't slip back:
  1. every town in tools/build_townsfolk.py TOWNS has at least its tier's floor of residents
  2. no 8x8 patch of a town holds more than CLUMP_CAP people (everyone standing there, residents or not)
  3. no townsfolk file opens more than a third of its lines with "I"

    PYTHONPATH=. python3 tools/qa_townsfolk.py        prints the table and any findings
"""
import collections
import glob
import importlib.util
import json
import os
import re
import sys

sys.path.insert(0, ".")
from world.zone_keys import zone_key  # noqa: E402

FLOOR = {"small": 15, "mid": 25, "capital": 50}
CAPITALS = {"Orgrimmar", "Undercity", "Aurelion", "Timbermaw Hold", "The Great Settlement"}
MID = {"Brill", "Crossroads", "Ratchet", "Tarren Mill", "Booty Bay", "Freewind Post", "Steamwheedle Port",
       "Onyxhollow", "Firstlight Spire", "Hammerfall", "Light's Hope Chapel", "The Bulwark", "Cinderwharf"}
# Spearhold is a war camp on the Sunward Crown's approach, not a town anyone lives in: a handful by the fires.
OWN_FLOOR = {"Spearhold": 5}
CLUMP_CAP = 6
OPENER_CAP = 1 / 3


def tier(name):
    return "capital" if name in CAPITALS else "mid" if name in MID else "small"


def _towns():
    src = open("tools/build_townsfolk.py", encoding="utf-8").read()
    body = re.search(r"^TOWNS\s*=\s*\{(.*?)^\}", src, re.M | re.S).group(1)
    return re.findall(r'"(\w+)": "([^"]+)"', body)


def _people(stem):
    spec = importlib.util.spec_from_file_location("tf_" + stem, f"tools/townsfolk/{stem}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.PEOPLE


def _non_residents():
    svc = set(json.load(open("data/travel/travel_data.json", encoding="utf-8"))["services"])
    tr = json.load(open("data/training/trainers.json", encoding="utf-8"))
    out = svc | set(tr.get("class_trainers", {})) | set(tr.get("profession_trainers", {}))
    for f in glob.glob("data/quests/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        for q in (d.get("quests") if isinstance(d, dict) else None) or []:
            out |= {q.get("giver_npc_id"), q.get("turn_in_npc_id")}
    return out


def findings(verbose=False):
    amb = json.load(open("data/npcs/ambient_npcs.json", encoding="utf-8"))["npcs"]
    ven = json.load(open("data/npcs/vendors.json", encoding="utf-8"))["vendors"]
    skip = _non_residents()
    residents = collections.Counter()
    pos = collections.defaultdict(list)
    for n in amb:
        i = n["npc_id"]
        if not (i in skip or n.get("is_mailbox") or i.startswith(("secret_", "ct_", "pt_", "ak_", "mailbox"))):
            residents[zone_key(str(n["zone"]))] += 1
    for n in amb + ven:
        if n.get("x") is not None and not n.get("is_mailbox"):
            pos[zone_key(str(n["zone"]))].append((n["x"], n["y"]))
    bad = []
    seen = set()
    for stem, name in _towns():
        if name in seen:
            continue
        seen.add(name)
        z = zone_key(name)
        floor = OWN_FLOOR.get(name, FLOOR[tier(name)])
        got = residents[z]
        P = pos[z]
        clump = max((sum(1 for (a, b) in P if 0 <= a - x < 8 and 0 <= b - y < 8) for (x, y) in P), default=0)
        lines = [p[5] for p in _people(stem)]
        opens = sum(1 for g in lines if re.match(r"I\b|I'", g))
        if verbose:
            print(f"  {name:28s} {tier(name):8s} residents {got:3d} (floor {floor:2d})  clump {clump}  "
                  f"'I' openers {opens}/{len(lines)}")
        if got < floor:
            bad.append(f"townsfolk: {name} has {got} residents, its floor is {floor}")
        if clump > CLUMP_CAP:
            bad.append(f"townsfolk: {name} has {clump} people in one 8x8 patch (cap {CLUMP_CAP})")
        if lines and opens > len(lines) * OPENER_CAP:
            bad.append(f"townsfolk: {stem}.py opens {opens} of {len(lines)} lines with 'I'")
    return bad


if __name__ == "__main__":
    b = findings(verbose=True)
    for x in b:
        print("  -", x)
    print("townsfolk OK" if not b else f"{len(b)} townsfolk problem(s)")
    sys.exit(1 if b else 0)
