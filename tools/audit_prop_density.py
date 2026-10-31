#!/usr/bin/env python3
"""Measure prop density zone by zone, across every zone in the game.

Kyle, 2026-10-31: "demon wastes in ashenvale is crowded full of stuff. sometimes
less is more. we should drop down overall props slightly when we can across the
world."

He is right about Demon Wastes. "Across the world" is the part that needs
measuring first, because a blanket multiplier also thins the zones that are
ALREADY sparse, and this codebase has burned me three times on exactly that
shape of change. So: measure every zone, rank it, and cut only where the number
says to.

WHAT COUNTS AS A PROP. A tree, a crate, a rock, a barrel: these are COLLISION
tiles, not visual ones. That is why ZoneGenerator._scatter carries
require_no_collision. A first version of this tool measured the visual layer
and happily reported Orgrimmar and Durotar at 0.0% props, which is how I knew
it was measuring the wrong thing - a check that reports what you know to be
false is at least honest about being broken.

So: prop = a collision tile that is NOT terrain. Terrain (cliff, wall, water,
mountain) is the shape of the zone and nobody experiences it as clutter.

DENOMINATOR. Open floor, i.e. walkable tiles plus the props standing in them.
Props per total map area would punish a zone for having a big lake.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Collision tiles that are terrain - the zone's shape, never clutter.
TERRAIN = {
    "cliff", "wall", "rock_wall", "mountain", "water", "deep_water", "lava",
    "stone_wall", "cave_wall", "bone_hall_wall", "ice_wall", "building",
    "wall_stone", "wall_wood", "hut", "tent", "roof", "ship_hull", "void",
}
#: ...and anything whose id ends in one of these reads as structure, not prop.
TERRAIN_SUFFIX = ("_wall", "_cliff", "_building", "_roof", "_hull", "_floor")

PROP_FLOOR_CROWDED = 0.22   # above this, the floor is visibly full of stuff
PROP_FLOOR_SPARSE  = 0.03   # below this, cutting further would empty the zone


def is_terrain(tid):
    return tid in TERRAIN or any(tid.endswith(s) for s in TERRAIN_SUFFIX)


def measure(zone):
    walk = 0
    props = collections.Counter()
    for y in range(zone.height):
        for x in range(zone.width):
            c = zone.collision_layer[y][x]
            if c is None:
                walk += 1
            elif not is_terrain(str(c)):
                props[str(c)] += 1
    return walk, props


def main():
    from world.zone_generator import create_all_zones
    zones = create_all_zones()

    rows = []
    for name, z in zones.items():
        if not hasattr(z, "collision_layer"):
            continue
        walk, props = measure(z)
        n = sum(props.values())
        floor = walk + n
        if floor < 200:          # tiny interiors tell you nothing
            continue
        rows.append((n / floor, name, n, floor, props))

    rows.sort(reverse=True)
    print(f"{len(rows)} zones measured\n")
    print(f"  {'props/floor':>11}  {'props':>6}  {'floor':>7}  zone")
    crowded = []
    for cov, name, n, floor, props in rows:
        flag = ""
        if cov >= PROP_FLOOR_CROWDED:
            flag = "   <-- CROWDED"
            crowded.append((name, cov, props))
        elif cov <= PROP_FLOOR_SPARSE:
            flag = "   (sparse - leave alone)"
        print(f"  {cov*100:10.1f}%  {n:6d}  {floor:7d}  {name}{flag}")

    cov = [r[0] for r in rows]
    print(f"\n  median {sorted(cov)[len(cov)//2]*100:.1f}%   "
          f"mean {sum(cov)/len(cov)*100:.1f}%   "
          f"crowded (>={PROP_FLOOR_CROWDED*100:.0f}%): {len(crowded)}   "
          f"sparse (<={PROP_FLOOR_SPARSE*100:.0f}%): {sum(1 for c in cov if c <= PROP_FLOOR_SPARSE)}")

    if crowded:
        print("\n  what the crowded zones are actually full of:")
        for name, cov, props in crowded:
            top = ", ".join(f"{t} x{c}" for t, c in props.most_common(6))
            print(f"    {name} ({cov*100:.0f}%): {top}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
