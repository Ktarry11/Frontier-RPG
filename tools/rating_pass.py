#!/usr/bin/env python3
"""Ratings on hand-authored loot: sized by item level, fitting the item, and arriving from the early levels.

    PYTHONPATH=. python3 tools/rating_pass.py                 # summary + examples, changes nothing
    PYTHONPATH=. python3 tools/rating_pass.py --apply

Kyle, 15 Nov 2026: "adjust some of the drip stats, fix up boss loot and quest loot to slap in some ratings for
easier transition from 1 to max level so not every rating is just dropped post 50. They need to be spread out and
logically done. None of this weird stuff we saw with crafting." and "We will remove and fix up a lot of drip stats
by changing stats from % to rating where 10 rating is 1%. Obviously some weigh more. Like crit rating is cheaper
than parry rating."

WHAT WAS THERE. The ratings switch (15 Nov) turned every authored percent into ten rating points, so the boss and
quest tables carry the same "+10 Crit Rating (1%)" on a level-14 ring and a level-60 chest - too much for the ring's
budget, nothing at 60 - and 6% of the items at 10-19 carry any rating against 50% at 50-59. Some ratings do not fit
the item they are on (dodge on a caster's robe, spell crit on an axe): the drip.

WHAT THIS DOES, per authored drop or quest reward (gear sets, crafting and recipes are not touched):
1. ROLE from its stats: tank (defense/dodge/parry/block, or a shield), healer (healing/mp5), caster (intellect,
   spell power, spirit), agility, strength.
2. DRIP OUT: a rating its role does not use is replaced by one it does (same slot in the list, so the item keeps
   its character).
3. SPREAD: an uncommon-or-better item from ilvl 8 with no rating gets one, chosen deterministically by name, until
   its level band carries roughly PRESENCE of them.
4. SIZE: an item's ratings take SHARE(ilvl) of its stat budget (the generator's own formula,
   tools/audit_item_budgets.budget_for) - 20% at ilvl 10 rising to 35% at 60; never under MIN_RATING (5, 0.5% - the crafting floor), and one rating where the budget cannot make two of that size - split 60/40 between two, priced by
   data/items/gear_suffixes.json stat_budget_costs. The primary stats are scaled to pay for it, so the item's total
   spend is what it was: on its curve before, on its curve after.
5. PRICES (stat_budget_costs): parry 1.25 and dodge 1.1 a point against crit's 1.0 (Kyle: "crit rating is cheaper
   than parry rating").
"""
import argparse
import collections
import glob
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
_spec = importlib.util.spec_from_file_location("_aib", ROOT / "tools/audit_item_budgets.py")
AIB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AIB)

RATINGS = {"crit_chance_physical", "crit_chance_spell", "hit_rating", "spell_hit_rating", "haste", "dodge_rating",
           "parry_rating", "block_rating", "defense_rating", "armor_penetration_pct", "spell_penetration"}
ALLOWED = {
    "tank": ["defense_rating", "dodge_rating", "parry_rating", "hit_rating"],
    "shield": ["block_rating", "defense_rating", "dodge_rating"],
    "healer": ["crit_chance_spell", "haste"],
    "caster": ["crit_chance_spell", "spell_hit_rating", "haste", "spell_penetration"],
    "agility": ["crit_chance_physical", "hit_rating", "haste", "armor_penetration_pct"],
    "strength": ["crit_chance_physical", "hit_rating", "haste", "armor_penetration_pct"],
}
#: how often each band should carry a rating (uncommon and better)
PRESENCE = [(8, 0.15), (10, 0.25), (20, 0.35), (30, 0.40), (40, 0.45), (50, 0.50)]
NEW_COSTS = {"parry_rating": 1.25, "dodge_rating": 1.1}
SOURCES = sorted(glob.glob("data/loot/*.json") + glob.glob("data/quests/*.json") + ["data/items/secret_uniques.json"])
PRIMARY = ("strength", "agility", "intellect", "stamina", "spirit")


MIN_RATING = 5          # 0.5%: Kyle's crafting floor (14 Nov: "No rating under 5 points") - one rule for crafted and dropped gear


