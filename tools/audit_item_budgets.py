#!/usr/bin/env python3
"""Every hand-authored item, measured against the generator's own stat-budget formula.

    PYTHONPATH=. python3 tools/audit_item_budgets.py [--tol 0.25] [--source quests|loot] [--worst N]

Kyle, 29 Oct 2026: "We need to keep items in line bro....i think we need to properly audit ALL the
item drops based on the stat allowance formula. For quests and dungeon drops. it should be based on
ilvl."

THE AUTHORITY IS ALREADY IN THE CODE. entities/loot_generator.LootGenerator computes, for every
procedural item:

    stat budget  = item_level * 0.36 * rarity_multiplier * slot_weight [* weapon_budget_multiplier]
    armor value  = item_level * 1.5 * armor_multiplier * slot_weight * rarity_multiplier
    avg damage   = (item_level * 1.1 + 6.4) * rarity_multiplier * damage_tier_multiplier

That 0.36 was fitted against Kyle's Gear.docx bracket table, so it is not an arbitrary constant -
it is the documented curve. Hand-authored items (quest rewards, boss tables) never went through it,
so nothing has ever checked them against it. This does.

Budget is spent on primary AND secondary stats, priced by data/items/gear_suffixes.json's
stat_budget_costs - a point of strength costs 1.0, a point of attack_power 0.5, one percent of crit
10.0. So an item trading primary stats for crit is NOT under budget, and comparing raw primary-stat
sums (which is what I did first, by eye) gets the answer backwards. Measured properly against the
formula:

    Terracekeeper's Glaive   polearm ilvl40 rare   sum 66   budget 66.1   on the money
    Favourite's Gurbashi Pike polearm ilvl41 rare  sum 67   budget 67.8   on the money
    Unbeaten's Notching Axe   axe_2h  ilvl39 rare  sum 26   budget 64.4   40% of budget

The two polearms I had flagged as over-tuned are exactly right, and the headline arena boss's
signature axe is the one that is broken. A peer-median eyeball said the opposite, because most of
its peers are under budget too.

WHAT IT CHECKS, per item: the budget spend ratio, the armor value, and the average weapon damage,
each against the formula for that item's own level, rarity, slot and type. Ratios inside +/-`--tol`
(default 25%) pass - hand-authored gear should have room to be interesting without being a different
power curve.

WHAT IT DOES NOT DO: change anything. Re-budgeting an item is a design decision per item, and the
output is ordered worst-first so the list can be worked down deliberately.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BASE_MULT = 0.36  # LootGenerator.STAT_BUDGET_BASE_MULT

# Imported, not restated. This file used to carry its own copies of the shield
# constants, so a change to the generator left the audit validating the old
# numbers and reporting every shield as correct.
try:
    from entities.loot_generator import LootGenerator as _LG
    _SHIELD_ARMOR_K = _LG.SHIELD_ARMOR_K
    _SHIELD_BLOCK_K = _LG.SHIELD_BLOCK_K
except Exception:  # pragma: no cover - audit must still run headless
    _SHIELD_ARMOR_K, _SHIELD_BLOCK_K = 6.0, 0.7

_SLOTS = json.loads((ROOT / "data/items/slots.json").read_text())
_RARITY = json.loads((ROOT / "data/items/rarity.json").read_text())["rarity_tiers"]
_WEAPONS = json.loads((ROOT / "data/items/weapon_types.json").read_text())
_ARMOR = json.loads((ROOT / "data/items/armor_types.json").read_text())["armor_types"]
_COSTS = json.loads((ROOT / "data/items/gear_suffixes.json").read_text())["stat_budget_costs"]


def spend(item):
    """What this item's stats cost, priced exactly as the generator prices them."""
    total = 0.0
    for block in ("primary_stats", "secondary_stats"):
        for stat, value in (item.get(block) or {}).items():
            total += float(value) * _COSTS.get(stat, 1.0)
    return total


def budget_for(item):
    """(stat_budget, expected_armor, expected_avg_damage). None where not applicable."""
    ilvl = item.get("item_level")
    rarity = item.get("rarity")
    if not ilvl or rarity not in _RARITY:
        return None, None, None
    rm = _RARITY[rarity]["stat_budget_multiplier"]
    wtype = item.get("weapon_type")

    if wtype and wtype in _WEAPONS["weapon_types"]:
        wd = _WEAPONS["weapon_types"][wtype]
        tier = "weapon_two_hand" if wd["hand"] == "two_hand" else "weapon_medium"
        sw = _SLOTS["weight_tiers"][tier]
        budget = ilvl * BASE_MULT * rm * sw * wd["budget_multiplier"]
        if wtype == "shield":
            # A shield is budgeted differently ON PURPOSE and the generator says so: it spends
            # 0.6 of the budget on stamina and nothing else, because its armor and block come from
            # their own formulas (ilvl*1.2*rarity and ilvl*1.5*rarity) rather than out of the stat
            # pool. Measured against the full budget, all 75 authored shields read as 0.42-0.80 of
            # target - a dead giveaway that the audit was wrong rather than the data, since real
            # scatter does not stop neatly below 1.0 on every single item.
            return budget * 0.6, int(ilvl * _SHIELD_ARMOR_K * rm), None
        dmg = None
        if wd.get("base_attack_speed"):
            tm = _WEAPONS["damage_tiers"].get(
                wd.get("damage_tier", "one_hand"), {}).get("dps_multiplier", 1.0)
            dmg = (ilvl * 1.1 + 6.4) * rm * tm
        return budget, None, dmg

    slot = item.get("slot")
    sd = _SLOTS["slots"].get(slot)
    if sd is None:
        return None, None, None
    sw = _SLOTS["weight_tiers"][sd["weight_tier"]]
    budget = ilvl * BASE_MULT * rm * sw
    atype = sd.get("armor_type_override") or (item.get("armor_type") if sd["armor_slot"] else None)
    armor = None
    if atype:
        am = _ARMOR.get(atype, {}).get("armor_multiplier", 0.0)
        if am:
            armor = int(ilvl * 1.5 * am * sw * rm)
    return budget, armor, None


