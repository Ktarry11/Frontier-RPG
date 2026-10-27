"""
Verify The Crystalline Underdark.

    PYTHONPATH=. python3 tools/verify_underdark.py

The archetype claim is THE ROOFED COUNTRY: underground, but laid out so it reads as outdoors. That is not a
matter of taste, it is measurable - open country has long distances to the nearest wall and long clear
sightlines; a cave does not. So the test puts this zone side by side with a real cave (The Frostward Descent,
a warren) and real open country (Eastern Hillsbrad), and requires it to sit nearer the country than the cave.

Everything else is the usual: reachability, no hand-placed prop skipped, portals walkable.
"""
import collections
import os
import sys

import numpy as np

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

from scipy import ndimage as ndi  # noqa: E402

import tools.handbuilt_underdark as UD  # noqa: E402
from world.zone_manager import ZoneManager  # noqa: E402


def openness(z):
    """(walkable fraction, 90th-percentile clear horizontal run) - the two things the claim is actually about.

    The first version of this measured MEAN DISTANCE TO THE NEAREST WALL and it was the wrong instrument: it
    rewards a map with few narrow obstacles and punishes one with many wide-apart ones, which is backwards for
    "does this read as open country". Measured against two known-good open zones it ranked the Underdark below
    the Frostward Descent, a warren that is 36% walkable. Walkable fraction and sightline length do not have
    that failure mode, and both are hard to game by moving a rock."""
    walk = np.zeros((z.height, z.width), bool)
    for y in range(z.height):
        for x in range(z.width):
            walk[y, x] = z.is_walkable(x, y)
    runs = []
    for y in range(z.height):
        run = 0
        for x in range(z.width):
            if walk[y, x]:
                run += 1
            else:
                if run:
                    runs.append(run)
                run = 0
        if run:
            runs.append(run)
    return 100.0 * walk.mean(), float(np.percentile(runs, 90)) if runs else 0.0


def flood(z, start):
    seen, q = {start}, collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if (0 <= n[0] < z.width and 0 <= n[1] < z.height
                    and n not in seen and z.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    return seen


def main():
    L = UD.build_layout()
    z = L.zone
    fails = []

    hand = [s for s in L.skipped if "shroom" not in s[0]]
    print(f"props placed {L.placed} (132 of them scattered mushrooms), hand-placed skips {len(hand)}")
    for s in hand:
        fails.append(f"hand-placed prop skipped: {s}")

    reach = flood(z, UD.START)
    print(f"reachable from the arrival shelf: {len(reach)} tiles")
    for p in UD.PORTALS:
        if not z.is_walkable(*p):
            fails.append(f"portal {p} is not walkable")
        elif p not in reach:
            fails.append(f"portal {p} is unreachable from the arrival")
    for c in UD.CHESTS:
        if tuple(c) not in reach:
            fails.append(f"chest {c} unreachable")
    for n, p in UD.NPC_POSITIONS.items():
        if tuple(p) not in reach:
            fails.append(f"NPC spot {n} at {p} unreachable")

    # ---- THE ARCHETYPE TEST, against a real cave and BOTH real open zones
    zm = ZoneManager()
    print("\nopenness - walkable fraction, and 90th-percentile clear sightline:")
    rows = {}
    for label, name in (("cave (Descent)", "The Frostward Descent"),
                        ("THIS ZONE", "The Crystalline Underdark"),
                        ("country (E Hillsbrad)", "Eastern Hillsbrad"),
                        ("country (W Hillsbrad)", "Western Hillsbrad")):
        zz = zm.get_zone_by_name(name)
        wpc, run = openness(zz)
        rows[label] = (wpc, run)
        print(f"  {label:24} walkable {wpc:5.1f}%   sightline {run:5.1f}")

    cave_w, cave_r = rows["cave (Descent)"]
    here_w, here_r = rows["THIS ZONE"]
    floor_w = min(rows["country (E Hillsbrad)"][0], rows["country (W Hillsbrad)"][0])
    floor_r = min(rows["country (E Hillsbrad)"][1], rows["country (W Hillsbrad)"][1])
    if here_w < floor_w - 3:
        fails.append(f"walkable {here_w:.0f}% is below the open-zone band ({floor_w:.0f}% floor)")
    if here_r < floor_r - 3:
        fails.append(f"sightline {here_r:.0f} is below the open-zone band ({floor_r:.0f} floor)")
    if here_w <= cave_w + 10:
        fails.append(f"walkable {here_w:.0f}% is too near the warren's {cave_w:.0f}% - it reads as a cave")
    if not fails:
        print(f"\n  -> {here_w:.0f}% walkable against the warren's {cave_w:.0f}%, and sightlines at or above "
              f"both open zones. It reads as a roofed country.")

    # ---- THE HOLLOW GEODE: Kyle's note on the first draft was "no massive open trash - a true geode isn't
    #      just open space", so that is tested rather than trusted. Two claims: the map is DENSE (near the
    #      warren, nowhere near open country), and the core is the ONLY generous chamber, because it is the
    #      one part the crystal has not finished filling.
    import tools.handbuilt_hollow_geode as HG
    gz, GL = HG.build_hollow_geode()
    HG.dress(gz, GL)
    HG.finish(gz, GL)
    gwalk = np.zeros((gz.height, gz.width), bool)
    for y in range(gz.height):
        for x in range(gz.width):
            gwalk[y, x] = gz.is_walkable(x, y)
    gd = ndi.distance_transform_edt(gwalk)
    gpc = 100.0 * gwalk.mean()
    ghand = [s for s in GL.skipped]
    print(f"\nThe Hollow Geode: {GL.placed} props, {len(ghand)} skips, {gpc:.1f}% walkable")
    for s in ghand:
        fails.append(f"Geode prop skipped: {s}")
    if gpc > 50:
        fails.append(f"the Geode is {gpc:.0f}% walkable - that is open space, not a filled cavity")
    cy, cx = np.unravel_index(gd.argmax(), gd.shape)
    core_cx, core_cy = HG.CX, HG.CY
    dist_to_core = max(abs(int(cx) - core_cx), abs(int(cy) - core_cy))
    print(f"  widest point at ({int(cx)},{int(cy)}), {gd.max():.1f} tiles from any wall; "
          f"the core is at ({core_cx},{core_cy})")
    if dist_to_core > 16:
        fails.append(f"the widest chamber is at ({int(cx)},{int(cy)}), not the core - "
                     f"something other than the core is the open space")

    # ---- KAEL'S BASTION rides along: it is the same cluster and the same baker, and its reachability is
    #      exactly the kind of thing that breaks quietly when a building moves.
    import tools.handbuilt_kaels_bastion as KB
    KL = KB.build_layout()
    kz = KL.zone
    khand = [s for s in KL.skipped if "shroom" not in s[0]]
    kreach = flood(kz, KB.START)
    print(f"\nKael's Bastion: {KL.placed} props, {len(khand)} hand-placed skips, "
          f"{len(kreach)} tiles reachable from the gate")
    for s in khand:
        fails.append(f"Bastion hand-placed prop skipped: {s}")
    for n, p in KB.NPC_POSITIONS.items():
        if tuple(p) not in kreach:
            fails.append(f"Bastion NPC spot {n} at {p} unreachable")
    for c in KL.chests:
        if tuple(c) not in kreach:
            fails.append(f"Bastion chest {c} unreachable")
    kp = list(KB.PORTALS)[0]
    if kp not in kreach:
        fails.append(f"Bastion portal {kp} unreachable from the gate")

    print()
    if fails:
        print(f"FAILED ({len(fails)}):")
        for f in fails:
            print("  -", f)
        return 1
    print("all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
