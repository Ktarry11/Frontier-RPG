#!/usr/bin/env python3
"""Give every clashing icon in fetch_coa_icons.MAPPING its own hue.

    python3 tools/dedupe_icon_mapping.py --class bloodmage          # report
    python3 tools/dedupe_icon_mapping.py --class bloodmage --apply  # rewrite

WHY THIS EXISTS. Kyle, on the first Barbarian set: "don't forget you can
rehue them slightly. And ensure you don't only use 1 icon per class." The
fetcher already refuses to install two ids whose final bytes match, which
turns the problem into a visible list - but that list ran to 26 entries for
Barbarian and 40 for Bloodmage, and hand-editing it for each of thirteen
classes is exactly the kind of repetitive judgement that gets sloppy by
class four.

THE CONVENTION IT APPLIES, which is why this can be automatic at all:

A talent that improves one specific ability SHOULD share that ability's
art. That is real WoW practice and it tells the player what the talent
touches. So a clash between a TALENT and an ABILITY is not an error to
resolve by picking different art - it is the right pairing, and all it
needs is for the talent to be a recoloured version so the two are not
literally the same file. Trip to the Alehouse becomes a tinted Keg Smash;
Overkill becomes a tinted Decapitate.

So: the ABILITY always keeps the base art, and the TALENT gets the hue.
When both sides are talents, or both abilities, the one that sorts later
gets the hue - arbitrary, but stable, so re-running does not churn.

HUES ARE CHOSEN, NOT GUESSED. Each candidate hue is fetched, recoloured
and hashed, and only accepted if the result is unique across everything
already assigned. A hue that happens to land on an existing image is
skipped. If no hue in the ladder works, the id is reported for a manual
pick rather than quietly left colliding.

Every fetch is cached in memory for the run, so a 157-id class costs one
request per distinct icon name rather than one per candidate hue.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

TOOL = ROOT / "tools/fetch_coa_icons.py"

#: Tried in order. 40 degrees is a clear shift without turning blood green;
#: the later values are for the rare icon reused three or more times.
HUE_LADDER = (40, 200, 280, 120, 320, 80, 160, 240)


def talent_ids():
    import json
    out = set()
    for f in (ROOT / "data/talents").glob("*.json"):
        nodes = json.loads(f.read_text()).get("nodes") or []
        if isinstance(nodes, dict):
            nodes = list(nodes.values())
        for n in nodes:
            if n.get("talent_id"):
                out.add(n["talent_id"])
    return out


def main(argv):
    import fetch_coa_icons as F

    apply = "--apply" in argv
    only = argv[argv.index("--class") + 1] if "--class" in argv else None
    items = sorted(F.MAPPING.items())
    if only:
        items = [(k, v) for k, v in items if k.startswith(only)]
    if not items:
        print("nothing mapped")
        return 1

    talents = talent_ids()
    cache: dict[tuple[str, int], str] = {}

    def digest(name, hue):
        key = (name, hue)
        if key not in cache:
            cache[key] = hashlib.sha1(F.fetch(name, hue)).hexdigest()
        return cache[key]

    # First pass: what does each id currently resolve to?
    cur = {}
    for ident, value in items:
        name, hue = (value if isinstance(value, tuple) else (value, 0))
        try:
            cur[ident] = (name, hue, digest(name, hue))
        except Exception as exc:                               # noqa: BLE001
            print(f"SKIP (name is wrong, fix it first): {ident} -> {name}"
                  f"  {str(exc)[:50]}")
    taken: dict[str, str] = {}
    clashes = []
    for ident in sorted(cur):
        name, hue, d = cur[ident]
        if d in taken:
            clashes.append((ident, taken[d]))
        else:
            taken[d] = ident

    if not clashes:
        print(f"{len(cur)} ids, {len(taken)} distinct images, nothing to do")
        return 0

    # Decide which side of each clash moves. The ability keeps the base.
    changes = {}
    unresolved = []
    for later, earlier in clashes:
        mover = later
        if later not in talents and earlier in talents:
            # `later` is the ability - move the talent instead, and give
            # the ability the base art it should have had.
            mover = earlier
        name, _, _ = cur[mover]
        for hue in HUE_LADDER:
            try:
                d = digest(name, hue)
            except Exception:                                  # noqa: BLE001
                continue
            if d not in taken:
                taken[d] = mover
                changes[mover] = (name, hue)
                break
        else:
            unresolved.append(mover)

    print(f"{len(cur)} ids -> {len(changes)} recoloured, "
          f"{len(unresolved)} need a different icon by hand\n")
    for ident, (name, hue) in sorted(changes.items()):
        kind = "talent " if ident in talents else "ability"
        print(f"    {kind} {ident:50} {name} hue {hue}")
    for ident in unresolved:
        print(f"    UNRESOLVED {ident} - no hue in the ladder was unique")

    if not apply:
        print("\n(report only; pass --apply to rewrite the mapping)")
        return 1 if unresolved else 0

    src = TOOL.read_text()
    for ident, (name, hue) in changes.items():
        pat = re.compile(r'("%s":\s*)(\([^)]*\)|"[^"]*")' % re.escape(ident))
        src, n = pat.subn(lambda m: f'{m.group(1)}("{name}", {hue})', src, count=1)
        if n != 1:
            print(f"WARNING: could not rewrite {ident}")
    TOOL.write_text(src)
    print(f"\nrewrote {len(changes)} entries in {TOOL.name}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