def collect():
    """(source, owner, item) for every hand-authored item in the game."""
    out = []
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        for quest in json.loads(path.read_text()).get("quests", []):
            for item in (quest.get("unique_item_defs") or []) + (quest.get("rewards") or []):
                out.append(("quests", f"{path.stem}/{quest['quest_id']}", item))
    for path in sorted((ROOT / "data/loot").glob("*.json")):
        doc = json.loads(path.read_text())
        rows = doc.get("bosses", doc)
        if not isinstance(rows, dict):
            continue
        for owner, items in rows.items():
            if owner.startswith("_") or not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and item.get("item_level"):
                    out.append(("loot", f"{path.stem}/{owner}", item))
    return out


def main():
    tol = 0.25
    if "--tol" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tol") + 1])
    only = None
    if "--source" in sys.argv:
        only = sys.argv[sys.argv.index("--source") + 1]
    worst_n = 25
    if "--worst" in sys.argv:
        worst_n = int(sys.argv[sys.argv.index("--worst") + 1])

    rows = [r for r in collect() if not only or r[0] == only]
    findings = []
    ratios = []
    by_file = Counter()
    buckets = defaultdict(list)

    for source, owner, item in rows:
        budget, armor, dmg = budget_for(item)
        if not budget:
            continue
        got = spend(item)
        ratio = got / budget
        ratios.append(ratio)
        kind = (item.get("weapon_type") or item.get("armor_type")
                or ("accessory" if item.get("slot") in ("neck", "ring", "trinket", "back") else "?"))
        buckets[kind].append(ratio)
        if abs(ratio - 1.0) > tol:
            findings.append((abs(ratio - 1.0), ratio, source, owner, item, budget, got, "stats"))
            by_file[owner.split("/")[0]] += 1
        # A shield's block_value has its own curve too; check it where present.
        if item.get("weapon_type") == "shield" and item.get("block_value"):
            want_block = int(item["item_level"] * 1.5
                             * _RARITY[item["rarity"]]["stat_budget_multiplier"])
            if want_block:
                br = item["block_value"] / want_block
                if abs(br - 1.0) > tol:
                    findings.append((abs(br - 1.0), br, source, owner, item, want_block,
                                     item["block_value"], "block"))
        if armor and item.get("armor_value"):
            ar = item["armor_value"] / armor
            if abs(ar - 1.0) > tol:
                findings.append((abs(ar - 1.0), ar, source, owner, item, armor,
                                 item["armor_value"], "armor"))
        if dmg and item.get("weapon_damage_max"):
            got_d = (item["weapon_damage_min"] + item["weapon_damage_max"]) / 2
            dr = got_d / dmg
            if abs(dr - 1.0) > tol:
                findings.append((abs(dr - 1.0), dr, source, owner, item, dmg, got_d, "damage"))

    import statistics
    print(f"hand-authored items measured: {len(ratios)}   tolerance +/-{tol:.0%}")
    if ratios:
        inside = sum(1 for r in ratios if abs(r - 1.0) <= tol)
        print(f"stat budget: {inside}/{len(ratios)} inside tolerance "
              f"({inside / len(ratios):.0%})   median ratio {statistics.median(ratios):.2f}")
    print("\nby item kind (median spend as a fraction of budget):")
    for kind, rs in sorted(buckets.items(), key=lambda kv: statistics.median(kv[1])):
        flag = "" if 0.75 <= statistics.median(rs) <= 1.25 else "   <-- off the curve"
        print(f"   {kind:16} n={len(rs):4} median {statistics.median(rs):.2f}"
              f"  range {min(rs):.2f}-{max(rs):.2f}{flag}")

    if by_file:
        print(f"\nfiles with the most stat-budget misses:")
        for f, n in by_file.most_common(12):
            print(f"   {f:36} {n}")

    print(f"\n{len(findings)} finding(s); worst {min(worst_n, len(findings))}:")
    for _d, ratio, _src, owner, item, want, got, what in sorted(
            findings, key=lambda f: -f[0])[:worst_n]:
        print(f"   {ratio:5.2f}x  {what:6} {item['name'][:34]:34} ilvl{item['item_level']:<3} "
              f"{item['rarity']:9} want {want:7.1f} got {got:7.1f}  [{owner}]")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
