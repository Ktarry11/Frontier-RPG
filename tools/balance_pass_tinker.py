"""Tinker low-level kit rescale (Oct 2026).

Tinker's filler/utility abilities kept raw Ascension tooltip numbers (Scrap Shot 1 -> 3 damage, Max-rank cost 2 mana)
while the other 16 classes sit on the OG9 balance bands (rank-1 ~42-56 for cd0-cd2 hits, ~3x by max rank, mana cost
~0.55-0.75x the value).  Rewrites rank values/costs for the affected abilities; absolute values, so it is idempotent.
Run: python3 tools/balance_pass_tinker.py
"""
import json, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/abilities/tinker.json")
MAXMULT = {1: 1.0, 2: 1.6, 3: 1.9, 4: 2.3, 5: 2.6, 6: 2.8, 7: 2.9, 8: 3.0}
#            rank-1 value, cost as a fraction of value
TARGETS = {
    "tinker_scrap_shot":         (42, 0.55),
    "tinker_spanner_smash":      (50, 0.40),
    "tinker_repair_shot":        (52, 0.75),
    "tinker_sticky_bomb":        (54, 0.55),
    "tinker_bomb_toss":          (64, 0.70),
    "tinker_makeshift_dynamite": (80, 0.55),
    "tinker_mechsuit_laser_beam": (66, 0.55),
    "tinker_med_pack":           (70, 0.70),
    "tinker_nanobot_swarm":      (56, 0.60),
    "tinker_healing_radiator":   (60, 0.60),
}
d = json.load(open(P, encoding="utf-8"))
for a in d["abilities"]:
    if a["ability_id"] not in TARGETS: continue
    r1, cf = TARGETS[a["ability_id"]]
    n = len(a["ranks"]); mm = MAXMULT[min(n, 8)]
    for i, r in enumerate(a["ranks"]):
        v = round(r1 * (1 + (mm - 1) * (i / (n - 1) if n > 1 else 0)))
        r["effect_value"] = v; r["cost"] = max(1, round(v * cf))
    print(f'{a["ability_id"]:30} {[(r["effect_value"], r["cost"]) for r in a["ranks"]]}')
json.dump(d, open(P, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(P, "a", encoding="utf-8").write("\n")
