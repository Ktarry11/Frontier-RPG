#!/usr/bin/env python3
"""
The Felwood quest pass: South Felwood, Emerald Sanctuary, North Felwood and Jaedenar. Idempotent.

    PYTHONPATH=. python3 tools/build_felwood_quests.py

The text and the people are in tools/felwood_quests.py and tools/felwood_quest_kit.py. Writes
data/quests/felwood.json, the quest drops (data/creatures/quest_drops.json) and the Emerald
Reclamation's capstones (data/factions/factions.json).

RULES KEPT, and checked below before anything is written (the Tempest Isle pass's rules):
  - every creature named spawns where the quest says, every fetch item drops, every explore point is
    a tile you can walk to from the zone's entrance, and every turn-in person exists;
  - most givers stand in a hub (the Sanctuary or Talonbranch); none carries more than five;
  - dungeon quests are given in a hub, never inside;
  - ASCII, no counts beside an objective word, every kill target named in the text;
  - VOICE (Kyle): no sentence of one or two words, no dashes, contractions, none of the stiff
    constructions (tools/build_tempest_quests.voice_problems, the same check).
"""
import collections
import contextlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import felwood_quest_kit as K               # noqa: E402
from tools import felwood_quests as FQ                 # noqa: E402
from tools.build_tempest_quests import voice_problems  # noqa: E402

OUT = ROOT / "data/quests/felwood.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
FACTIONS = ROOT / "data/factions/factions.json"
RATE = 0.75
MAX_PER_GIVER = 5
#: The Reclamation's two capstones: the end of Jaedenar, and the turncoat.
CAPSTONES = {"fw_the_unbound": 500, "fw_voralith_the_turncloak": 350}

#: quest zone key -> (zone name, the map module, its generate function, an entrance tile or None)
MAPS = {
    K.SF: ("South Felwood", "tools.handbuilt_felwood_south", "generate_felwood_south", (76, 186)),
    K.NF: ("North Felwood", "tools.handbuilt_felwood_north", "generate_felwood_north", (70, 170)),
    K.ES: ("Emerald Sanctuary", "tools.handbuilt_emerald_sanctuary", None, None),
    K.JD: ("Jaedenar", "tools.handbuilt_jaedenar", "generate_jaedenar", None),
    K.RH: ("The Royal Hive", "tools.handbuilt_royal_hive", "generate_royal_hive", None),
    K.KV: ("Khaz Varun, the Black Hollow", "tools.handbuilt_khaz_varun", "generate_khaz_varun", None),
}


def _zones():
    """{key: (zone, reachable tiles or None, what spawns there)} for every zone a quest names."""
    import importlib
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    out = {}
    for key, (name, mod, gen, start) in MAPS.items():
        if gen is None:
            out[key] = (None, None, set())
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            z = getattr(importlib.import_module(mod), gen)()
        if start is None:
            start = next(((x, y) for (x, y, _n) in z.boss_positions if z.is_walkable(x, y)))
        seen, todo = {tuple(start)}, [tuple(start)]
        while todo:
            x, y = todo.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in seen and 0 <= nx < z.width and 0 <= ny < z.height and z.is_walkable(nx, ny):
                    seen.add((nx, ny))
                    todo.append((nx, ny))
        spawns = {n for (_x, _y, n) in (getattr(z, "boss_positions", None) or [])}
        spawns |= {m[2] for v in (getattr(z, "boss_pack", None) or {}).values() for m in v}
        spawns |= {m[2] for m in (getattr(z, "trash_spawns", None) or [])}
        if name in enc:
            spawns |= set(enc[name].get("open_zone", {}).get("creatures", {}))
            for t in enc[name].get("subzones", {}).values():
                spawns |= set(t["creatures"])
        out[key] = (z, seen, spawns)
    return out


