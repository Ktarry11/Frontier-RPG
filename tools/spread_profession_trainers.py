#!/usr/bin/env python3
"""Put each profession trainer where their trade actually happens, instead of all five in a clump.

    PYTHONPATH=. python3 tools/spread_profession_trainers.py --dry-run
    PYTHONPATH=. python3 tools/spread_profession_trainers.py

Kyle, 2026-10-31: "with profession trainers in towns or cities, split them up. Like we keep
doing this bunch of 5 which makes no sense."

He is describing something the data does literally. Fourteen towns each hold the SAME five
trainers - Tinker, Tanner, Woodwright, Apothecary, Forge - in the SAME X-shape, and in every
one of them the closest pair stands ONE tile apart. Orgrimmar's five occupy a 3x5 box.

ANCHORED, NOT JUST SCATTERED. A blacksmith belongs at the forge and a tanner at the hide racks,
and these towns already have that art - grand_forge, smithy, hide_tanners_hut, vot_hide_rack,
uc_alchemy_table, ash_herbalist_table, rf_tool_rack, scrapyard_workshop. Each trainer is placed
beside the nearest landmark that matches their trade; only where a town has no such prop do they
fall back to being fanned out from where they already stood.

Every destination is checked against the zone's own is_walkable and snapped if it is not, using
the same spiral ZoneManager uses for portal arrivals. A trainer inside a wall is worse than a
trainer in a clump.
"""
import argparse
import collections
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

#: Minimum tiles between any two profession trainers in the same town.
MIN_SPACING = 9

#: How far a trainer may be moved from where they already stand.
#:
#: Without this, a trainer went to the FIRST matching prop in the landmark list, which in
#: Orgrimmar sent the Woodwright 128 tiles across the city. Kyle asked for them split up, not
#: scattered - a player should not have to cross a capital to find the tanner. Candidate props
#: are sorted by distance from where the trainer already is, and anything past this is ignored
#: in favour of the spread ring.
MAX_MOVE = 30

#: profession -> substrings of a landmark's sprite name that mean "this trade happens here".
#: Ordered best-match-first within each list.
TRADE_PROPS = {
    "blacksmithing": ("grand_forge", "smithy", "forge", "anvil"),
    "leatherworking": ("hide_tanners_hut", "hide_rack", "tanner", "drying_rack"),
    "alchemy": ("alchemy_table", "herbalist_table", "cauldron", "copper_still", "still"),
    "woodworking": ("tool_rack", "lumber", "saw", "driftwood", "log"),
    "engineering": ("scrapyard_workshop", "workshop", "trading_post", "crate_stack", "crates"),
}

