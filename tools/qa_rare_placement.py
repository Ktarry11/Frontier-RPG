#!/usr/bin/env python3
"""RARE MOBS LIVE IN SUBZONES, NOWHERE ELSE. Checks it, and --fix enforces it.

    PYTHONPATH=. python3 tools/qa_rare_placement.py [--fix]

Kyle, 2026-10-30: "Rares should only be in subzones."

THIS IS A RULE WITH TEETH IN THE ENGINE, NOT A PREFERENCE. world/creature_manager.py rolls for a
named is_boss creature in exactly one place:

    if location_type == "subzone":
        rare_names = [n for n in encounter_table if creatures[n]["is_boss"]]
        ...

Nothing else in the game ever rolls one outside a cave, where boss_positions pins them instead. So a
rare sitting in an open_zone table is not "also available on the open map" - it is DEAD DATA. It is
excluded from the trash table for being is_boss, and the only code path that would pick it up never
runs for an open zone. The creature exists, has a kit, has a loot pool, and can never be met.

Measured when this check was written: 28 rares sat in open_zone tables. 14 of them were also in a
subzone, so the open_zone entry was harmless noise that read like it did something. The other 14
could not spawn at all - of which 8 were in zones that pin their rares with boss_positions (the
Frostward Descent, the Gurbashi Arena) and so were fine by accident, and SIX WERE GENUINELY
UNREACHABLE: Old Redtooth, Old Sunhide, Stormwing the Skyrider, Elder Timberling, Felstalker and the
Ancient Curse-Beast. Six hand-written rares with hand-written loot that no player could ever find,
and nothing anywhere threw, logged or complained.

A FIRST VERSION OF THIS CHECK REPORTED ALL 14 AS BROKEN and that would have been crying wolf: the
Frostward and Gurbashi eight spawn fine from boss_positions. The check skips any zone that pins.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENC = ROOT / "data/creatures/encounters.json"
CRE = ROOT / "data/creatures/creatures.json"

#: Homes for the six that had none, chosen from each one's own quest text rather than by vibe.
#:
#:   Old Sunhide           "a giraffe the height of a watchtower... the dry grass he stands in"
#:   Stormwing             a thunderhawk, and Sentinel Rocks is where the Plains Thunderhawks are
#:   Elder Timberling      already lives in Ashenvale EAST's Warsong Lumber Camp; West's timberlings
#:                         are in Silverwind Vale
#:   Felstalker            a demon hound, and the Demon Wastes is where the demons are
#:   Ancient Curse-Beast   "Cursed Shore: a bear the size of a barn, wrapped in its own rot"
#:
#:   Old Redtooth          THE ONE THAT DOESN'T FIT, and it is flagged rather than hidden. He leads
#:                         the Rustfang pack, which the quest puts "tailing the caravans out of
#:                         Orgrimmar" - the open ROAD, which under this rule can no longer host a
#:                         rare, and Rustfang Hyena itself is open_zone trash with no subzone of its
#:                         own. Rocktusk Farm is the nearest honest answer: a working farm with
#:                         livestock on it is exactly what a hyena pack tails. If that reads wrong,
#:                         the real fix is a Rustfang subzone on the road, not a different farm.
HOMES = {
    ("Durotar", "Old Redtooth"): "Rocktusk Farm",
    ("Central Barrens", "Old Sunhide"): "Sentinel Rocks",
    ("Central Barrens", "Stormwing the Skyrider"): "Sentinel Rocks",
    ("Ashenvale West", "Elder Timberling"): "Silverwind Vale",
    ("Ashenvale East", "Felstalker"): "The Demon Wastes",
    ("Fenris Isle", "Ancient Curse-Beast"): "The Drowned Docks",
}


def audit(enc, creatures, pinned):
    """[(zone, rare, 'in a subzone already' | 'nowhere else')] for every rare in an open_zone table."""
    out = []
    for zn, z in enc["zones"].items():
        in_sub = set()
        for s in z.get("subzones", {}).values():
            in_sub |= set(s.get("creatures", {}))
        for n in z.get("open_zone", {}).get("creatures", {}):
            if not creatures.get(n, {}).get("is_boss"):
                continue
            if n in in_sub:
                out.append((zn, n, "already in a subzone"))
            elif zn in pinned:
                out.append((zn, n, "pinned by boss_positions"))
            else:
                out.append((zn, n, "UNREACHABLE"))
    return out


def main(fix=False):
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    from world.zone_generator import create_all_zones
    zones = create_all_zones()
    pinned = {n for n, z in zones.items()
              if getattr(z, "is_cave", False) or getattr(z, "boss_positions", None)}

    raw = ENC.read_text(encoding="utf-8")
    enc = json.loads(raw)
    creatures = json.loads(CRE.read_text(encoding="utf-8"))["creatures"]

    rows = audit(enc, creatures, pinned)
    if not rows:
        print("every rare is in a subzone and nowhere else")
        return 0

    for why in ("UNREACHABLE", "pinned by boss_positions", "already in a subzone"):
        hit = [r for r in rows if r[2] == why]
        if hit:
            print(f"{len(hit)} rare(s) in an open_zone table - {why}:")
            for zn, n, _ in hit:
                print(f"    {zn:26} {n}")
    if not fix:
        print("\nrun with --fix to move them into subzones")
        return 1

    moved = dropped = 0
    for zn, n, why in rows:
        z = enc["zones"][zn]
        del z["open_zone"]["creatures"][n]
        dropped += 1
        if why != "UNREACHABLE":
            continue
        home = HOMES.get((zn, n))
        if home is None:
            print(f"  NO HOME for {zn}/{n} - add one to HOMES")
            return 1
        sub = z["subzones"][home]
        sub.setdefault("creatures", {})[n] = 0      # weight 0: never rolled as filler
        print(f"  {n} -> {zn} / {home}")
        moved += 1

    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{dropped} open_zone entries removed, {moved} rare(s) given a subzone home")
    left = audit(json.loads(ENC.read_text(encoding="utf-8")), creatures, pinned)
    print("re-audit:", "clean" if not left else f"STILL {len(left)} - {left}")
    return 0 if not left else 1


if __name__ == "__main__":
    sys.exit(main("--fix" in sys.argv))