def audit(quests, drop_rows):
    bad = []
    ids = {q["quest_id"] for q in quests}
    Z = _zones()
    npcs = {r["npc_id"]: r for r in json.loads((ROOT / "data/npcs/ambient_npcs.json")
                                                .read_text(encoding="utf-8"))["npcs"]}
    item_source = {iid: cre for (cre, iid) in drop_rows}
    givers = collections.Counter(q["giver_npc_id"] for q in quests if not q["giver_npc_id"].startswith("item:"))
    for g, n in givers.items():
        if n > MAX_PER_GIVER:
            bad.append(f"{g} gives {n} quests")
        if g not in npcs:
            bad.append(f"giver {g} doesn't exist")
    hub = sum(1 for q in quests if q["giver_npc_id"] in K.HUB_GIVERS)
    if hub < 0.9 * len(quests) - 4:
        bad.append(f"only {hub} of {len(quests)} quests are given in a hub")
    for q in quests:
        qid = q["quest_id"]
        text = " ".join(str(q.get(kk) or "") for kk in ("title", "description", "accept_text", "turn_in_text"))
        if not text.isascii():
            bad.append(f"{qid}: non-ASCII text")
        for key in ("accept_text", "turn_in_text", "description"):
            for p in voice_problems(q[key]):
                bad.append(f"{qid} {key}: {p}")
        if not q["giver_npc_id"].startswith("item:") and "'" not in q["accept_text"]:
            bad.append(f"{qid}: no contraction in the accept line")
        if q.get("turn_in_npc_id") and q["turn_in_npc_id"] not in npcs:
            bad.append(f"{qid}: turns in to {q['turn_in_npc_id']}, who doesn't exist")
        granted = {g["item_id"] for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        for o in q["objectives"]:
            t = o["type"]
            if t in ("kill", "kill_boss"):
                oz = o["zone"]
                if oz not in Z:
                    bad.append(f"{qid}: sends you to {oz}, which this pass can't check")
                elif o["target"] not in Z[oz][2]:
                    bad.append(f"{qid}: {o['target']} doesn't spawn in {oz}")
                if o["target"] not in text:
                    bad.append(f"{qid}: never names {o['target']}")
                if oz in (K.JD, K.RH, K.KV) and q["giver_npc_id"] not in K.HUB_GIVERS:
                    bad.append(f"{qid}: a dungeon quest that isn't given in a hub")
            if t == "fetch" and o["target"] not in item_source:
                bad.append(f"{qid}: fetches {o['target']}, which nothing drops")
            if t == "deliver" and o["target"] not in granted | set(item_source):
                bad.append(f"{qid}: delivers {o['target']}, which nothing grants or drops")
            if t == "explore":
                z, seen, _s = Z[o["target"]]
                if seen is not None and (o["target_x"], o["target_y"]) not in seen:
                    bad.append(f"{qid}: {o['label']} ({o['target_x']},{o['target_y']}) is not a tile you can walk to")
        for nx in [q.get("next_quest_id")] + list(q.get("requires_quests") or []):
            if nx and nx not in ids:
                bad.append(f"{qid}: refers to {nx}, which this pass doesn't define")
        if re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+"
                     r"(wolf|wolves|imp|imps|treant|treants|hound|hounds|sentr\w+|felguard|bear|bears|stag|"
                     r"stags|boar|boars|ooze|oozes|satyr\w*|rogue\w*|trickster\w*|warrior\w*|watcher\w*|"
                     r"shaman\w*|splinter\w*|pelt\w*|antler\w*|gland\w*|fetish\w*|sample\w*|claw\w*|"
                     r"keystone\w*|hinge\w*|page\w*)\b", text, re.I):
            bad.append(f"{qid}: a count in the prose beside an objective word")
    return bad


def main():
    qs = FQ.build()
    rows = []
    for cre, rr in FQ.FETCH_DROPS.items():
        for r in rr:
            rows.append((cre, r[0], r[1], r[2], r[3] if len(r) > 3 else RATE, None))
    for cre, rr in FQ.STARTER_DROPS.items():
        for (iid, nm, desc, ch) in rr:
            rows.append((cre, iid, nm, desc, ch, FQ.STARTER_IDS[iid]))
    ids = [q["quest_id"] for q in qs]
    if len(set(ids)) != len(ids):
        print("FAILED: duplicate quest ids")
        return 1
    bad = audit(qs, [(r[0], r[1]) for r in rows])
    if bad:
        print(f"\nFAILED ({len(bad)}) - fix the quests, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    OUT.write_text(json.dumps({"quests": qs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for cre, iid, nm, desc, ch, starts in rows:
        have = {r["item_id"]: r for r in drops.get(cre, [])}
        rec = {"item_id": iid, "name": nm, "category": "quest", "description": desc, "chance": ch}
        if starts:
            rec["starts_quest_id"] = starts
        have[iid] = rec
        drops[cre] = list(have.values())
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fd = json.loads(FACTIONS.read_text(encoding="utf-8"))
    fd["factions"]["emerald_reclamation"]["quest_rep"]["capstones"] = CAPSTONES
    FACTIONS.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)

    by_zone = collections.Counter(q["zone"] for q in qs)
    kinds = collections.Counter(o["type"] for q in qs for o in q["objectives"])
    hub = sum(1 for q in qs if q["giver_npc_id"] in K.HUB_GIVERS)
    print(f"{len(qs)} quests {dict(by_zone)}; {hub} given in a hub; objectives {dict(kinds)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