#: Which of the five a trainer is, by the crafting profession they teach.
def trade_of(professions):
    for p in ("blacksmithing", "leatherworking", "alchemy", "woodworking", "engineering"):
        if p in professions:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from world.zone_manager import ZoneManager
    zm = ZoneManager()

    trainers = json.loads((ROOT / "data/training/trainers.json").read_text(encoding="utf-8"))
    prof_trainers = trainers.get("profession_trainers", {})

    npc_path = ROOT / "data/npcs/ambient_npcs.json"
    amb = json.loads(npc_path.read_text(encoding="utf-8"), object_pairs_hook=collections.OrderedDict)

    def walk(o):
        if isinstance(o, dict):
            if o.get("npc_id"):
                yield o
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)

    by_id = {n["npc_id"]: n for n in walk(amb)}
    zone_keys = list(zm.zones) if isinstance(getattr(zm, "zones", None), dict) else []

    # town (as the NPC record spells it) -> [(npc record, professions)]
    by_town = collections.defaultdict(list)
    for npc_id, professions in prof_trainers.items():
        n = by_id.get(npc_id)
        if n:
            by_town[n["zone"]].append((n, professions))

    moved = anchored = 0
    for town, members in sorted(by_town.items()):
        # The NPC records spell towns in snake_case; ZoneManager keys them as display names,
        # which are neither snake_case NOR plain .title() - "Valley of Trials" has a lowercase
        # "of" and "The Sepulcher" has a word the NPC record leaves out entirely. Match on
        # letters only, case-insensitively, which handles all three shapes.
        def _key(t):
            return "".join(ch for ch in str(t).lower() if ch.isalnum())
        zone = zm.get_zone_by_name(town)
        if zone is None:
            want = _key(town)
            for known in zone_keys:
                k = _key(known)
                if k == want or k.endswith(want) or want.endswith(k):
                    zone = zm.get_zone_by_name(known)
                    break
        if zone is None:
            print(f"  !! no zone for {town} - left alone")
            continue
        landmarks = getattr(zone, "landmarks", None) or []
        taken = []
        cx = sum(n["x"] for n, _ in members) // len(members)
        cy = sum(n["y"] for n, _ in members) // len(members)

        print(f"\n{town}  ({len(members)} trainers, {len(landmarks)} landmarks)")
        for i, (npc, professions) in enumerate(sorted(members, key=lambda m: m[0]["npc_id"])):
            trade = trade_of(professions)
            spot = None
            why = ""
            if trade:
                for needle in TRADE_PROPS.get(trade, ()):
                    matches = [lm for lm in landmarks
                               if needle in str(lm.get("sprite_key", "")).lower()]
                    # NEAREST first, so a trainer stays in their own quarter of the town.
                    matches.sort(key=lambda lm: max(abs(lm["anchor_x"] - npc["x"]),
                                                    abs(lm["anchor_y"] - npc["y"])))
                    best = None
                    for lm in matches:
                        if max(abs(lm["anchor_x"] - npc["x"]),
                               abs(lm["anchor_y"] - npc["y"])) > MAX_MOVE:
                            break
                        # Stand just below the prop's anchor, the side a shopkeeper faces.
                        cand = (lm["anchor_x"] + lm.get("width_tiles", 1) // 2,
                                lm["anchor_y"] + lm.get("height_tiles", 1) + 1)
                        snapped = ZoneManager._find_nearest_walkable(zone, *cand, max_radius=6)
                        if snapped is None:
                            continue
                        if any(max(abs(snapped[0] - px), abs(snapped[1] - py)) < MIN_SPACING
                               for px, py in taken):
                            continue
                        best = snapped
                        break
                    if best:
                        spot, why = best, f"at the {needle}"
                        break
            if spot is None:
                # No matching prop with room: fan out from the town centre on a ring wide
                # enough that no two trainers read as one group.
                import math
                for ring in range(MIN_SPACING, MIN_SPACING * 5, 3):
                    ang = (2 * math.pi * i) / max(1, len(members))
                    cand = (int(cx + ring * math.cos(ang)), int(cy + ring * math.sin(ang)))
                    snapped = ZoneManager._find_nearest_walkable(zone, *cand, max_radius=8)
                    if snapped is None:
                        continue
                    if any(max(abs(snapped[0] - px), abs(snapped[1] - py)) < MIN_SPACING
                           for px, py in taken):
                        continue
                    spot, why = snapped, "spread from the town centre"
                    break
            if spot is None:
                print(f"    {npc['name']:28s} nowhere to put them - left at ({npc['x']},{npc['y']})")
                taken.append((npc["x"], npc["y"]))
                continue
            taken.append(spot)
            if (npc["x"], npc["y"]) != spot:
                moved += 1
            if why.startswith("at the"):
                anchored += 1
            print(f"    {npc['name']:28s} ({npc['x']:3d},{npc['y']:3d}) -> ({spot[0]:3d},{spot[1]:3d})  {why}")
            npc["x"], npc["y"] = spot

    if not args.dry_run:
        npc_path.write_text(json.dumps(amb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{moved} trainers moved, {anchored} of them onto a prop of their own trade"
          f"{' (dry run)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
