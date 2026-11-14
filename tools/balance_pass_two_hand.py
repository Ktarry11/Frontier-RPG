"""Cap two-handed weapon damage at 1.35x a one-hand weapon (was 1.8x).

Combat is turn-based and attack_speed never gates anything, so a 2H weapon swings once per turn like a 1H - a 1.8x
damage tier made every 2H strictly better (Husk-Cracker Maul).  1.35x keeps 2H ahead of a lone 1H without making
the off-hand / dual-wield / shield choice pointless.  Staves (own 0.55 tier) are untouched.

  * data/items/weapon_types.json  damage_tiers.two_hand.dps_multiplier 1.8 -> 1.35   (procedural drops + future builders)
  * data/loot/*_boss_loot.json and data/quests/*.json: existing two_hand-tier weapons whose avg damage is more than
    1.40x the 1H formula baseline are scaled down to 1.35x (min/max spread preserved).  Idempotent.
"""
import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = 1.35
rar = json.load(open(f"{ROOT}/data/items/rarity.json", encoding="utf-8"))["rarity_tiers"]
wp_path = f"{ROOT}/data/items/weapon_types.json"
wp = json.load(open(wp_path, encoding="utf-8"))
wp["damage_tiers"]["two_hand"]["dps_multiplier"] = TARGET
json.dump(wp, open(wp_path, "w", encoding="utf-8"), indent=2); open(wp_path, "a", encoding="utf-8").write("\n")
W = wp["weapon_types"]


def fix(it):
    wt = it.get("weapon_type")
    if not wt or wt not in W or W[wt].get("damage_tier") != "two_hand": return False
    r = rar[it["rarity"]]["stat_budget_multiplier"]
    base = (it["item_level"] * 1.1 + 6.4) * r
    avg = (it["weapon_damage_min"] + it["weapon_damage_max"]) / 2
    if avg / base <= TARGET + 0.05: return False
    new_avg = base * TARGET
    it["weapon_damage_min"] = max(1, int(new_avg * 0.85))
    it["weapon_damage_max"] = max(it["weapon_damage_min"] + 1, int(new_avg * 1.15))
    return True


changed = 0
for p in glob.glob(f"{ROOT}/data/loot/*_boss_loot.json") + glob.glob(f"{ROOT}/data/quests/*.json"):
    raw = open(p, encoding="utf-8").read(); d = json.loads(raw); n = 0
    def walk(o):
        global n
        if isinstance(o, dict):
            if "weapon_damage_min" in o and "item_level" in o and fix(o): n += 1
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d)
    if n:
        indent = 2
        open(p, "w", encoding="utf-8").write(json.dumps(d, indent=indent, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))
        print(f"{os.path.basename(p)}: {n} two-handers rescaled"); changed += n
print("total", changed)
