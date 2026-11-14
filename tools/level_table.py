#!/usr/bin/env python3
"""Print the world level table (open world / subzones / caves, with per-zone level_overrides applied) and flag any cave whose
low end is below its zone's open-world low end (Kyle's rule: a cave/dungeon is never BELOW its zone; higher is fine).

    python3 tools/level_table.py > /tmp/level_table.md
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
E = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
Q = {}
for f in sorted((ROOT / "data/quests").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    for q in (d["quests"] if isinstance(d, dict) else d):
        Q.setdefault(q.get("zone"), []).append(q.get("level_min") or 0)


def rng(zone, tbl):
    ov = E[zone].get("level_overrides", {})
    lo, hi = 999, 0
    for n in (tbl.get("creatures") or {}):
        r = ov.get(n) or C.get(n, {}).get("level_range")
        if r:
            lo, hi = min(lo, r[0]), max(hi, r[1])
    return None if hi == 0 else (lo, hi)


def fmt(r):
    return "-" if r is None else (f"{r[0]}" if r[0] == r[1] else f"{r[0]}-{r[1]}")


def main():
    print("| Zone | Open world | Subzones (range) | Caves / dungeons | Flags |\n|---|---|---|---|---|")
    for z, zz in E.items():
        if "open_zone" not in zz:
            continue
        o = rng(z, zz["open_zone"])
        subs = "; ".join(f"{s} {fmt(rng(z, v))}" for s, v in zz.get("subzones", {}).items())
        caves, flags = [], []
        for s, v in zz.get("caves", {}).items():
            r = rng(z, v)
            caves.append(f"**{s}** {fmt(r)}")
            if o and r and r[0] < o[0]:
                flags.append(f"{s} starts at {r[0]} (zone {o[0]})")
        print(f"| {z} | {fmt(o)} | {subs or '-'} | {'; '.join(caves) or '-'} | {'; '.join(flags)} |")
    print("\n## Quest levels per zone (min of level_min .. max)")
    for z, lv in sorted(Q.items(), key=lambda kv: min(kv[1] or [0])):
        lv = [x for x in lv if x]
        if lv:
            print(f"- {z}: {min(lv)}-{max(lv)} ({len(lv)} quests)")


if __name__ == "__main__":
    main()
