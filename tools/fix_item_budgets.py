#!/usr/bin/env python3
"""Bring the ilvl 26+ budget outliers onto the curve, keeping each item's character. Idempotent.

    PYTHONPATH=. python3 tools/fix_item_budgets.py [--check]

Kyle, 29 Oct 2026, on the 21 outliers tools/audit_item_budgets.py found above ilvl 26:
"yes please - i want gear to be unique, diverse, and have something for every class/spec but i also
love balance. i want any class to be viable"

So the rule here is: change the NUMBERS, never the identity. An item that was intellect-and-spirit
stays intellect-and-spirit; a polearm that was the agility polearm stays the agility polearm. What
changes is how much, and only where the formula says the item was mis-sized.

TWO DIFFERENT FAULTS, and they want different handling.

THIRTEEN WERE SHIELDS, every one of them at 1.26-1.33x of target and every one pure stamina. That
uniformity is the tell: somebody authored shields with a consistent rule that is not the generator's
rule. The generator spends 0.6 of a shield's stat budget on stamina and derives armor and block from
their own curves, so a shield's correct stamina is int(full_budget * 0.6). These are brought to that,
which costs each of them 1-3 stamina and nothing else - their armor and block values were already
right.

  If that trade is unwelcome, the honest alternative is to raise the generator's 0.6 rather than let
  thirteen hand-authored shields sit above a curve the other 62 sit on. One constant, one place.
  Nerfing the thirteen is the smaller change and the one that needs no balance decision, so it is
  what this does.

EIGHT WERE INDIVIDUAL MIS-SIZINGS. Two matter much more than the other six:

  Devourer's Barbed Spear   0.29x. A rare polearm off a Blackfathom boss carrying agi 8 / sta 5
                            against a 44.6 budget. A two-hander's budget multiplier is 1.8 and
                            whoever wrote this sized it like a one-hander, so it is currently worse
                            than the quest greens a player arrives with. This is the single worst
                            item in the game by this measure and fixing it is a real buff.
  Aku'mai's Deepwater Pearl 1.97x. From the same boss, in the other direction - a trinket at double
                            budget. One boss with one item at a third of target and another at
                            double suggests the table was written without a budget in mind at all.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("_aib", ROOT / "tools/audit_item_budgets.py")
_aib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_aib)

_SLOTS = _aib._SLOTS
_RARITY = _aib._RARITY
_WEAPONS = _aib._WEAPONS

#: item name -> new primary_stats. Proportions kept from the original; totals moved onto budget.
#: Each line says what the item is for, because "which class wants this" is the thing a bare number
#: loses.
NON_SHIELD_FIXES = {
    # 0.29x -> ~1.0x. The agility two-hander for a Hunter or a feral Druid at the Blackfathom
    # bracket. Tripling it is the point: at agi 8 / sta 5 it was losing to quest greens.
    "Devourer's Barbed Spear": {"agility": 27, "stamina": 17},
    # 1.97x -> ~1.0x. A healer trinket; keeps int > sta > spi, loses the inflation.
    "Aku'mai's Deepwater Pearl": {"intellect": 3, "stamina": 2, "spirit": 2},
    # 1.59x -> ~1.0x. Healing ring. healing_power costs 1.25 a point, which is most of why it was
    # over; the 3.1 stays because it is the item's whole character, so the primaries give way.
    "Grove Warden's Oath Ring": {"intellect": 2, "spirit": 1},
    # 1.42x -> ~1.0x. A Shaman/Hunter mail glove, strength-and-stamina.
    "Illyen's Tarred Gloves": {"stamina": 4, "strength": 2},
    # 0.62x -> ~1.0x. Plate legs for a Warrior or Paladin; it was sized like a minor slot.
    "Sentinel's Ashen Greaves": {"strength": 10, "stamina": 8},
    # 1.34x -> ~1.0x. Caster neck.
    "Grimtotem's Wardstone": {"intellect": 3, "stamina": 2},
    # 1.28x -> ~1.0x. Caster ring.
    "Nightmare-Touched Signet": {"intellect": 4, "stamina": 4},
    # 0.75x -> ~1.0x. Cloth shoulders for a healer.
    "Sanctum Warden's Mantle": {"intellect": 8, "spirit": 7},
    # 1.29x -> ~1.0x. An epic hybrid glove - agi and int together, which is unusual and worth
    # keeping. Its four secondaries cost 8.0 of the 13.1 budget, so the primaries come down.
    "Scavenger's Honest Grip": {"agility": 3, "intellect": 3},
}


def shield_target(item):
    """What a shield's stamina should be: 0.6 of its full stat budget, as the generator does it."""
    ilvl = item["item_level"]
    rm = _RARITY[item["rarity"]]["stat_budget_multiplier"]
    wd = _WEAPONS["weapon_types"]["shield"]
    sw = _SLOTS["weight_tiers"]["weapon_medium"]
    full = ilvl * _aib.BASE_MULT * rm * sw * wd["budget_multiplier"]
    # ROUND, do not truncate. The generator uses int(), which is why a generated ilvl-30 uncommon
    # shield also measures 0.84x of its own target - the truncation throws away up to a full point
    # on a budget of five. A hand-authored item is not obliged to reproduce that, and rounding
    # lands nearer the real number, so these come out at 0.95-1.05x instead of 0.84-0.97x.
    return max(1, round(full * 0.6))


