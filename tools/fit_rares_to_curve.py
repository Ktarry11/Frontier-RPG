#!/usr/bin/env python3
"""Put Felwood's, Tempest Isle's and the Plaguelands' drops on the item curve.

    PYTHONPATH=. python3 tools/fit_rares_to_curve.py --dry-run
    PYTHONPATH=. python3 tools/fit_rares_to_curve.py

Kyle, 16 Nov 2026: "So if the item score is too weak we can improve it bro. We can look at the Felwood, Tempest
Isle and the plaguelands all at once."

WHAT WAS WRONG. The open-world rares in these zones were built by LootGenerator, which spends a budget as a plain
sum split by whichever suffix it rolled. The curve (entities/item_budget.py) reads stats through the 1.5 / 2-3 norm,
so the same budget lands anywhere from a tenth of the line to on it. Felwood's rares sat at a median of 0.71 of
their budget and the Plaguelands' at 0.62 to 0.69, against 0.95 for the game's loot as a whole. Tempest Isle's were
mostly fine, with a handful far off.

WHAT THIS DOES.
  * The generated rare tables (GENERATED) go onto the line exactly: every item at 1.0. A generated rare that
    rolled no stat its template exists for (Stamina-only gloves on a caster template, resistance and healing on
    a wand) gets its template's lead stat first, at the size of its biggest stat, so the scale-up makes an item
    somebody wants rather than 28 Stamina.
  * The hand-authored tables (AUTHORED: these zones' boss loot and quest rewards) keep their author's spread and
    only items outside the audit's band (0.65 to 1.45, tools/audit_item_curve.py) move, to 1.0.
Budget is linear in a uniform multiply, so this keeps each item's stat mix. Weapon damage, speed and armour don't
move. See entities/item_budget.fit_to_curve.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.item_budget import RARITY_MULT, budget_ratio, fit_to_curve  # noqa: E402

GENERATED = [
    "data/loot/felwood_rare_loot.json",
    "data/loot/tempest_isle_rare_loot.json",
    "data/loot/plaguelands_rare_loot.json",
    "data/loot/plaguelands_east_rare_loot.json",
]
AUTHORED = [
    "data/loot/tempest_isle_boss_loot.json",
    "data/quests/felwood.json",
    "data/quests/tempest_shallows.json",
]
LOW, HIGH = 0.65, 1.45

#: What each template exists to deliver (LootGenerator._TEMPLATE_LEAD); a healer's lead is Intellect here.
LEAD = {"str_physical": ["strength"], "agi_physical": ["agility"], "int_caster": ["intellect"],
        "spi_healer": ["intellect"], "str_int_hybrid": ["strength", "intellect"],
        "agi_int_hybrid": ["agility", "intellect"]}


def give_lead(it):
    """Add the template's lead stat to an item that rolled none of it. True if it changed."""
    lead = LEAD.get(it.get("stat_template"))
    prim = it.setdefault("primary_stats", {}) or {}
    it["primary_stats"] = prim
    if not lead or any(prim.get(s) for s in lead):
        return False
    vals = [v for g in ("primary_stats", "secondary_stats") for v in (it.get(g) or {}).values()
            if isinstance(v, (int, float))]
    size = max([5] + [int(round(v)) for v in vals])
    for s in lead:
        prim[s] = size
    return True


def _items(o):
    if isinstance(o, dict):
        if o.get("item_level") and o.get("rarity") in RARITY_MULT and (
                o.get("primary_stats") or o.get("secondary_stats")):
            yield o
        for v in o.values():
            yield from _items(v)
    elif isinstance(o, list):
        for v in o:
            yield from _items(v)


def _fmt(raw):
    """Match the file's own indent and trailing newline."""
    indent = 2
    for line in raw.splitlines()[1:]:
        if line.strip():
            indent = len(line) - len(line.lstrip(" "))
            break
    return indent, raw.endswith("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    total = 0
    for rel, every in [(f, True) for f in GENERATED] + [(f, False) for f in AUTHORED]:
        path = ROOT / rel
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        moved, led = [], 0
        for it in _items(data):
            if every:
                led += give_lead(it)
            r = budget_ratio(it)
            if r is None:
                continue
            if not every and LOW <= r <= HIGH:
                continue
            if every and abs(r - 1.0) < 0.03:
                continue
            res = fit_to_curve(it)
            if res:
                moved.append((it["name"], res[0], res[1]))
        total += len(moved)
        print(f"{rel}: {len(moved)} moved" + (f", {led} given their template's lead stat" if led else ""))
        for n, b, af in sorted(moved, key=lambda m: m[1])[:6]:
            print(f"    {n:38s} {b:5.2f} -> {af:4.2f}")
        if (moved or led) and not a.dry_run:
            indent, nl = _fmt(raw)
            path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if nl else ""),
                            encoding="utf-8")
    print(f"{total} items {'would move' if a.dry_run else 'moved'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
