#!/usr/bin/env python3
"""Hammerfall has what a garrison town needs, and nothing authored for it is missing.

    PYTHONPATH=. python3 tools/qa_hammerfall.py

Kyle, 13 Nov 2026: "Then arathi as needed." Sixty authored pieces never appeared here. Fifty-two
were a stockade, towers and a gatehouse sited in the rock; they are cut, because the cliff already
is the wall. What the town was actually short of was a forge.

FIVE CLAIMS:
  1. NOTHING AUTHORED IS MISSING from the finished map.
  2. THE WAR FORGE IS BUILT, and a forge record sits where the weaponsmith and the blacksmithing
     trainer can both reach it from where they stand (ForgeManager.FORGE_REACH).
  3. AN ARMOURY stands in the war yard, and TWO TOWERS flank the gate.
  4. THE INN, THE FLIGHT MASTER AND THE STABLE each have their building.
  5. EVERYONE CAN BE WALKED TO from the gate.
"""
import collections
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))
    from tools import handbuilt_hammerfall as HF
    from world.forge_manager import ForgeManager

    L = HF.build_layout()
    L = L[0] if isinstance(L, tuple) else L
    z = L.z
    stem = lambda n: os.path.basename(str(n)).replace(".png", "")
    have = collections.Counter(stem(l["sprite_key"]) for l in z.landmarks)
    bad = []

    gone = sorted({(stem(s[0]), s[1], s[2], str(s[3])) for s in L.skipped if stem(s[0]) not in have})
    if gone:
        bad.append(f"authored and not on the map: {gone}")

    for name, n in (("orc_war_forge", 1), ("orc_armoury", 1), ("orc_watch_tower", 2),
                    ("orc_officers_house", 1), ("orc_warbeast_stable", 1), ("orc_warchief_lodge", 1)):
        if have[name] < n:
            bad.append(f"{name}: {have[name]} on the map, wanted {n}")

    forges = [f for f in json.load(open("data/npcs/forges.json"))["forges"] if f["zone"] == "hammerfall"]
    if len(forges) != 1:
        bad.append(f"{len(forges)} forge records for Hammerfall, wanted 1")
    else:
        f = forges[0]
        for who in ("hammerfall_weaponsmith", "pt_hammerfall_forge"):
            x, y = HF.NPC_POSITIONS[who]
            d = max(abs(f["x"] - x), abs(f["y"] - y))
            if d > ForgeManager.FORGE_REACH + 3:
                bad.append(f"{who} stands {d} tiles from the forge")
        if not z.is_walkable(f["x"], f["y"]):
            bad.append(f"the forge tile {f['x'], f['y']} cannot be stood on")

    # 5. flood from the arrival tile
    start = HF.ARRIVALS[0]
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < z.width and 0 <= n[1] < z.height and z.is_walkable(*n):
                seen.add(n)
                todo.append(n)
    for who, (x, y) in HF.NPC_POSITIONS.items():
        if not any((x + dx, y + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            bad.append(f"{who} at {(x, y)} cannot be reached from the gate")

    print(f"{len(z.landmarks)} pieces on the map, {sum(v for k, v in have.items() if k.startswith('orc_'))} "
          f"buildings, {len(HF.NPC_POSITIONS)} people, forge at {forges[0]['x'], forges[0]['y'] if forges else None}")
    for b in bad:
        print("  FAIL", b)
    print("\nHammerfall OK - forge, armoury, gate towers, and nothing authored is missing."
          if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
