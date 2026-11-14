#!/usr/bin/env python3
"""
The Tempest Isle quest pass: Tempest Shallows, the Ashen Reach, Cinderwharf and both dungeons.
Idempotent. 52-58.

    PYTHONPATH=. python3 tools/build_tempest_quests.py

Kyle, 13 Nov 2026: "Lets finish tempest isle first", in the order loot, then mobs, then quests.

SIXTY-SEVEN QUESTS in two files: data/quests/tempest_shallows.json (35) and
data/quests/ashen_reach.json (32). The text lives in tools/tempest_quests_shallows.py and
tools/tempest_quests_reach.py; the people in tools/tempest_npc_roster.py.

RULES KEPT, and checked below before anything is written:
  - every creature named spawns where the quest says, every fetch item drops (three in four),
    every explore point is a tile you can walk to from the zone's entrance;
  - no giver carries more than three; dungeon quests are given in town;
  - nobody is sent to the subzone they are standing in without a named far point to go to;
  - ASCII, no counts beside an objective word, every kill target named in the text;
  - VOICE (Kyle, same day): "the single word sentences... no one talks like this". No sentence of
    one or two words, no dashes, contractions, none of the stiff constructions.
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

from tools import tempest_quest_kit as K              # noqa: E402
from tools import tempest_quests_shallows as SH       # noqa: E402
from tools import tempest_quests_reach as RE          # noqa: E402

DROPS = ROOT / "data/creatures/quest_drops.json"
FACTIONS = ROOT / "data/factions/factions.json"
FILES = [("tempest_shallows", SH), ("ashen_reach", RE)]
RATE = 0.75
#: The two ends of the island. Standing for these matches the other factions' capstones.
CAPSTONES = {"tmp_thane_morrun": 500, "tmp_the_deep_claim": 500}

TICS = {
    "it is not X, it is Y": re.compile(
        r"\b(is|was|are) not (a|an|the)? ?[\w' ]{2,40}[.,;:] (it|that|this|they) (is|was|are)\b", re.I),
    "no contraction": re.compile(
        r"\b(I am|do not|does not|did not|it is|that is|you will|I will|cannot|I have|"
        r"is not|was not|are not|will not|would not|could not|have not|there is) \w"),
    "dash": re.compile(r" - |—|--"),
    "filler": re.compile(r"which is to say|in other words|take your pick|thank you,? (friend|stranger)",
                         re.I),
    "kill N of X": re.compile(r"\b(kill|slay|cull|thin)\s+(a\s+)?(dozen|\d+|ten|twelve|eight|six)\b",
                              re.I),
}
_ABBR = re.compile(r"\b(Dr|Mr|Mrs|St|MV)\.")


def fragments(text):
    """Sentences of one or two words. 'Stay. I'm asking.' is the thing Kyle named."""
    out = []
    flat = _ABBR.sub(lambda m: m.group(1), text.replace("\n", " "))
    for s in re.split(r"(?<=[.!?])['\"]?\s+", flat):
        words = re.findall(r"[A-Za-z0-9'][\w'-]*", s)
        if 0 < len(words) < 3:
            out.append(s.strip())
    return out


def voice_problems(text):
    bad = [f"{name}: '{m.group(0)}'" for name, rx in TICS.items() if (m := rx.search(text))]
    bad += [f"fragment: '{f}'" for f in fragments(text)]
    return bad


def _zones():
    """The live maps, the tiles reachable from each entrance, and what spawns where."""
    with contextlib.redirect_stdout(io.StringIO()):
        import tools.handbuilt_tempest_shallows as a
        import tools.handbuilt_ashen_reach as b
        import tools.handbuilt_khaz_varun as c
        import tools.handbuilt_emberdeep as d
        maps = {K.TS: (a.generate_tempest_shallows(), a.START),
                K.AR: (b.generate_ashen_reach(), b.NPC_POSITIONS["ar_gate_factor"]),
                K.KV: (c.generate_khaz_varun(), None),
                K.ED: (d.generate_emberdeep(), None)}
    out = {}
    for key, (z, start) in maps.items():
        if start is None:
            start = next(((x, y) for (x, y, _n) in z.boss_positions if z.is_walkable(x, y)))
        seen, todo = {tuple(start)}, [tuple(start)]
        while todo:
            x, y = todo.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in seen and 0 <= nx < z.width and 0 <= ny < z.height \
                        and z.is_walkable(nx, ny):
                    seen.add((nx, ny))
                    todo.append((nx, ny))
        spawns = {n for (_x, _y, n) in (getattr(z, "boss_positions", None) or [])}
        spawns |= {n for (_x, _y, n, _l) in (getattr(z, "trash_spawns", None) or [])}
        out[key] = (z, seen, spawns)
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    for key, name in ((K.TS, "Tempest Shallows"), (K.AR, "The Ashen Reach")):
        z, seen, spawns = out[key]
        spawns |= set(enc[name]["open_zone"]["creatures"])
        where = {}
        for sub, t in enc[name]["subzones"].items():
            spawns |= set(t["creatures"])
            for c in t["creatures"]:
                where[c] = sub
        out[key] = (z, seen, spawns, where)
    return out


def _inside(zone, sub_name, x, y):
    for s in zone.subzones:
        if s["name"] == sub_name:
            return s["x"] <= x < s["x"] + s["w"] and s["y"] <= y < s["y"] + s["h"]
    return False


