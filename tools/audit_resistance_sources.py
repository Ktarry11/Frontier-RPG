#!/usr/bin/env python3
"""What a player can actually stack in one resistance school, and what it is worth.

    PYTHONPATH=. python3 tools/audit_resistance_sources.py

WHY THIS EXISTS. The resistance rework (85fe92a) kept RESIST_MAX at 60 and
changed what reaching it pays:

    RESIST_PCT_PER_POINT   0.005 -> 0.0125
    RESIST_CAP             30%   -> 75%

That is a 2.5x uplift on every point of resistance in the game. The rework
rescaled the CREATURE side - it added the level ceiling, the negative range
and the curated vulnerabilities - and did not touch a single PLAYER-side
resistance value. All 72 of them were authored against a 30% cap, which is
the same mistake the creature armour unification made: a scale moved and the
values authored against the old one stayed put.

This tool does not fix that. The fix is a design call with more than one
sensible shape, so it measures and prints, and Kyle decides.

WHAT IT MEASURES. Per school, the best PERSISTENT stack a party can hand one
member - buffs with no cooldown that last 30 turns or do not expire, one per
exclusive_group per class, plus an elixir - against the 60-point cap. Short
combat buffs (Shaman's resistance totems, Hunter's Aspect of the Wild) are
listed separately because they cost a slot and a window rather than nothing.
"""

import argparse
import collections
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCHOOLS = ["fire", "frost", "nature", "shadow", "arcane", "holy"]
#: A buff this long, with no cooldown, is one a party simply has up.
PERSISTENT_DURATION = 30


def _abilities(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = doc.get("abilities", doc)
    if isinstance(entries, dict):
        entries = list(entries.values())
    return [a for a in entries if isinstance(a, dict)]


def collect():
    """Every player-side resistance source, tagged persistent or windowed."""
    out = []
    for path in sorted(glob.glob(str(ROOT / "data/abilities/*.json"))):
        cls = os.path.basename(path)[:-5]
        for a in _abilities(path):
            mods = a.get("stat_mods") or {}
            got = {s: mods[f"{s}_resistance"] for s in SCHOOLS
                   if mods.get(f"{s}_resistance")}
            if not got:
                continue
            target = str(a.get("target_type") or a.get("target") or "")
            # A negative resistance with no stated target is a debuff put on
            # an ENEMY (Stormstrike makes its target take more nature), not
            # something a player carries. Counting it here would read as the
            # player resisting -20.
            if not target and any(v < 0 for v in got.values()):
                continue
            dur = a.get("duration") or 0
            cd = a.get("cooldown") or 0
            # duration 0 means "until replaced"; >=30 with no cooldown is a
            # raid buff in all but name.
            persistent = cd == 0 and (dur == 0 or dur >= PERSISTENT_DURATION)
            out.append(dict(source=cls, name=a.get("name"),
                            group=a.get("exclusive_group"),
                            party="party" in target,
                            duration=dur, cooldown=cd,
                            persistent=persistent, mods=got))

    elixirs = json.loads(
        (ROOT / "data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    for group in elixirs.values() if isinstance(elixirs, dict) else []:
        if not isinstance(group, list):
            continue
        for c in group:
            if not isinstance(c, dict):
                continue
            bonus = c.get("stat_bonuses") or {}
            got = {s: bonus[f"{s}_resistance"] for s in SCHOOLS
                   if bonus.get(f"{s}_resistance")}
            if got:
                out.append(dict(source="consumable", name=c.get("name"),
                                group="elixir", party=False,
                                duration=None, cooldown=0, persistent=True,
                                mods=got))
    return out


def best_persistent_stack(sources, school):
    """One buff per (class, exclusive_group); ungrouped buffs all apply."""
    per_slot = {}
    loose = []
    for s in sources:
        if not s["persistent"]:
            continue
        v = s["mods"].get(school)
        if not v:
            continue
        if s["group"]:
            key = (s["source"], s["group"])
            if v > per_slot.get(key, (0, None))[0]:
                per_slot[key] = (v, s)
        else:
            loose.append((v, s))
    return sorted(loose + list(per_slot.values()), key=lambda p: -p[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--party-size", type=int, default=5,
                    help="how many distinct buff-bringers to allow (default 5)")
    args = ap.parse_args()

    from entities.character import Character as C

    sources = collect()
    print(f"{len(sources)} player-side resistance sources\n")

    print("what a rating is worth, before and after the rework:")
    for r in (10, 20, 30, 45, 60, 90):
        after = C.resist_mitigation_from(r)
        before = min(0.30, max(0, min(60, r)) * 0.005)
        print(f"  {r:>3} rating ->  before {before:6.1%}   now {after:6.1%}")

    print(f"\nbest PERSISTENT stack ON ONE CHARACTER per school - party "
          f"buffs from up to {args.party_size} distinct classes plus that "
          f"character's own self-buffs and an elixir:")
    for school in SCHOOLS:
        picks = best_persistent_stack(sources, school)
        if not picks:
            print(f"\n  {school:8} - nothing persistent")
            continue
        used, total, lines = set(), 0.0, []
        for v, s in picks:
            if len(used) >= args.party_size and s["source"] not in used:
                continue
            used.add(s["source"])
            total += v
            kind = "party" if s["party"] else (
                "elixir" if s["source"] == "consumable" else "self")
            lines.append(f"      {v:>5} {s['source']:14}"
                         f"{str(s['name'])[:30]:32}{kind}")
        capped = min(C.RESIST_MAX, total)
        waste = total - capped
        print(f"\n  {school:8} {total:>6.0f} rating -> "
              f"{C.resist_mitigation_from(total):5.1%}"
              + (f"   ({waste:.0f} of it wasted above the "
                 f"{C.RESIST_MAX}-point cap)" if waste else ""))
        for line in lines:
            print(line)

    windowed = [s for s in sources if not s["persistent"]]
    if windowed:
        print("\nwindowed sources (cost a slot or a cooldown, listed for "
              "completeness):")
        for s in sorted(windowed, key=lambda s: -max(s["mods"].values())):
            mods = ", ".join(f"{k} {v}" for k, v in s["mods"].items())
            worth = C.resist_mitigation_from(max(s["mods"].values()))
            print(f"  {s['source']:14}{str(s['name'])[:26]:28}"
                  f"dur {str(s['duration']):>4}  cd {s['cooldown']:>2}  "
                  f"{mods:36}-> {worth:5.1%}")

    over = [s for s in sources if max(s["mods"].values()) > C.RESIST_MAX]
    if over:
        print(f"\nsingle sources that exceed the {C.RESIST_MAX}-point cap on "
              f"their own (every point above it is thrown away):")
        for s in sorted(over, key=lambda s: -max(s["mods"].values())):
            print(f"  {max(s['mods'].values()):>5}  {s['source']:14}"
                  f"{s['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
