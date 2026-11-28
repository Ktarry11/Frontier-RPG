#!/usr/bin/env python3
"""Map a class's abilities onto CoA's spec tabs, from the live client data (Kyle, 27 Nov 2026: flesh out the CoA
classes with a real split between specs - "look at wind stormbringer learning lightning and maelstrom exclusive stuff").

    python3 tools/coa_spec_map.py Tinker tinker "Firearms=tinker_demolition,Invention=tinker_invention,Mechanics=tinker_mechanics"

Reads github.com/Bharph/coa-preservation-data (clone it to /home/claude/bharph/coa-preservation-data or pass
--data): the client's CharacterAdvancementData tabs (frozen Feb 2026: old tab keys and some old node names, so names
are taken from the LIVE tooltips of each node's spell) and the tooltips themselves.

Prints, for every ability in data/abilities/<slug>.json, which CoA tab(s) it belongs to (Class = every spec), then
each spec's actives that the class doesn't have yet, with their tooltip - the shortlist to choose from. It writes
nothing: choosing what fits a turn-based game is a judgement (no movement, knockback, line of sight).
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
norm = lambda s: re.sub(r"[^a-z]", "", str(s).lower())
SKIP = re.compile(r"DEPP|NEEDS REDONE|Specialization|Hit Rating|^Wands$|\(Alpha\)|Unused", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("coa_class"); ap.add_argument("slug"); ap.add_argument("tabs", help="Tab=spec_slug,...")
    ap.add_argument("--data", default="/home/claude/bharph/coa-preservation-data")
    a = ap.parse_args()
    data = Path(a.data)
    tabmap = dict(x.split("=") for x in a.tabs.split(","))
    nodes = json.loads((data / "client-content/CharacterAdvancementData.json").read_text())
    tt = {}
    with open(data / "spell-tooltips/all-spell-tooltips-merged.ndjson") as f:
        for line in f:
            o = json.loads(line); tt[o["id"]] = o

    def live(r):
        for s in r.get("Spells") or []:
            o = tt.get(s)
            if o and o.get("name"):
                return o["name"], (o.get("tt") or "")
        return r.get("Name", ""), ""

    tabs, tips = {}, {}
    for r in nodes:
        if r.get("Class") != a.coa_class or r.get("Type") not in ("Ability", "TalentAbility"):
            continue
        n, t = live(r)
        if SKIP.search(n) or SKIP.search(str(r.get("Name"))):
            continue
        tabs.setdefault(r["Tab"], {}).setdefault(norm(n), (n, r.get("RequiredLevel", 0)))
        if len(t) > len(tips.get(norm(n), "")):
            tips[norm(n)] = t
    cls = set(tabs.get("Class", {}))
    ours = json.loads((ROOT / f"data/abilities/{a.slug}.json").read_text())["abilities"]
    have = {norm(x["name"]) for x in ours}
    print("== our abilities")
    for x in ours:
        n = norm(x["name"])
        where = [tabmap.get(t, t) for t in tabs if t != "Class" and n in tabs[t]]
        tag = "class" if (n in cls and len(where) != 1) else (",".join(where) if where else "-- not in CoA tree")
        print(f"{x['ranks'][0]['level_req']:>3} {x['name']:<26} {tag}   now={x.get('specs', 'all')}")
    for t, spec in tabmap.items():
        print(f"\n== {spec} ({t}) actives we don't have")
        for k, (n, lv) in sorted(tabs.get(t, {}).items(), key=lambda kv: kv[1][1]):
            tip = tips.get(k, "")
            if k in have or k in cls or not re.search(r"cooldown|cast|Instant|Channel", tip):
                continue
            print(f"{lv:>3} {n} :: {tip[:220]}".replace("\n", " ").replace("\r", ""))
    print("\n== Class actives we don't have")
    for k, (n, lv) in sorted(tabs.get("Class", {}).items(), key=lambda kv: kv[1][1]):
        tip = tips.get(k, "")
        if k in have or not re.search(r"cooldown|cast|Instant|Channel", tip):
            continue
        print(f"{lv:>3} {n} :: {tip[:220]}".replace("\n", " ").replace("\r", ""))


if __name__ == "__main__":
    sys.exit(main())
