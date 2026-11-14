"""
One-time balance-pass script (Kyle's direction, 2026-09-05): rewrites
rank-1 effect_value for every OG9 damage/spell_damage ability (excluding
basic Attack, handled separately - see attack effect_value=0 change).

Target bands (rank-1 damage output, which at Level 1 with minimal AP/
spell_power IS approximately the real hit since effect_value dominates
the formula):
  cd=0 (spammable, no cooldown): ~40-50
  cd=1:                          ~46-50
  cd=2:                          ~50-56
  cd=3:                          ~56-64
  cd=4-5:                        ~64-75
  cd=6+:                         ~78-85 (big cooldown payoff)

Values are hand-picked per ability (not a blind formula) to preserve each
kit's internal power ordering - e.g. Mortal Strike should still hit
harder than Heroic Strike at the same cooldown tier, Execute is still a
finisher-style spike. Only rank 1 is touched here; higher ranks keep
their EXISTING relative growth curve from rank 1 (i.e. this script also
rescales ranks 2+ proportionally to the old rank-1 -> new rank-1 ratio,
so a 5-rank spell's shape is preserved, not flattened).

Run once, not idempotent-safe to run twice.
"""
import json

OG9 = ["warrior", "rogue", "hunter", "mage", "warlock", "priest", "shaman", "druid", "paladin"]

# ability_id -> new rank-1 effect_value
TARGETS = {
    # --- Warrior ---
    "warrior_heroic_strike": 44,     # cd0
    "warrior_thunder_clap": 48,      # cd1, aoe
    "warrior_overpower": 56,         # cd3
    "warrior_mortal_strike": 60,     # cd2, signature finisher-ish
    "warrior_execute": 68,           # cd3, execute spike
    "warrior_bladestorm": 82,        # cd6, big cooldown
    "warrior_devastate": 42,         # cd0
    "warrior_concussion_blow": 70,   # cd5
    "warrior_shockwave": 72,         # cd5, aoe
    "warrior_bloodthirst": 58,       # cd2
    "warrior_cleave": 48,            # cd1, aoe
    "warrior_charge": 42,            # cd4 but small opener, keep low-ish
    "warrior_intercept": 66,         # cd5
    "warrior_whirlwind": 58,         # cd3, aoe

    # --- Rogue ---
    "rogue_sinister_strike": 42,     # cd0
    "rogue_backstab": 52,            # cd2
    "rogue_eviscerate": 54,          # cd2, finisher
    "rogue_mutilate": 44,            # cd0

    # --- Hunter ---
    "hunter_steady_shot": 42,        # cd0
    "hunter_multi_shot": 52,         # cd2, aoe
    "hunter_aimed_shot": 58,         # cd3
    "hunter_chimera_shot": 78,       # cd3, signature big hit

    # --- Mage ---
    "mage_fireball": 44,             # cd0
    "mage_frostbolt": 42,            # cd0
    "mage_arcane_explosion": 52,     # cd2, aoe
    "mage_pyroblast": 62,            # cd3, signature big hit
    "mage_cone_of_cold": 58,         # cd3, aoe
    "mage_fire_blast": 58,           # cd3
    "mage_ice_lance": 40,            # cd0

    # --- Warlock ---
    "warlock_shadow_bolt": 44,       # cd0
    "warlock_drain_life": 46,        # cd2, also heals caster - keep modest
    "warlock_shadowburn": 62,        # cd3, execute-style
    "warlock_conflagrate": 56,       # cd2
    "warlock_chaos_bolt": 80,        # cd3, signature nuke
    "warlock_searing_pain": 42,      # cd0

    # --- Priest ---
    "priest_smite": 42,              # cd0
    "priest_mind_blast": 54,         # cd2
    "priest_holy_fire": 56,          # cd2

    # --- Shaman ---
    "shaman_lightning_bolt": 44,     # cd0
    "shaman_earth_shock": 52,        # cd2
    "shaman_lava_burst": 60,         # cd3
    "shaman_chain_lightning": 58,    # cd3, aoe
    "shaman_thunderstorm": 74,       # cd5, aoe, free (0 cost)

    # --- Druid ---
    "druid_wrath": 44,               # cd0
    "druid_mangle": 48,              # cd1
    "druid_starfire": 54,            # cd2
    "druid_typhoon": 70,             # cd4, aoe knockback
    "druid_claw": 40,                # cd0, cat builder
    "druid_shred": 44,               # cd0, cat builder (positional)
    "druid_ferocious_bite": 48,      # cd1, cat finisher
    "druid_ravage": 54,              # cd2, cat opener
    "druid_swipe_cat": 46,           # cd1, aoe
    "druid_maul": 42,                # cd0, bear

    # --- Paladin ---
    "paladin_crusader_strike": 42,   # cd0
    "paladin_judgement": 48,         # cd1
    "paladin_hammer_of_wrath": 58,   # cd3, execute-style
    "paladin_avengers_shield": 56,   # cd3, aoe-ish
    "paladin_divine_storm": 72,      # cd5, aoe
    "paladin_exorcism": 50,          # cd1
}


def main():
    changed = []
    for cls in OG9:
        path = f"data/abilities/{cls}.json"
        d = json.load(open(path, encoding="utf-8"))
        touched = False
        for a in d["abilities"]:
            if a["ability_id"] not in TARGETS:
                continue
            new_r1 = TARGETS[a["ability_id"]]
            old_r1 = a["ranks"][0]["effect_value"]
            if old_r1 == 0:
                continue  # shouldn't happen, but avoid divide-by-zero
            ratio = new_r1 / old_r1
            old_vals = [r["effect_value"] for r in a["ranks"]]
            for r in a["ranks"]:
                r["effect_value"] = max(1, int(round(r["effect_value"] * ratio)))
            # Force rank 1 to the exact target (rounding above should
            # already land here since ratio = new/old, but be explicit).
            a["ranks"][0]["effect_value"] = new_r1
            new_vals = [r["effect_value"] for r in a["ranks"]]
            changed.append((a["ability_id"], a["cooldown"], old_vals, new_vals))
            touched = True
        if touched:
            json.dump(d, open(path, "w", encoding="utf-8"), indent=2)

    print(f"Rebalanced {len(changed)} damage abilities:\n")
    for ability_id, cd, old, new in changed:
        print(f"  {ability_id:32s} cd={cd}  {old} -> {new}")


if __name__ == "__main__":
    main()