def share(ilvl):
    return 0.20 + 0.15 * max(0.0, min(1.0, (ilvl - 10) / 50.0))


def presence(ilvl):
    p = 0.0
    for lv, v in PRESENCE:
        if ilvl >= lv:
            p = v
    return p


def role(it):
    s = {**(it.get("primary_stats") or {}), **(it.get("secondary_stats") or {})}
    if it.get("weapon_type") == "shield":
        return "shield"
    if any(k in s for k in ("defense_rating", "dodge_rating", "parry_rating", "block_rating", "block_value")):
        return "tank"
    if s.get("healing_power") or (s.get("mp5") and not s.get("spell_power")):
        return "healer"
    cast = sum(s.get(k, 0) for k in ("intellect", "spell_power", "spirit")) + sum(
        v for k, v in s.items() if k.endswith("_spell_power"))
    agi = s.get("agility", 0) + s.get("ranged_attack_power", 0) * 0.5
    stren = s.get("strength", 0) + s.get("attack_power", 0) * 0.5
    best = max((cast, "caster"), (agi, "agility"), (stren, "strength"))
    return best[1] if best[0] > 0 else None


def pick(name, options, k=0):
    h = int(hashlib.md5(f"{name}#{k}".encode()).hexdigest(), 16)
    return options[h % len(options)]


def chance(name):
    return (int(hashlib.md5(f"{name}#spread".encode()).hexdigest(), 16) % 1000) / 1000.0


def items_in(node, out):
    if isinstance(node, dict):
        if "secondary_stats" in node and node.get("item_level") and node.get("rarity") in ("uncommon", "rare", "epic"):
            out.append(node)
        for v in node.values():
            items_in(v, out)
    elif isinstance(node, list):
        for v in node:
            items_in(v, out)


OLD_COSTS = None


def old_spend(it):
    total = 0.0
    for block in ("primary_stats", "secondary_stats"):
        for stat, value in (it.get(block) or {}).items():
            if isinstance(value, (int, float)):
                total += float(value) * OLD_COSTS.get(stat, 1.0)
    return total