def audit(quests, drops_by_item):
    bad = []
    ids = {q["quest_id"] for q in quests}
    Z = _zones()
    pos = {}
    with contextlib.redirect_stdout(io.StringIO()):
        import tools.handbuilt_tempest_shallows as a
        import tools.handbuilt_ashen_reach as b
    for key, M in ((K.TS, a), (K.AR, b)):
        for nid, xy in M.NPC_POSITIONS.items():
            pos[nid] = (key, xy)
    item_source = {iid: cre for cre, iid in drops_by_item}

    givers = collections.Counter(q["giver_npc_id"] for q in quests
                                 if not q["giver_npc_id"].startswith("item:"))
    for g, n in givers.items():
        if n > 3:
            bad.append(f"{g} gives {n} quests")

    for q in quests:
        qid = q["quest_id"]
        text = " ".join(str(q.get(kk) or "") for kk in ("title", "description", "accept_text",
                                                         "turn_in_text"))
        if not text.isascii():
            bad.append(f"{qid}: non-ASCII text")
        for key in ("accept_text", "turn_in_text", "description"):
            for p in voice_problems(q[key]):
                bad.append(f"{qid} {key}: {p}")
        if not q["giver_npc_id"].startswith("item:") and "'" not in q["accept_text"]:
            bad.append(f"{qid}: no contraction in the accept line")
        granted = {g["item_id"] for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        gz, gxy = pos.get(q["giver_npc_id"], (None, None))
        has_far_point = any(o["type"] == "explore" for o in q["objectives"])
        for o in q["objectives"]:
            t = o["type"]
            if t in ("kill", "kill_boss"):
                oz = o["zone"]
                if o["target"] not in Z[oz][2]:
                    bad.append(f"{qid}: {o['target']} does not spawn in {oz}")
                if o["target"] not in text:
                    bad.append(f"{qid}: never names {o['target']}")
                if oz in (K.KV, K.ED) and q["zone"] != K.CW and q["giver_npc_id"] != K.KENJI:
                    bad.append(f"{qid}: a dungeon quest that is not given in town")
                # nobody is sent to the ground they are standing on
                if gz == oz and len(Z[oz]) > 3 and not has_far_point:
                    sub = Z[oz][3].get(o["target"])
                    if sub and _inside(Z[oz][0], sub, *gxy) and q["giver_npc_id"] != K.BRON \
                            and q["giver_npc_id"] not in K.HUB_GIVERS:
                        bad.append(f"{qid}: {q['giver_npc_id']} stands in {sub}, where "
                                   f"{o['target']} is")
            if t == "fetch":
                if o["target"] not in item_source:
                    bad.append(f"{qid}: fetches {o['target']}, which nothing drops")
            if t == "deliver" and o["target"] not in granted | set(item_source):
                bad.append(f"{qid}: delivers {o['target']}, which nothing grants or drops")
            if t == "explore":
                seen = Z[o["target"]][1]
                if (o["target_x"], o["target_y"]) not in seen:
                    bad.append(f"{qid}: {o['label']} is not a tile you can walk to")
        for nx in [q.get("next_quest_id")] + list(q.get("requires_quests") or []):
            if nx and nx not in ids:
                bad.append(f"{qid}: refers to {nx}, which this pass does not define")
        if re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+"
                     r"(raptor|panther|gorilla|brawler|ashpreacher|basilisk|spirit|scorpion|whelp|"
                     r"snapper|crab|murloc|raider|ooze|elemental|drake|claw|tablet|stone|cask|"
                     r"hook|membrane|hide|gland|mask|pouch)s?\b", text, re.I):
            bad.append(f"{qid}: a count in the prose beside an objective word")
    return bad


def main():
    built, all_q, rows = [], [], []
    for stem, M in FILES:
        qs = M.build()
        built.append((stem, qs))
        all_q += qs
        for cre, rr in M.FETCH_DROPS.items():
            for r in rr:
                rows.append((cre, r[0], r[1], r[2], r[3] if len(r) > 3 else RATE, None))
        for cre, rr in M.STARTER_DROPS.items():
            for (iid, nm, desc, ch) in rr:
                rows.append((cre, iid, nm, desc, ch, M.STARTER_IDS[iid]))
    ids = [q["quest_id"] for q in all_q]
    if len(set(ids)) != len(ids):
        print("FAILED: duplicate quest ids")
        return 1
    for (_c, iid, _n, _d, _ch, starts) in rows:
        if starts and starts not in ids:
            print(f"FAILED: {iid} starts {starts}, which does not exist")
            return 1
    bad = audit(all_q, [(r[0], r[1]) for r in rows])
    if bad:
        print(f"\nFAILED ({len(bad)}) - fix the quests, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    for stem, qs in built:
        (ROOT / f"data/quests/{stem}.json").write_text(
            json.dumps({"quests": qs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
    fd["factions"]["the_ashclaim"]["quest_rep"]["capstones"] = CAPSTONES
    FACTIONS.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True,
                   stdout=subprocess.DEVNULL)

    hub = sum(1 for q in all_q if q["giver_npc_id"] in K.HUB_GIVERS)
    starters = sum(1 for q in all_q if q["giver_npc_id"].startswith("item:"))
    print(f"{len(all_q)} quests ({', '.join(f'{s} {len(q)}' for s, q in built)}): {hub} from the "
          f"landing, the Works and Cinderwharf, {starters} started by a drop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
