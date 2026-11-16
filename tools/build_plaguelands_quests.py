#!/usr/bin/env python3
"""
The Plaguelands quest pass. Idempotent.

    PYTHONPATH=. python3 tools/build_plaguelands_quests.py

One content module a map (tools/plaguelands_quests_<part>.py), one quest file a map
(data/quests/plaguelands_<part>.json). Also writes the quest drops (data/creatures/quest_drops.json) and the
reputation by giver (data/factions/factions.json, each faction's "also" list).

The rules are the Stonetalon pass's, shared with the Monastery's (tools/build_scarlet_monastery_quests.py) and checked
before anything is written: every creature named spawns where the quest says, every fetch item drops, every giver and
turn-in person exists, givers stand in hubs and give no more than five, the voice rules, chains are chains, reward
names are new to the game, and each map's rewards give every one of the 97 specs something it can wear and wants.
"""
import collections
import contextlib
import importlib
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from tools import build_scarlet_monastery_quests as SMB   # noqa: E402
from tools.build_tempest_quests import voice_problems      # noqa: E402

DROPS = ROOT / "data/creatures/quest_drops.json"
FACTIONS = ROOT / "data/factions/factions.json"
NPCS = ROOT / "data/npcs/ambient_npcs.json"
RATE = 0.75
MAX_PER_GIVER = 5

#: part -> (content module, quest id prefix, item id prefix, the zone's own faction, the level the chain ends at)
PARTS = {
    "south": ("tools.plaguelands_quests_south", "pls_", "plsq_", "pale_flame", 54),
    "north": ("tools.plaguelands_quests_north", "pln_", "plnq_", "pale_flame", 56),
    "epl_west": ("tools.plaguelands_quests_epl_west", "plw_", "plwq_", "argent_dawn", 58),
    "epl_east": ("tools.plaguelands_quests_epl_east", "ple_", "pleq_", "argent_dawn", 60),
}

#: quest zone key -> (map module, start attribute, encounter zone)
MAPS = {
    "western_plaguelands_south": ("tools.handbuilt_wpl_south", "START", "Western Plaguelands South"),
    "western_plaguelands_north": ("tools.handbuilt_wpl_north", "START", "Western Plaguelands North"),
    "eastern_plaguelands_west": ("tools.handbuilt_epl_west", "START", "Eastern Plaguelands West"),
    "eastern_plaguelands_east": ("tools.handbuilt_epl_east", "START", "Eastern Plaguelands East"),
}

XP = lambda lvl: 80 * lvl - 360        # noqa: E731  (the Stonetalon scale carried on)
GOLD = lambda lvl: 300 * lvl - 600     # noqa: E731


def _zones():
    from tools import ashenvale_engine as E
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    out = {}
    for key, (mod, start, ez) in MAPS.items():
        with contextlib.redirect_stdout(io.StringIO()):
            m = importlib.import_module(mod)
            L = m.build_layout()
        _n, _w, seen = E.reachable_report(L, getattr(m, start))
        t = enc[ez]
        spawns = set(t["open_zone"]["creatures"])
        for s in t["subzones"].values():
            spawns |= set(s["creatures"])
        out[key] = (seen, spawns)
    return out