def main():
    check = "--check" in sys.argv
    rows = _aib.collect()

    # name -> every (file, item) carrying it, since a name can appear in more than one table
    edits = []
    for _src, owner, item in rows:
        if item.get("item_level", 0) < 26:
            continue
        budget, _a, _d = _aib.budget_for(item)
        if not budget:
            continue
        ratio = _aib.spend(item) / budget
        if abs(ratio - 1.0) <= 0.25:
            continue
        if item.get("weapon_type") == "shield":
            want = shield_target(item)
            if want and item.get("primary_stats", {}).get("stamina") != want:
                edits.append((owner, item, {"stamina": want}, ratio, "shield -> 0.6 of budget"))
        elif item["name"] in NON_SHIELD_FIXES:
            edits.append((owner, item, NON_SHIELD_FIXES[item["name"]], ratio, "re-budgeted"))
        else:
            print(f"  UNHANDLED {ratio:.2f}x {item['name']!r} [{owner}] - add it to NON_SHIELD_FIXES")

    print(f"{len(edits)} item(s) to re-budget\n")
    for owner, item, new, ratio, why in sorted(edits, key=lambda e: -abs(e[3] - 1)):
        before = item.get("primary_stats")
        probe = dict(item)
        probe["primary_stats"] = new
        budget, _a, _d = _aib.budget_for(probe)
        after = _aib.spend(probe) / budget
        print(f"  {ratio:5.2f}x -> {after:4.2f}x  {item['name']:34} {before}  ->  {new}   ({why})")

    if check:
        return 1 if edits else 0
    if not edits:
        print("nothing to do")
        return 0

    # Apply by rewriting each touched file, matching on item name within it.
    wanted = {}
    for owner, item, new, _r, _w in edits:
        wanted.setdefault(owner.split("/")[0], {})[item["name"]] = new

    touched = 0
    for path in list((ROOT / "data/quests").glob("*.json")) + list((ROOT / "data/loot").glob("*.json")):
        if path.stem not in wanted:
            continue
        doc = json.loads(path.read_text())
        names = wanted[path.stem]
        hit = 0

        def walk(items):
            nonlocal hit
            for it in items:
                if isinstance(it, dict) and it.get("name") in names:
                    it["primary_stats"] = dict(names[it["name"]])
                    hit += 1

        for quest in doc.get("quests", []):
            walk(quest.get("unique_item_defs") or [])
            walk(quest.get("rewards") or [])
        rows_ = doc.get("bosses", doc)
        if isinstance(rows_, dict):
            for owner_name, items in rows_.items():
                if not owner_name.startswith("_") and isinstance(items, list):
                    walk(items)
        if hit:
            path.write_text(json.dumps(doc, indent=2) + "\n")
            touched += 1
            print(f"  wrote {path.name} ({hit} item(s))")

    print(f"\n{touched} file(s) updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
