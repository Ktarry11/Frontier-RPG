#!/usr/bin/env python3
"""Deal every place in the game an image from its pack, as evenly as possible.

    PYTHONPATH=. python3 tools/build_background_assignments.py [--check]

WHY THIS EXISTS. The loader used to pick with random.choice, frozen for the
session. Hashing the place name instead fixes stability - a place looks like
itself across restarts - but it does NOT fix spread, and spread is the whole
point of the art that went in on 7 Nov. Hashing 84 places into 15 buckets is
rolling a die 84 times, not dealing 15 cards: measured, it left one
dark_dungeon image covering ten places and another covering two, against an
even share of 5.6. That is the same repetition the art was bought to remove,
arriving by a different road.

So the assignment is computed ONCE, here, with every place in hand, and
written to assets/backgrounds/assignments.json. Dealing needs the whole list,
which the loader cannot have at combat time without building the world.

HOW IT DEALS. Per pack: sort the places for determinism, then walk them
handing out images round-robin from a rotation that is itself ordered by the
pack's own file list. Round-robin over a sorted list also means the subzones
of one dungeon - which a player walks through back to back, and which is
where repetition is actually noticed - get consecutive, different images
rather than whatever a hash happened to collide on.

STALENESS IS SAFE. A place added after this ran is simply missing from the
map, and the loader falls back to its hash. So this never has to be re-run to
keep the game working; re-running it only makes the spread even again. --check
reports drift without writing, for the QA suite.
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "assets", "backgrounds")
OUT = os.path.join(PACKS, "assignments.json")


def _images(folder, variant=None):
    path = os.path.join(PACKS, folder, variant) if variant else os.path.join(PACKS, folder)
    if not os.path.isdir(path):
        return []
    return sorted(f for f in os.listdir(path) if f.lower().endswith((".png", ".jpg", ".jpeg")))


def build():
    from world.zone_generator import create_all_zones
    from world.combat_backgrounds import resolve_place
    from world.tile_textures import CAVE_BIOME

    zones = create_all_zones()

    # (folder, variant) -> [(zone, place)]. KEYED ON THE ZONE TOO, not the
    # place alone: "The Great Hall" is a subzone of Dun Garok, Shadowfang Keep
    # AND Tiragarde Keep, and flattening those to one key gave all three keeps
    # the same room. 81 names are shared across zones. What still collapses is
    # a name repeated INSIDE one zone - Southern Barrens has eleven subzones
    # called "The Rift" - and that is correct: a player cannot tell those
    # apart either.
    by_pack = collections.defaultdict(set)
    for zname, z in zones.items():
        cave = zname in CAVE_BIOME
        places = [zname] + [sz["name"] if isinstance(sz, dict) else getattr(sz, "name", None)
                            for sz in (getattr(z, "subzones", []) or [])]
        for place in places:
            if not place:
                continue
            folder, variant, _ = resolve_place(zname, None if place == zname else place, cave)
            by_pack[(folder, variant)].add((zname, place))

    assignments = {}
    report = []
    for (folder, variant), places in sorted(by_pack.items()):
        imgs = _images(folder, variant)
        if not imgs:
            continue
        key = f"{folder}/{variant}" if variant else folder
        ordered = sorted(places)
        counts = collections.Counter()
        for i, (zname, place) in enumerate(ordered):
            chosen = imgs[i % len(imgs)]
            assignments[f"{key}\t{zname}\t{place}"] = chosen
            counts[chosen] += 1
        report.append((key, len(imgs), len(ordered), min(counts.values()), max(counts.values())))
    return assignments, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report drift against the written map; do not write")
    args = ap.parse_args()

    assignments, report = build()

    if args.check:
        if not os.path.exists(OUT):
            print(f"  MISSING: {os.path.relpath(OUT, ROOT)} - run this tool without --check")
            return 1
        with open(OUT) as fh:
            on_disk = json.load(fh)
        missing = set(assignments) - set(on_disk)
        stale = set(on_disk) - set(assignments)
        print(f"  {len(assignments)} places assigned; {len(missing)} unassigned, {len(stale)} stale")
        for k in sorted(missing)[:10]:
            print(f"       unassigned (loader will hash): {k}")
        for k in sorted(stale)[:10]:
            print(f"       no longer a place: {k}")
        # Drift is not a failure. An unassigned place still gets a background,
        # it just gets a hashed one instead of a dealt one.
        return 0

    with open(OUT, "w") as fh:
        json.dump(assignments, fh, indent=0, sort_keys=True)
    print(f"  {len(assignments)} places -> {os.path.relpath(OUT, ROOT)}\n")
    print(f"  {'pack':24}{'imgs':>5}{'places':>8}{'min':>6}{'max':>6}")
    for key, imgs, places, lo, hi in sorted(report, key=lambda r: -r[2]):
        print(f"  {key:24}{imgs:>5}{places:>8}{lo:>6}{hi:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
