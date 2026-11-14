#!/usr/bin/env python3
"""Re-tier every authored quest reward: WoW-style rarity policy + stats from the real loot budget.  Idempotent.

    python3 tools/retier_quest_rewards.py            # rewrite data/quests/*.json
    python3 tools/retier_quest_rewards.py --report   # just print the before/after summary

WHY (Kyle, 2026-10-22): nearly every Durotar quest paid blues, a lvl-6 staff was +13 Sta / +13 Spi, and a lvl-1 quest paid the
same green stats as a lvl-12 quest (authored stats were flat across levels, and a runtime "quest bonus" then lifted greens to
blues).  Quest gear now sits IN LINE with drops of the same item level:

RARITY  levels 1-5: white (green only for a chain's last quest or a boss kill)
        levels 6-10: ~55% white / 45% green  (chain end or boss kill: green, or blue if the item is ilvl >= 10 and the quest is lvl 8+)
        levels 11+ : green; blue only for a chain's last quest or a boss/elite kill
STATS   primary total = the loot budget formula for the item's level, rarity and slot (ilvl * 0.36 * rarity mult * slot weight),
        capped by the Gear.docx allowance band for that rarity; the authored stat mix is kept, secondary stats scale with it.
        Armor value and weapon damage use the same formulas as boss loot.  Blues are therefore strictly better than greens.
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from entities.loot_generator import LootGenerator  # noqa: E402

LG = LootGenerator()
W = LG.slots["weight_tiers"]
SLOTS = LG.slots["slots"]
R = {k: v["stat_budget_multiplier"] for k, v in LG.rarity_tiers.items()}

# Gear.docx "total stats" allowance (max of the band) per rarity; interpolated inside a band by item level.
BANDS = [(1, 10), (11, 20), (21, 35), (36, 50), (51, 60)]
GREEN = [(2, 4), (4, 8), (8, 15), (15, 25), (25, 35)]
BLUE = [(2, 4), (7, 10), (13, 20), (23, 33), (35, 48)]


def allowance(rarity, ilvl):
    table = BLUE if rarity == "rare" else GREEN
    for (lo_l, hi_l), (lo_a, hi_a) in zip(BANDS, table):
        if ilvl <= hi_l:
            t = max(0.0, min(1.0, (ilvl - lo_l) / max(1, hi_l - lo_l)))
            top = lo_a + (hi_a - lo_a) * t
            return top * (0.7 if rarity == "common" else 1.0)
    return table[-1][1]


def slot_weight(it):
    wt = it.get("weapon_type")
    if wt:
        info = LG.weapon_types["weapon_types"][wt]
        tier = "weapon_two_hand" if info.get("hand") == "two_hand" else "weapon_medium"
        return W[tier] * info.get("budget_multiplier", 1.0)
    return W[SLOTS.get(it["slot"], {}).get("weight_tier", "minor")]


def chain_len(qid):
    n = 1
    while qid in PREV:
        qid = PREV[qid]
        n += 1
        if n > 20:
            break
    return n


def pick_rarity(q, chain_end, boss, it):
    lv = q.get("level_min") or max(1, it.get("item_level", 1) - 2)
    h = int(hashlib.md5(q["quest_id"].encode()).hexdigest(), 16) % 100
    # blues are earned: the last quest of a real chain (3+ steps), or about half of the boss/elite kills
    special = (chain_end and chain_len(q["quest_id"]) >= 3) or (boss and h >= 50)
    minor_special = chain_end or boss          # a short chain end / the other boss kills still pay a green (not white)
    if lv <= 5:
        r = "uncommon" if minor_special else "common"
    elif lv <= 10:
        if special:
            r = "rare" if (lv >= 8 and it.get("item_level", 1) >= 10) else "uncommon"
        elif minor_special:
            r = "uncommon"
        else:
            r = "common" if h < 55 else "uncommon"
    else:
        r = "rare" if special else "uncommon"
    if r == "rare" and it.get("item_level", 1) < 10:
        r = "uncommon"
    return r


def spread(prim, target):
    """Rescale a {stat: n} dict to sum to `target` (largest remainder, min 1 each while target allows)."""
    old = sum(prim.values())
    if not prim or old <= 0:
        return prim
    target = max(1, int(round(target)))
    raw = {k: v * target / old for k, v in prim.items()}
    out = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - out[k], reverse=True):
        if sum(out.values()) >= target:
            break
        out[k] += 1
    out = {k: v for k, v in out.items() if v > 0}
    if not out:                                   # keep the dominant stat at least
        out = {max(prim, key=prim.get): 1}
    return out


def retier_item(it, rarity):
    """Rewrite one authored item def for `rarity` (returns (old_total, new_total))."""
    ilvl = it.get("item_level", 1)
    r = R[rarity]
    w = slot_weight(it)
    old_total = sum((it.get("primary_stats") or {}).values())
    if it.get("weapon_type") == "shield":
        budget = ilvl * LG.STAT_BUDGET_BASE_MULT * r * 0.75
        it["primary_stats"] = {"stamina": max(1, int(budget * 0.6))}
        it["armor_value"] = int(ilvl * 1.2 * r)
        it["block_value"] = int(ilvl * 1.5 * r)
    else:
        budget = min(ilvl * LG.STAT_BUDGET_BASE_MULT * r * w, allowance(rarity, ilvl) * min(1.5, max(0.5, w)))
        prim = it.get("primary_stats") or {}
        if prim:
            new_total = max(1, round(budget))
            it["primary_stats"] = spread(prim, new_total)
            f = sum(it["primary_stats"].values()) / old_total if old_total else 1.0
        else:
            f = budget / max(old_total, 1)
        if it.get("secondary_stats"):
            it["secondary_stats"] = {k: round(v * f, 1) for k, v in it["secondary_stats"].items()}
        if it.get("armor_type") and it.get("armor_type") in LG.armor_types["armor_types"]:
            mult = LG.armor_types["armor_types"][it["armor_type"]]["armor_multiplier"]
            it["armor_value"] = int(ilvl * 1.5 * mult * w * r)
        if it.get("weapon_type") and it.get("weapon_damage_max"):
            info = LG.weapon_types["weapon_types"][it["weapon_type"]]
            tier = info.get("damage_tier", "one_hand")
            mult = LG.weapon_types["damage_tiers"][tier]["dps_multiplier"]
            avg = (ilvl * 1.1 + 6.4) * r * mult
            it["weapon_damage_min"] = max(1, int(avg * 0.85))
            it["weapon_damage_max"] = max(it["weapon_damage_min"] + 1, int(avg * 1.15))
    it["rarity"] = rarity
    it.pop("quest_bonus_applied", None)
    return old_total, sum((it.get("primary_stats") or {}).values())


def main():
    boss_names = {n for n, c in json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"].items()
                  if c.get("is_boss")}
    report = "--report" in sys.argv
    before, after = {}, {}
    tot_old = tot_new = n_items = 0
    for f in sorted(glob.glob(str(ROOT / "data/quests/*.json"))):
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        qs = data["quests"] if isinstance(data, dict) else data
        nxt = {q.get("next_quest_id") for q in qs if q.get("next_quest_id")}
        # cross-file chains: also count predecessors from other files
        changed = False
        for q in qs:
            has_pred = q["quest_id"] in ALL_NEXT
            chain_end = has_pred and not q.get("next_quest_id")
            boss = any(o["type"] == "kill_boss" or (o["type"] == "kill" and o.get("target") in boss_names)
                       for o in q.get("objectives", []))
            items = q.get("unique_item_defs") or []
            for it in items:
                before[it["rarity"]] = before.get(it["rarity"], 0) + 1
            if items:
                rarity = pick_rarity(q, chain_end, boss, items[0])
                for it in items:
                    rr = rarity if not (rarity == "rare" and it.get("item_level", 1) < 10) else "uncommon"
                    o, n = retier_item(it, rr)
                    tot_old += o
                    tot_new += n
                    n_items += 1
                    after[rr] = after.get(rr, 0) + 1
                changed = True
            elif q.get("gear_reward_gear_level"):
                it = {"item_level": q["gear_reward_gear_level"], "slot": "chest"}
                q["gear_reward_rarity"] = pick_rarity(q, chain_end, boss, it)
                after[q["gear_reward_rarity"]] = after.get(q["gear_reward_rarity"], 0) + 1
                changed = True
        if changed and not report:
            Path(f).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("authored items by rarity before:", before)
    print("by rarity after (+procedural sets):", after)
    print(f"{n_items} authored items; mean primary-stat total {tot_old / max(n_items, 1):.1f} -> {tot_new / max(n_items, 1):.1f}")


def _all_next():
    s, prev = set(), {}
    for f in glob.glob(str(ROOT / "data/quests/*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for q in (d["quests"] if isinstance(d, dict) else d):
            if q.get("next_quest_id"):
                s.add(q["next_quest_id"])
                prev[q["next_quest_id"]] = q["quest_id"]
    return s, prev


ALL_NEXT, PREV = _all_next()

if __name__ == "__main__":
    main()
