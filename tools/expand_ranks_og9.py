"""
One-time balance-pass script (Kyle's direction, 2026-09-05): expands the
13 OG9 "spam skill" abilities (cd=0, the class-defining workhorse
damage/dot spells - Fireball, Lightning Bolt, Sinister Strike, Wrath,
Corruption, etc.) from their old flat 5-rank tables to 8-9 ranks, matching
the CoA classes' progression convention (see combat/rank_generator.py's
_GAP_SEQUENCES additions for 8/9-rank tables, added alongside this
script).

Rank-1 values are left EXACTLY as set by the previous balance_pass_damage.py
pass (this script reads them, doesn't re-target them). Damage/cost growth
per rank is a linear step chosen so the final rank lands at roughly the
same TOTAL growth multiple the old 5-rank table had (~2.6x rank1 for
damage abilities, ~2.9x for the higher-cost DoTs) - just spread across
more, smaller steps instead of 4 big jumps. This keeps a rank-9 Fireball
in the same power ballpark it would have been at old rank-5, rather than
inflating late-game ceilings as a side effect of adding more rungs.

level_learned=1 for every ability here (all 13 are starting-kit spells
known at character creation) - all get the 9-rank table.

Run once, not idempotent-safe to run twice (re-running would re-expand
the already-9-rank list using the wrong "old 5-rank final value" as its
growth anchor).
"""
import json
import sys
sys.path.insert(0, ".")
from combat.rank_generator import generate_ranks

OG9 = ["warrior", "rogue", "hunter", "mage", "warlock", "priest", "shaman", "druid", "paladin"]

# Abilities to expand. All are cd=0, level_learned=1, target 9 ranks.
TARGET_ABILITIES = {
    "warrior_heroic_strike", "rogue_sinister_strike", "hunter_steady_shot",
    "mage_fireball", "mage_frostbolt", "warlock_shadow_bolt",
    "warlock_corruption", "priest_smite", "priest_shadow_word_pain",
    "shaman_lightning_bolt", "druid_wrath", "druid_moonfire",
    "paladin_crusader_strike",
}

NUM_RANKS = 9


def expand_ability(a):
    old_ranks = a["ranks"]
    old_r1_val = old_ranks[0]["effect_value"]
    old_r1_cost = old_ranks[0]["cost"]
    old_final_val = old_ranks[-1]["effect_value"]
    old_final_cost = old_ranks[-1]["cost"]

    # Preserve the OLD table's total growth ratio (final/rank1), just
    # spread across NUM_RANKS steps instead of the old 5. A flat-cost
    # ability (warrior_heroic_strike: cost never changed across ranks)
    # keeps cost flat here too, rather than inventing cost growth that
    # wasn't there before.
    val_ratio = old_final_val / old_r1_val
    cost_ratio = old_final_cost / old_r1_cost if old_r1_cost > 0 else 1.0

    def rank_value_fn(i):
        # Linear interpolation from rank1 -> final across NUM_RANKS steps
        # (i is 0-based), applied as a multiple of the rank-1 value/cost
        # that's already been set by the damage-rebalance pass.
        t = i / (NUM_RANKS - 1)
        val = int(round(old_r1_val * (1 + (val_ratio - 1) * t)))
        cost = int(round(old_r1_cost * (1 + (cost_ratio - 1) * t)))
        return {"cost": cost, "effect_value": val}

    new_ranks = generate_ranks(level_learned=1, base_ranks_wanted=NUM_RANKS, rank_value_fn=rank_value_fn)
    a["ranks"] = new_ranks


def main():
    changed = []
    for cls in OG9:
        path = f"data/abilities/{cls}.json"
        d = json.load(open(path, encoding="utf-8"))
        touched = False
        for a in d["abilities"]:
            if a["ability_id"] not in TARGET_ABILITIES:
                continue
            old_summary = [(r["level_req"], r["effect_value"], r["cost"]) for r in a["ranks"]]
            expand_ability(a)
            new_summary = [(r["level_req"], r["effect_value"], r["cost"]) for r in a["ranks"]]
            changed.append((a["ability_id"], old_summary, new_summary))
            touched = True
        if touched:
            json.dump(d, open(path, "w", encoding="utf-8"), indent=2)

    print(f"Expanded {len(changed)} abilities to {NUM_RANKS} ranks:\n")
    for ability_id, old, new in changed:
        print(f"  {ability_id}")
        print(f"    old ({len(old)} ranks): {old}")
        print(f"    new ({len(new)} ranks): {new}")
        print()


if __name__ == "__main__":
    main()
