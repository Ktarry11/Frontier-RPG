#!/usr/bin/env python3
"""Which abilities and talents have real art, and which only look like they do.

WHY THIS IS NOT A ONE-LINE `ls | wc`. There are THREE states, not two, and
counting the wrong pair gives a confidently wrong answer - which it did
twice while this was first measured by hand:

  OWN ART      a PNG exists named after the ability_id/talent_id (or the
               explicit icon_id). This is the goal state.
  BLANK        no PNG matches, so IconRenderer falls through to
               _make_fallback_surface and the player sees a flat coloured
               square.
  SHARED       an explicit icon_id points at a real file that dozens or
               hundreds of OTHER abilities also point at - almost always
               "ability_melee", which is the default in several
               tools/build_<class>.py `ability()` helpers. These render
               perfectly and are invisible to any "does the file exist"
               check, yet 190 abilities drawing the same sword means a
               hotbar of identical buttons.

Two measurement traps, both hit while writing this:

  - `icon_id: null` is NOT a missing icon. icon_migration_and_ui.py's
    get_ability_icon_surface defaults icon_id to ability_id on purpose, and
    the art is named to match, so 570 abilities with a null icon_id were
    already rendering their own art. Treating null as missing produced a
    "1059 missing icons" figure and a plan to stamp 570 redundant icon_id
    values into JSON.
  - a talent's id field is `talent_id`. Reading `node_id` or `id` returns
    None for every node, every node then gets skipped, and the tool reports
    a triumphant 0 missing across all 2306 talents.

    python3 tools/audit_icon_coverage.py
    python3 tools/audit_icon_coverage.py --class barbarian
    python3 tools/audit_icon_coverage.py --list barbarian
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Every directory IconRenderer.get_icon_surface tries, in its own order.
#: Kept in sync with that method - if it gains a directory and this does
#: not, this tool starts reporting art that exists as missing.
ICON_DIRS = ("abilities", "talents", "bags", "gear", "vendor_trash",
             "quest_items", "consumables", "recipes")

#: An icon_id used by more than this many things is a shared placeholder
#: rather than that thing's own art.
SHARED_THRESHOLD = 3


def class_slugs():
    """The real class slugs, longest first so a prefix match is unambiguous."""
    slugs = {p.stem for p in (ROOT / "data/abilities").glob("*.json")}
    return sorted(slugs, key=len, reverse=True)


def class_of_tree(stem):
    """Which class a talent tree file belongs to.

    Splitting the filename on "_" and taking the first piece is wrong for
    every class whose slug contains an underscore, and four of them do:
    knight_of_xoroth_war became "knight", witch_hunter_boltslinger and
    witch_doctor_voodoo both became "witch" (merging two unrelated classes
    into one row of 161), and sun_cleric_piety became "sun". The totals
    were right and the per-class table was nonsense, which is the kind of
    error that survives review because the number at the bottom checks out.
    """
    for slug in class_slugs():
        if stem == slug or stem.startswith(slug + "_"):
            return slug
    return stem.split("_")[0]


def on_disk():
    have = set()
    for d in ICON_DIRS:
        p = ROOT / "assets/icons" / d
        if p.exists():
            have |= {x.stem for x in p.glob("*.png")}
    return have


def collect():
    """Return (rows, icon_id_usage). A row is (kind, cls, ident, icon_id)."""
    rows, usage = [], Counter()
    for f in sorted((ROOT / "data/abilities").glob("*.json")):
        for a in json.loads(f.read_text(encoding="utf-8")).get("abilities", []):
            key = a.get("icon_id") or a["ability_id"]
            rows.append(("ability", f.stem, a["ability_id"], a.get("icon_id")))
            usage[key] += 1
    for f in sorted((ROOT / "data/talents").glob("*.json")):
        nodes = json.loads(f.read_text(encoding="utf-8")).get("nodes") or []
        if isinstance(nodes, dict):
            nodes = list(nodes.values())
        for n in nodes:
            # `talent_id`, not `node_id` and not `id` - see the module
            # docstring for what reading the wrong one costs.
            tid = n.get("talent_id")
            if not tid:
                continue
            key = n.get("icon_id") or tid
            rows.append(("talent", class_of_tree(f.stem), tid, n.get("icon_id")))
            usage[key] += 1
    return rows, usage


def classify(rows, usage, have):
    out = defaultdict(lambda: {"own": 0, "blank": 0, "shared": 0,
                               "blank_ids": [], "shared_ids": []})
    for kind, cls, ident, icon_id in rows:
        key = icon_id or ident
        bucket = out[cls]
        if key not in have:
            bucket["blank"] += 1
            bucket["blank_ids"].append(ident)
        elif icon_id and usage[key] > SHARED_THRESHOLD:
            bucket["shared"] += 1
            bucket["shared_ids"].append(f"{ident} -> {icon_id}")
        else:
            bucket["own"] += 1
    return out


def main(argv):
    only = argv[argv.index("--class") + 1] if "--class" in argv else None
    listing = argv[argv.index("--list") + 1] if "--list" in argv else None
    have = on_disk()
    rows, usage = collect()
    table = classify(rows, usage, have)

    if listing:
        b = table.get(listing)
        if not b:
            print(f"no class {listing!r}")
            return 1
        print(f"{listing}: {b['blank']} blank, {b['shared']} shared, "
              f"{b['own']} with own art\n")
        if b["blank_ids"]:
            print("BLANK - renders a flat coloured square:")
            for i in sorted(b["blank_ids"]):
                print(f"    {i}")
        if b["shared_ids"]:
            print("\nSHARED - renders, but the same image as many others:")
            for i in sorted(b["shared_ids"]):
                print(f"    {i}")
        return 0

    keys = [only] if only else sorted(table)
    print(f"{'class':18} {'blank':>7} {'shared':>7} {'own art':>8} {'total':>7}")
    print("-" * 52)
    tb = ts = to = 0
    for k in keys:
        b = table[k]
        n = b["blank"] + b["shared"] + b["own"]
        tb += b["blank"]
        ts += b["shared"]
        to += b["own"]
        print(f"{k:18} {b['blank']:>7} {b['shared']:>7} {b['own']:>8} {n:>7}")
    print("-" * 52)
    print(f"{'TOTAL':18} {tb:>7} {ts:>7} {to:>8} {tb+ts+to:>7}")

    print(f"\n{tb} BLANK - no PNG matches, so the player sees a coloured square.")
    print(f"{ts} SHARED - renders someone else's generic art. Biggest offenders:")
    for key, n in usage.most_common(6):
        if n > SHARED_THRESHOLD and key in have:
            print(f"    {key:24} {n:>4} things draw this one image")
    print(f"\nSheets needed at 48 icons per sheet: {-(-(tb + ts) // 48)}")
    print("\nNOTE: a null icon_id is NOT a gap - the UI defaults it to the")
    print("ability_id/talent_id and the art is named to match. Only a")
    print("missing FILE is a gap. See this tool's docstring.")
    return 1 if tb else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