def rework(it, costs, stats):
    """Change one item in place. Returns a short description, or None if untouched."""
    r = role(it)
    if r is None:
        return None
    sec = it.setdefault("secondary_stats", {})
    prim = it.setdefault("primary_stats", {})
    allowed = ALLOWED[r]
    have = [k for k in list(sec) if k in RATINGS]
    budget, _a, _d = AIB.budget_for(it)
    if not budget:
        return None
    # the item's place on its curve is kept: its spend as a share of budget under the OLD prices, re-spent at the
    # new ones (a repriced parry or dodge must not push the other stats up or down)
    before_spend = old_spend(it) / budget * budget
    # 2. drip out: an off-role rating becomes an on-role one
    swapped = []
    for i, k in enumerate(have):
        if k not in allowed:
            new = next((a for a in [pick(it["name"], allowed, i)] + allowed if a not in sec or a == k), allowed[0])
            sec[new] = sec.pop(k)
            swapped.append(f"{k}->{new}")
            stats["drip swapped"] += 1
    have = [k for k in sec if k in RATINGS]
    # 3. spread: a rating where the band wants more
    added = None
    # avoidance IS a tank's stat: tank gear spends 1.4x the share on its ratings
    pool = share(it["item_level"]) * budget * (1.4 if r in ("tank", "shield") else 1.0)
    if not have and pool >= 2.0 and chance(it["name"]) < presence(it["item_level"]) - stats[
            "_present_share"].get((it["item_level"] // 10) * 10, 0.0):
        added = pick(it["name"], allowed)
        sec[added] = 1
        have = [added]
        stats["added"] += 1
    if not have:
        return None
    # an item whose stats are ALL ratings (tank weapons and bracers) spends everything on them
    other_now = [k for g in ("primary_stats", "secondary_stats") for k in it[g]
                 if k not in RATINGS and isinstance(it[g][k], (int, float)) and it[g][k] > 0]
    if not other_now:
        pool = before_spend
    # 4. size: SHARE of the budget, split 60/40, priced per stat - one rating when the budget cannot make two of
    # at least MIN_RATING
    two = len(have) > 1 and pool * 0.4 / max(costs.get(have[1], 1.0), 1e-9) >= MIN_RATING
    parts = [1.0] + [0.0] * (len(have) - 1) if not two else [0.6, 0.4] + [0.0] * (len(have) - 2)
    old = {k: sec[k] for k in have}
    rating_spend = 0.0
    for k, part in zip(have, parts):
        if part <= 0:
            sec.pop(k)
            continue
        amt = max(MIN_RATING, int(round(pool * part / costs.get(k, 1.0))))
        sec[k] = amt
        rating_spend += amt * costs.get(k, 1.0)
    # 5. pay for it from the primaries (or the other secondaries if there are none), keeping total spend
    other = [(g, k) for g in ("primary_stats", "secondary_stats") for k in it[g]
             if k not in RATINGS and isinstance(it[g][k], (int, float)) and it[g][k] > 0]
    other_spend = sum(it[g][k] * costs.get(k, 1.0) for g, k in other)
    target_other = max(0.0, before_spend - rating_spend)
    if other_spend > 0:
        f = target_other / other_spend
        for g, k in other:
            it[g][k] = max(1, int(round(it[g][k] * f)))
    stats["resized"] += 1
    return (f"{it['name'][:34]:<34} ilvl {it['item_level']:>2} {it['rarity']:<8} {r:<8} "
            f"{old if not added else {added: 'new'}} -> {{{', '.join(f'{k}: {sec[k]}' for k in have if k in sec)}}}"
            + (f"  swapped {swapped}" if swapped else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--examples", type=int, default=24)
    args = ap.parse_args()
    suffix_path = ROOT / "data/items/gear_suffixes.json"
    suffixes = json.loads(suffix_path.read_text(encoding="utf-8"))
    global OLD_COSTS
    OLD_COSTS = dict(suffixes["stat_budget_costs"])
    costs = dict(suffixes["stat_budget_costs"])
    costs.update(NEW_COSTS)
    AIB._COSTS.update(NEW_COSTS)
    # the share of each band that already carries a rating
    all_items = []
    docs = {}
    for f in SOURCES:
        docs[f] = json.loads(Path(f).read_text(encoding="utf-8"))
        items_in(docs[f], all_items)
    band = collections.defaultdict(lambda: [0, 0])
    for it in all_items:
        b = (it["item_level"] // 10) * 10
        band[b][0] += 1
        band[b][1] += any(k in RATINGS for k in (it.get("secondary_stats") or {}))
    stats = collections.Counter()
    stats["_present_share"] = {b: v[1] / v[0] for b, v in band.items()}
    lines = []
    for f in SOURCES:
        its = []
        items_in(docs[f], its)
        for it in its:
            d = rework(it, costs, stats)
            if d:
                lines.append((it["item_level"], d))
    after = collections.defaultdict(lambda: [0, 0, []])
    for it in all_items:
        b = (it["item_level"] // 10) * 10
        r = [v for k, v in (it.get("secondary_stats") or {}).items() if k in RATINGS]
        after[b][0] += 1
        after[b][1] += bool(r)
        after[b][2] += r
    print(f"{len(all_items)} authored uncommon+ items; resized {stats['resized']}, added {stats['added']}, "
          f"drip swapped {stats['drip swapped']}")
    print("band      with a rating (before -> after)   rating points: median, max")
    for b in sorted(after):
        pts = sorted(after[b][2])
        med = pts[len(pts) // 2] if pts else 0
        print(f"  {b:>2}-{b + 9:<3}  {band[b][1] / band[b][0]:5.0%} -> {after[b][1] / after[b][0]:5.0%}"
              f"                    {med:>4}  {pts[-1] if pts else 0:>4}")
    lines.sort()
    step = max(1, len(lines) // args.examples)
    print("\nexamples:")
    for _lv, d in lines[::step][:args.examples]:
        print("  " + d)
    if args.apply:
        for f, d in docs.items():
            Path(f).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        suffixes["stat_budget_costs"].update(NEW_COSTS)
        suffix_path.write_text(json.dumps(suffixes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("\nwritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
