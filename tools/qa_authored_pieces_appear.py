"""Things a zone's builder asked for that are not in the zone at all.

The layout kits refuse a placement that lands on water, a road, an NPC or a door, and only
note it in `L.skipped`, which nothing read. Losing one tuft of a scatter is fine. Losing the
ONLY copy of something is a building that was authored and is not in the game - Brill had a
forge tile and no smithy; Orgrimmar had no tannery or warlock tower; Razor Hill no well.

This prints every piece whose name appears nowhere on its finished map, and holds the count
to a ceiling so it can only fall. The ones left need siting by eye (Hammerfall is the worst).
"""
import collections
import glob
import importlib
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)

#: Pieces missing today. Lower it when you site some; never raise it.
CEILING = 133
#: Early-game towns must have every building they were given.
MUST_BE_WHOLE = ("brill", "razor_hill", "orgrimmar", "durotar", "deathknell", "undercity", "vot")


def stem(name):
    return os.path.basename(str(name)).replace(".png", "")


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))
    missing, bad = collections.OrderedDict(), []
    for path in sorted(glob.glob("tools/handbuilt_*.py")):
        mod = os.path.basename(path)[:-3]
        try:
            m = importlib.import_module(mod)
            if not hasattr(m, "build_layout"):
                continue
            L = m.build_layout()
            L = L[0] if isinstance(L, tuple) else L
        except Exception:
            continue                      # builders with their own shape are checked elsewhere
        skipped = getattr(L, "skipped", None)
        if not skipped:
            continue
        have = {stem(l["sprite_key"]) for l in getattr(L.z, "landmarks", [])}
        gone = sorted({(stem(s[0]), s[1], s[2], str(s[3])[:24]) for s in skipped
                       if stem(s[0]) not in have and "chest" not in stem(s[0])})
        if gone:
            missing[mod[10:]] = gone
    total = sum(len(v) for v in missing.values())
    for zone, gone in missing.items():
        print(f"  {zone:24s} {len(gone):3d}  " + ", ".join(f"{g[0]} ({g[3]})" for g in gone[:6])
              + (" ..." if len(gone) > 6 else ""))
        if zone in MUST_BE_WHOLE:
            bad.append(f"{zone} is missing {[g[0] for g in gone]}")
    print(f"\n{total} authored pieces appear nowhere on their map (ceiling {CEILING})")
    if total > CEILING:
        bad.append(f"{total} missing pieces, ceiling is {CEILING}")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nauthored pieces OK - the early towns are whole and the count has not grown.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