def taken_names(own_files):
    """Every gear name already in the game, so a quest reward never shares one."""
    names = set()

    def walk(x):
        if isinstance(x, dict):
            if "name" in x and ("slot" in x or "armor_type" in x or "weapon_type" in x):
                names.add(x["name"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for f in sorted((ROOT / "data/items").glob("*.json")) + sorted((ROOT / "data/quests").glob("*.json")):
        if f.name in own_files:
            continue
        try:
            walk(json.loads(f.read_text(encoding="utf-8")))
        except ValueError:
            pass
    return names


def audit(QM, quests, drop_rows, Z, npcs):
    bad = []
    item_names = {r[0]: r[1] for rr in QM.FETCH_DROPS.values() for r in rr}
    ids = {q["quest_id"] for q in quests}
    item_source = {iid for (_cre, iid) in drop_rows}
    givers = collections.Counter(q["giver_npc_id"] for q in quests)
    for g, n in givers.items():
        if n > MAX_PER_GIVER:
            bad.append(f"{g} gives {n} quests")
        if g not in npcs:
            bad.append(f"giver {g} doesn't exist")
    hub = sum(1 for q in quests if q["giver_npc_id"] in QM.HUB_GIVERS)
    if hub < 0.8 * len(quests):
        bad.append(f"only {hub} of {len(quests)} quests are given in a hub")
    for cre, _iid in drop_rows:
        if not any(cre in sp for (_s, sp) in Z.values()):
            bad.append(f"{cre} carries a quest item and spawns nowhere in the Plaguelands")
    for q in quests:
        qid = q["quest_id"]
        text = " ".join(str(q.get(kk) or "") for kk in ("title", "description", "accept_text", "turn_in_text"))
        if not text.isascii():
            bad.append(f"{qid}: non-ASCII text")
        for key in ("accept_text", "turn_in_text", "description"):
            for p in voice_problems(q[key]):
                bad.append(f"{qid} {key}: {p}")
        if "'" not in q["accept_text"]:
            bad.append(f"{qid}: no contraction in the accept line")
        if q.get("turn_in_npc_id") and q["turn_in_npc_id"] not in npcs:
            bad.append(f"{qid}: turns in to {q['turn_in_npc_id']}, who doesn't exist")
        if q["giver_npc_id"] in getattr(QM, "NATIVE_GIVERS", ()) and re.search(r"\bEarth\b", text):
            bad.append(f"{qid}: a native says Earth")
        granted = {g["item_id"] for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        for o in q["objectives"]:
            t = o["type"]
            if t in ("kill", "kill_boss"):
                oz = o["zone"]
                if oz not in Z:
                    bad.append(f"{qid}: sends you to {oz}, which this pass can't check")
                elif o["target"] not in Z[oz][1]:
                    bad.append(f"{qid}: {o['target']} doesn't spawn in {oz}")
                if o["target"] not in text:
                    bad.append(f"{qid}: never names {o['target']}")
            if t == "fetch" and o["target"] not in item_source:
                bad.append(f"{qid}: fetches {o['target']}, which nothing drops")
            if t == "deliver" and o["target"] not in granted:
                bad.append(f"{qid}: delivers {o['target']}, which nothing grants")
            if t == "explore":
                seen, _s = Z[o["target"]]
                if (o["target_x"], o["target_y"]) not in seen:
                    bad.append(f"{qid}: {o['label']} ({o['target_x']},{o['target_y']}) is not a tile you can walk to")
        for nx in [q.get("next_quest_id")] + list(q.get("requires_quests") or []):
            if nx and nx not in ids:
                bad.append(f"{qid}: refers to {nx}, which this pass doesn't define")
        # no counts in the prose beside the words the objectives use (the target's last word, singular or plural)
        words = set()
        for o in q["objectives"]:
            name = item_names.get(o["target"], o["target"]) if o["type"] in ("fetch", "deliver") else o["target"]
            if o["type"] != "explore":
                words.add(re.sub(r"(es|s)$", "", name.split()[-1].lower()))
        if words and re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+(\w+\s+)?("
                               + "|".join(re.escape(w) for w in words) + r")\w*\b", text, re.I):
            bad.append(f"{qid}: a count in the prose beside an objective word")
    return bad


def build_part(part, Z, npcs, fd, dd, built, used):
    mod, qprefix, iprefix, home_faction, top = PARTS[part]
    QM = importlib.import_module(mod)
    qs = QM.build()
    ids = [q["quest_id"] for q in qs]
    bad = []
    if len(set(ids)) != len(ids):
        bad.append(f"duplicate quest ids {[i for i, n in collections.Counter(ids).items() if n > 1]}")
    bad += [f"{i} doesn't start with {qprefix}" for i in ids if not i.startswith(qprefix)]
    by = {q["quest_id"]: q for q in qs}
    for q in qs:
        nx = q.get("next_quest_id")
        if nx and nx in by:
            req = by[nx].setdefault("requires_quests", [])
            if q["quest_id"] not in req:
                req.append(q["quest_id"])
    rows = []
    for cre, rr in QM.FETCH_DROPS.items():
        for r in rr:
            rows.append((cre, r[0], r[1], r[2], r[3] if len(r) > 3 else RATE))
    bad += audit(QM, qs, [(r[0], r[1]) for r in rows], Z, npcs)

    all_items = []
    for q in qs:
        items, ilvl, rarity, b = SMB.author_rewards(q, used, rid_prefix=iprefix)
        bad += b
        is_boss = any(o["type"] == "kill_boss" for o in q["objectives"])
        mult = 1.5 if q.get("elite") else (1.3 if is_boss else 1.0)
        q["reward_exp"] = int(XP(q["level_max"]) * mult)
        q["reward_gold"] = int(GOLD(q["level_max"]) * mult)
        q["unique_item_defs"] = items
        q["gear_reward_gear_level"] = ilvl
        q["gear_reward_rarity"] = rarity
        q.pop("_prefix", None)
        q.pop("_rewards", None)
        all_items += items
    sb, fewest, nspecs, nclasses = SMB.spec_audit(all_items, level=top)
    bad += sb
    if bad:
        print(f"\n{part}: FAILED ({len(bad)}) - fix the quests, not the check:")
        for b in bad:
            print(f"  - {b}")
        return False

    built[part] = qs
    drops = dd["drops"]
    for cre, iid, nm, desc, ch in rows:
        have = {r["item_id"]: r for r in drops.get(cre, [])}
        have[iid] = {"item_id": iid, "name": nm, "category": "quest", "description": desc, "chance": ch}
        drops[cre] = list(have.values())
    pay = collections.Counter()
    for f in fd["factions"].values():
        qr = f.get("quest_rep")
        if qr and "also" in qr:
            qr["also"] = [x for x in qr["also"] if not x.startswith(qprefix)]
    for q in qs:
        fid = (getattr(QM, "FACTION_BY_QUEST", {}).get(q["quest_id"])
               or QM.FACTION_BY_GIVER.get(q["giver_npc_id"], home_faction))
        fd["factions"][fid].setdefault("quest_rep", {}).setdefault("also", []).append(q["quest_id"])
        pay[fid] += 1

    kinds = collections.Counter(o["type"] for q in qs for o in q["objectives"])
    hub = sum(1 for q in qs if q["giver_npc_id"] in QM.HUB_GIVERS)
    gated = sum(1 for q in qs if q.get("requires_quests"))
    away = sum(1 for q in qs if q.get("turn_in_npc_id") and npcs[q["turn_in_npc_id"]].get("zone") not in MAPS)
    print(f"{part}: {len(qs)} quests, {hub} given in a hub, {gated} unlocked by earlier quests, "
          f"{away} handed in outside the Plaguelands")
    print(f"  objectives {dict(kinds)}")
    print(f"  reputation {dict(pay)}")
    print(f"  {len(all_items)} rewards for {nspecs} specs of {nclasses} classes (fewest any spec gets: {fewest})")
    return True


def main():
    only = list(PARTS)          # always all of them, in order, so reward names come out the same every run
    used = taken_names({f"plaguelands_{p}.json" for p in PARTS})
    Z = _zones()
    npcs = {r["npc_id"]: r for r in json.loads(NPCS.read_text(encoding="utf-8"))["npcs"]}
    fd = json.loads(FACTIONS.read_text(encoding="utf-8"))
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    built = {}
    ok = all([build_part(p, Z, npcs, fd, dd, built, used) for p in only])
    # no more than five quests a person across the whole game, counting every file this pass doesn't write
    mine = {f"plaguelands_{p}.json" for p in PARTS}
    givers = collections.Counter(q["giver_npc_id"] for qs in built.values() for q in qs)
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        if f.name in mine:
            continue
        qs = json.loads(f.read_text(encoding="utf-8")).get("quests", [])
        for q in (qs if isinstance(qs, list) else list(qs.values())):
            if isinstance(q, dict) and q.get("giver_npc_id") in givers:
                givers[q["giver_npc_id"]] += 1
    over = {g: n for g, n in givers.items() if n > MAX_PER_GIVER}
    if over:
        print(f"FAILED: givers with more than {MAX_PER_GIVER} quests across the game: {over}")
        ok = False
    if not ok:
        return 1
    for p, qs in built.items():
        (ROOT / f"data/quests/plaguelands_{p}.json").write_text(json.dumps({"quests": qs}, indent=2,
                                                                           ensure_ascii=False) + "\n",
                                                                encoding="utf-8")
    FACTIONS.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
