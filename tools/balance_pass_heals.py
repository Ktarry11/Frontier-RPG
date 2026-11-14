"""
One-time balance-pass script (Kyle's direction, 2026-09-05): rewrites
rank-1 effect_value for every OG9 heal/hot ability to Kyle's stated
"heals should go off for about 50-75 at the start" target.

Target bands (rank-1 heal output; heal formula is effect_value +
healing_power*1.2, and healing_power is small at Level 1, so
effect_value dominates just like the damage-ability pass):
  cd=0-1 (main-line spam heal):      50-60
  cd=2-3 (bigger/slower heal):       65-80
  cd=4+ (big AoE heal):              75-90
  HoTs (total across duration):      45-65 for basic ones, higher for
                                      premium/expensive ones (Wild
                                      Growth, Riptide)
  Long-CD "emergency" finishers (Lay on Hands, Redemption, Reincarnation,
  hunter_revive_pet): LEFT ALONE - these are rare-use safety nets with
  intentionally huge numbers (near-full-heal or full-revive), not part
  of the normal healing rotation Kyle's 50-75 target describes.

Same proportional-rank-rescaling approach as balance_pass_damage.py:
only rank 1 is directly targeted, ranks 2+ keep the OLD table's growth
ratio from rank 1, just applied to the new rank-1 base.

Run once, not idempotent-safe to run twice.
"""
import json

OG9 = ["warrior", "rogue", "hunter", "mage", "warlock", "priest", "shaman", "druid", "paladin"]

# Left alone - emergency/finisher heals or revive abilities, not part of
# Kyle's "start of the game" spam-heal target.
SKIP = {
    "hunter_revive_pet", "shaman_reincarnation",
    "paladin_redemption", "paladin_lay_on_hands",
}

# ability_id -> new rank-1 effect_value
TARGETS = {
    # --- Hunter ---
    "hunter_mend_pet": 40,             # cd3 hot, pet-only utility, kept modest

    # --- Warlock ---
    "warlock_health_funnel": 55,       # cd2, also costs caster HP - keep at low end of that tier

    # --- Priest ---
    "priest_heal": 54,                 # cd1, main-line spam heal
    "priest_renew": 48,                # cd2 hot, total-over-duration
    "priest_penance": 72,              # cd2, premium heal
    "priest_circle_of_healing": 82,    # cd3, aoe
    "priest_prayer_of_healing": 86,    # cd4, aoe

    # --- Shaman ---
    "shaman_healing_wave": 56,         # cd1, main-line spam heal

    # --- Druid ---
    "druid_rejuvenation": 46,          # cd1 hot, total-over-duration
    "druid_healing_touch": 68,         # cd2
    "druid_regrowth": 52,              # cd1 hot (has an instant component in real WoW; keep modest as a hot-total)

    # --- Paladin ---
    "paladin_holy_light": 52,          # cd1, main-line spam heal
    "paladin_holy_shock": 60,          # cd1, premium instant
    "paladin_flash_of_light": 50,      # cd0, fast/cheap heal
}


def main():
    changed = []
    for cls in OG9:
        path = f"data/abilities/{cls}.json"
        d = json.load(open(path, encoding="utf-8"))
        touched = False
        for a in d["abilities"]:
            if a["ability_id"] in SKIP:
                continue
            if a["ability_id"] not in TARGETS:
                continue
            new_r1 = TARGETS[a["ability_id"]]
            old_r1 = a["ranks"][0]["effect_value"]
            if old_r1 == 0:
                continue
            ratio = new_r1 / old_r1
            old_vals = [r["effect_value"] for r in a["ranks"]]
            for r in a["ranks"]:
                r["effect_value"] = max(1, int(round(r["effect_value"] * ratio)))
            a["ranks"][0]["effect_value"] = new_r1
            new_vals = [r["effect_value"] for r in a["ranks"]]
            changed.append((a["ability_id"], a["cooldown"], old_vals, new_vals))
            touched = True
        if touched:
            json.dump(d, open(path, "w", encoding="utf-8"), indent=2)

    print(f"Rebalanced {len(changed)} heal/hot abilities:\n")
    for ability_id, cd, old, new in changed:
        print(f"  {ability_id:32s} cd={cd}  {old} -> {new}")


if __name__ == "__main__":
    main()
