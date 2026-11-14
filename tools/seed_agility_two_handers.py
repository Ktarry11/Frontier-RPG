#!/usr/bin/env python3
"""Give two-handed swords and maces an agility line. Idempotent.

    PYTHONPATH=. python3 tools/seed_agility_two_handers.py [--check]

Kyle, 29 Oct 2026: "there should be polearms and a few 2H swords with agi. there should be agi
swords anyways as rogues can use swords. Also an agi 2H mace works for druid tanks."

THE CENSUS THAT PROVED HIM RIGHT. Counting every hand-authored weapon by its lead primary stat:

    sword_2h    21 authored,  0 agility   - the generator ALLOWS agility and nobody ever used it
    mace_2h     33 authored,  0 agility   - the generator did not allow it at all

sword_2h has carried agi_physical in its valid_stat_templates the whole time. The gap was never an
engine limit, it was that no author reached for it. mace_2h genuinely was blocked: str_physical and
int_caster only, so a feral druid wanting a two-hander had polearms and staves and nothing else.
That one word is added to data/items/weapon_types.json separately.

WHICH ITEMS, AND WHY NOT A SWEEP. Converting strength to agility costs nothing in budget - both
stats price at 1.0 in gear_suffixes.json - so a straight key rename keeps every item exactly on
curve. That makes it tempting to convert by the dozen, which would be wrong: a maul whose entire
joke is its weight is not secretly an agility weapon, and renaming its stat makes the item worse,
not more diverse. So each one below is picked because its NAME AND FLAVOUR ALREADY READ AS AGILITY,
and the reason is recorded next to it.

TWO I PICKED AND THEN PUT BACK. Pathfinder's Glaive ("cut for someone who walks and does not
rattle") and Skum's Tail-Club read as agility weapons from their names, and both turned out to carry
no strength at all: the Glaive spends its whole 19-point budget on dodge and parry, and the Tail-Club
on stamina, armor and parry. They are avoidance two-handers, already on budget at 0.99x and 1.01x,
and "converting" either would mean restructuring a correct item to satisfy a census. Left alone.

The ones deliberately left on strength are the ones whose identity is force: Gruzak's Splitting
Maul ("heavy as a stump and smells like one"), Kragg's Battering Maul ("it breaks walls"),
Stead-Breaker Maul ("the Nethanders built that barn in a season; this took an hour"),
Shelf-King's Roadbreaker, Pen-Breaker's Maul ("hits like a collapsing corral"). Those are correct
as written.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: item name -> (weapon_type, why this one). Spread over level bands on purpose: an agility
#: two-hander that only exists at ilvl 43 does not help anybody levelling.
CONVERT = {
    # ---- sword_2h: 0 of 21 were agility ---------------------------------------------------------
    "Warden's Moonglaive": (
        "sword_2h", "ilvl23 - a sentinel's curved glaive that 'sings in the moonlight'"),
    "Ilthae's Moonglaive": (
        "sword_2h", "ilvl23 - 'cuts cleaner than it should', the boss-drop twin of the above"),
    "Brood-Slayer's Blade": (
        "sword_2h", "ilvl26 - 'the edge is chitin-fine', ground from a claw: precision, not mass"),
    "Razorjaw's Serrated Edge": (
        "sword_2h", "ilvl17 - a tooth in a driftwood hilt, 'it bites the way it was grown to'"),
    "Lamed Outrider's Glaive": (
        "sword_2h", "ilvl15 - 'balanced for a rider with one good leg', and balance is the point"),

    # ---- mace_2h: 0 of 33, and the type was blocked ----------------------------------------------
    "Hexbreaker's Maul": (
        "mace_2h", "ilvl18 - petrified mangrove, made to unmake hexes: the druid weapon Kyle asked "
                   "for, and it was already written as one in everything but its stats"),
    "Fenrus' Devouring Maw": (
        "mace_2h", "ilvl27 - a jaw-shaped head with real teeth; a bite, not a hammer"),
    "Brontus's Horn-Hewn Greatclub": (
        "mace_2h", "ilvl27 - cut from a single giant horn"),
    "Hoofbeat Maul": (
        "mace_2h", "ilvl17 - 'a hoof, a haft and a lot of upward momentum'"),
}


def convert(item):
    """strength -> agility, budget untouched. Returns True if anything changed."""
    primary = item.get("primary_stats") or {}
    if "strength" not in primary:
        return False
    moved = primary.pop("strength")
    primary["agility"] = primary.get("agility", 0) + moved
    item["primary_stats"] = primary
    if item.get("stat_template") == "str_physical":
        item["stat_template"] = "agi_physical"
    return True


def main():
    check = "--check" in sys.argv

    import importlib.util
    spec = importlib.util.spec_from_file_location("_aib", ROOT / "tools/audit_item_budgets.py")
    aib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aib)

    # Refuse to run if the engine does not allow what we are about to author - an agility mace the
    # generator rejects is data that contradicts its own schema.
    wt = json.loads((ROOT / "data/items/weapon_types.json").read_text(encoding="utf-8"))["weapon_types"]
    for name, (wtype, _why) in CONVERT.items():
        allowed = wt[wtype].get("valid_stat_templates") or []
        if "agi_physical" not in allowed:
            raise SystemExit(
                f"{wtype} does not list agi_physical in valid_stat_templates, so {name!r} would be "
                f"invalid data. Add it there first.")

    targets = {n for n in CONVERT}
    found, planned = {}, []
    for _src, owner, item in aib.collect():
        if item.get("name") not in targets:
            continue
        if item.get("weapon_type") != CONVERT[item["name"]][0]:
            continue
        found.setdefault(item["name"], []).append(owner)
        primary = item.get("primary_stats") or {}
        if "strength" in primary:
            before = aib.spend(item)
            probe = json.loads(json.dumps(item))
            convert(probe)
            planned.append((item["name"], owner, dict(primary), probe["primary_stats"],
                            before, aib.spend(probe)))

    missing = targets - set(found)
    if missing:
        print(f"NOT FOUND in any table: {sorted(missing)}")

    print(f"{len(planned)} item(s) to convert\n")
    for name, owner, before, after, sb, sa in planned:
        tag = "" if abs(sb - sa) < 1e-9 else f"   BUDGET MOVED {sb:.1f} -> {sa:.1f}"
        print(f"  {name:34} {before}  ->  {after}{tag}")
        print(f"      {CONVERT[name][1]}")
    if any(abs(sb - sa) > 1e-9 for *_x, sb, sa in planned):
        raise SystemExit("a conversion moved an item's budget - refusing to write")

    if check:
        return 1 if planned else 0
    if not planned:
        print("nothing to do")
        return 0

    names = {n for n, *_ in planned}
    touched = 0
    for path in list((ROOT / "data/quests").glob("*.json")) + list((ROOT / "data/loot").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        hit = 0

        def walk(items):
            nonlocal hit
            for it in items:
                if (isinstance(it, dict) and it.get("name") in names
                        and it.get("weapon_type") == CONVERT[it["name"]][0]):
                    if convert(it):
                        hit += 1

        for quest in doc.get("quests", []):
            walk(quest.get("unique_item_defs") or [])
            walk(quest.get("rewards") or [])
        rows = doc.get("bosses", doc)
        if isinstance(rows, dict):
            for owner, items in rows.items():
                if not owner.startswith("_") and isinstance(items, list):
                    walk(items)
        if hit:
            path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            touched += 1
            print(f"  wrote {path.name} ({hit})")

    print(f"\n{touched} file(s) updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
