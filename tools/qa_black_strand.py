#!/usr/bin/env python3
"""The Black Strand is an open zone you can get into, walk across and fight in.

    PYTHONPATH=. python3 tools/qa_black_strand.py

Kyle, 13 Nov 2026: a layer under the Dry Deep, 50-53, "a gorgeous mix of dark sand, fungi, and
silithid"; then of the first pass, "increase playing area massively....maybe 30% more? I do like
the cave zone, but i still want it 'open zone' as well"; "less is more with props"; and of a rare
elsewhere, "Dont make the boss with 1300 HP".

SIX CLAIMS:
  1. IT IS AN OPEN ZONE, not a cave, and one connected floor.
  2. THE FLOOR IS AT LEAST 30% BIGGER than the first pass (7,129 tiles) - and stays that way.
  3. THE WAY DOWN AND THE WAY BACK UP JOIN: the Dry Deep's last room and the Bottom Step.
  4. EVERY PLACE HAS SOMETHING TO FIGHT, except the gate, which is safe; every creature exists,
     has a kit, and the zone's level band is 50-53.
  5. NO RARE IS A PUSHOVER: each has at least 2,500 health and its own loot.
  6. THE PROPS LEAVE THE FLOOR SHOWING: under one prop per 60 walkable tiles.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

FIRST_PASS_FLOOR = 7129

with contextlib.redirect_stdout(io.StringIO()):
    from tools import handbuilt_black_strand as M
    from tools import handbuilt_dry_deep as D
    from world.creature_manager import CreatureManager
    from entities.boss_loot import _load_boss_loot_tables


def main():
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        zone, L = M.build_black_strand_baked()
        cm = CreatureManager()
    info = M.verify(zone)
    floor = info["reachable"]
    if zone.is_cave:
        bad.append("the zone is flagged a cave")
    if floor < FIRST_PASS_FLOOR * 1.3:
        bad.append(f"{floor} walkable tiles - less than 30% over the first pass ({FIRST_PASS_FLOOR})")

    src = Path("world/portal_manager.py").read_text(encoding="utf-8")
    for needle in (f'({D.DOWN[0]}, {D.DOWN[1]}): ("The Black Strand", {M.START[0]}, {M.START[1]})',
                   f'({M.UP[0]}, {M.UP[1]}): ("The Dry Deep", {D.DOWN_ARRIVAL[0]}, {D.DOWN_ARRIVAL[1]})'):
        if needle not in src:
            bad.append(f"portal link missing: {needle}")
    with contextlib.redirect_stdout(io.StringIO()):
        dz, _ = D.build_dry_deep_baked()
    if dz.interaction_layer[D.DOWN[1]][D.DOWN[0]] != "portal" or not dz.is_walkable(*D.DOWN_ARRIVAL):
        bad.append("the Dry Deep has no way down, or nowhere to arrive coming up")
    if zone.interaction_layer[M.UP[1]][M.UP[0]] != "portal" or not zone.is_walkable(*M.START):
        bad.append("the Bottom Step has no way up, or nowhere to arrive")

    enc = json.load(open("data/creatures/encounters.json", encoding="utf-8"))["zones"].get(M.NAME, {})
    creatures = json.load(open("data/creatures/creatures.json", encoding="utf-8"))["creatures"]
    kits = json.load(open("data/creatures/ability_kits.json", encoding="utf-8"))["kits"]
    loot = _load_boss_loot_tables()
    rares = 0
    for (name, *_r) in M.CHAMBERS:
        sz = enc.get("subzones", {}).get(name)
        if sz is None:
            bad.append(f"{name} has no encounter table")
            continue
        if sz.get("safe"):
            continue
        if not any(w > 0 for w in sz["creatures"].values()):
            bad.append(f"{name} has nothing to fight")
        for c, w in sz["creatures"].items():
            d = creatures.get(c)
            if d is None or d.get("ability_kit") not in kits:
                bad.append(f"{c} does not exist or has no kit")
                continue
            if not (50 <= d["level_range"][0] and d["level_range"][1] <= 53):
                bad.append(f"{c} is outside 50-53")
            if d.get("is_boss"):
                rares += 1
                with contextlib.redirect_stdout(io.StringIO()):
                    hp = cm.spawn_creature(c).max_health
                if hp < 2500:
                    bad.append(f"{c} has {hp} health")
                if w != 0:
                    bad.append(f"{c} is a rare on a weight, not on the rare roll")
                if not loot.get(c):
                    bad.append(f"{c} drops nothing of its own")
    band = json.load(open("data/zones/zone_levels.json", encoding="utf-8"))["zones"].get(M.NAME)
    if band != [50, 53]:
        bad.append(f"the zone's level band is {band}")

    props = len(zone.landmarks)
    if props * 60 > floor:
        bad.append(f"{props} props on {floor} tiles - more than one per 60")

    print(f"{floor} walkable tiles (+{floor / FIRST_PASS_FLOOR - 1:.0%} on the first pass), "
          f"{len(M.CHAMBERS)} places, {rares} rares, {props} props")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nBlack Strand OK - open, joined to the Dry Deep, populated, and not carpeted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
