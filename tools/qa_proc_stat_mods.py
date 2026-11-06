#!/usr/bin/env python3
"""A proc's stat_mods may only carry keys a STATUS EFFECT can be read for.

    PYTHONPATH=. python3 tools/qa_proc_stat_mods.py [--report]

THE BLIND SPOT THIS CLOSES, and it is a subtle one.

A talent's `effects` and a proc's `apply_effect.stat_mods` look
interchangeable and are read through COMPLETELY DIFFERENT CHANNELS:

    talent effects   -> Character.get_talent_effects()
                        summed from spent talents AND the current stance
                        (character.py:628), read by Ability._talent()
    status stat_mods -> Character.get_status_stat_mod(key)
                        summed from active StatusEffects only

So a key is "live" only with respect to ONE of those channels, and most of
the damage and healing vocabulary is live in the TALENT channel only:

    all_damage, physical_damage, spell_damage      abilities.py:1606-1610
    <school>_spell_damage                          abilities.py:1371
    healing_done                                   abilities.py:1566

Put any of those in a proc's stat_mods and NOTHING READS IT. The talent
loads, the tooltip reads correctly, audit_talents passes - because the key
genuinely does have read sites, just not from a status effect - and the
buff does nothing at all.

The damage path reads exactly ONE key from the status channel
(abilities.py:1680-1683):

    damage_dealt_pct      for everything that is not healing
    healing_done_pct      for healing

both in PERCENTAGE POINTS (the value is divided by 100), which is the
opposite convention to their talent-channel cousins' fractions.

STANCES LOOK LIKE A COUNTER-EXAMPLE AND ARE NOT. combat/stances.py and
combat/guardian_stance.py both put all_damage and physical_damage in a
"stat_mods" dict and both work - because a stance's mods are folded into
get_talent_effects (character.py:628), reaching the TALENT bus. A
proc-applied buff is not.

FOUND BY THE AUDIT HALF-WORKING. audit_talents flagged
shadow_spell_damage in a proc's stat_mods as a dead key, which prompted
checking its relatives - and all_damage, physical_damage and
healing_power_pct were sitting in nine more procs across six classes,
unflagged, because they have read sites elsewhere. Eight were authored
during the Classic rebuild on 5 Nov 2026 and the rest during the CoA pass.

WHAT IS CHECKED: every key in every proc apply_effect stat_mods, against
two lists - keys known to be read from the status channel, and keys known
to be TALENT-CHANNEL ONLY. A key on neither list is reported as unknown
rather than wrong, because this vocabulary is not closed and a false
accusation is worse than a gap.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: MEASURED, not reasoned about. Each key below was applied as a real
#: StatusEffect to a live level-60 character and the derived stats
#: compared before and after. That matters because the first draft of this
#: tool got it WRONG in both directions.
#:
#: WHY SO MANY STAT KEYS ARE SAFE: _recalculate_derived_stats folds active
#: status effects into the SAME `bonuses` pool as gear and talents
#: (character.py:1218), so anything the recalc reads from `bonuses` is live
#: from a status effect too. attack_power_pct, strength_pct,
#: healing_power_pct and block_value_pct were all accused by the first
#: draft and all move a real attribute.
STATUS_READABLE = {
    # the damage/healing pair the DAMAGE PATH reads from the status
    # channel, abilities.py:1680-1683, in PERCENTAGE POINTS
    "damage_dealt_pct", "healing_done_pct",
    # damage taken, character.py:2716/2755/2781/2923, plus the DYNAMIC
    # f"{damage_type}_damage_taken_pct" family (monster.py:743,
    # character.py:2781) which a literal grep cannot see
    "damage_taken_pct", "physical_damage_taken_pct",
    "magic_damage_taken_pct", "spell_damage_taken_pct", "healing_taken_pct",
    "fire_damage_taken_pct", "frost_damage_taken_pct",
    "shadow_damage_taken_pct", "nature_damage_taken_pct",
    "arcane_damage_taken_pct", "holy_damage_taken_pct",
    # cost, abilities.py:1243
    "all_ability_cost_pct",
    # MEASURED to move an attribute through the `bonuses` pool
    "attack_power_pct", "strength_pct", "stamina_pct", "intellect_pct",
    "spirit_pct", "max_health_pct", "max_mana_pct", "healing_power_pct",
    "block_value_pct", "all_stats_pct", "armor_pct",
    # flat stats, summed from active effects like any gear bonus
    "strength", "agility", "intellect", "spirit", "stamina",
    "attack_power", "ranged_ap", "spell_power", "healing_power", "armor",
    "magic_resistance", "armor_penetration", "armor_penetration_pct",
    "spell_penetration",
    "crit_chance_physical", "crit_chance_spell", "haste", "hit_rating",
    "expertise", "dodge", "parry", "block", "block_value",
    "mp5", "threat_generation_pct", "cc_immune",
    "fire_resistance", "frost_resistance", "nature_resistance",
    "shadow_resistance", "arcane_resistance", "holy_resistance",
    # per-school spell power, read by Character._per_school_spell_power
    "fire_spell_power", "frost_spell_power", "arcane_spell_power",
    "shadow_spell_power", "nature_spell_power", "holy_spell_power",
    # pet scaling, read by the pet from its owner's bonus pool
    "pet_damage", "pet_health", "pet_armor",
}

#: TALENT-CHANNEL ONLY, and this is the real finding. Every key here is a
#: DAMAGE or HEALING MULTIPLIER or a CONDITIONAL, read through
#: Ability._talent() / get_talent_effect(), which sums spent talents and
#: the current stance and NOTHING ELSE. In a proc's stat_mods each is
#: silent dead data. Confirmed by measurement: none moves any attribute.
TALENT_ONLY = {
    "all_damage": "damage_dealt_pct (POINTS)",
    "physical_damage": "damage_dealt_pct (POINTS)",
    "spell_damage": "damage_dealt_pct (POINTS)",
    "aoe_damage": "damage_dealt_pct (POINTS)",
    "dot_damage": "damage_dealt_pct (POINTS)",
    "healing_done": "healing_done_pct (POINTS)",
    "crit_damage_pct": "no status equivalent",
    "crit_damage_physical": "no status equivalent",
    "crit_damage_spell": "no status equivalent",
    "crit_taken_reduction": "no status equivalent",
    "stun_duration_reduction_pct": "no status equivalent",
    "low_health_damage_pct": "no status equivalent",
    "low_health_damage_reduction_pct": "no status equivalent",
    "low_health_healing_pct": "no status equivalent",
    "low_health_threshold_pct": "no status equivalent",
    "threat_multiplier": "threat_generation_pct",
}

#: The per-school DAMAGE family (not spell POWER, which is safe above).
#: Built with f-strings at abilities.py:1371 and read via _talent, so live
#: as a talent effect and dead in a status effect.
SCHOOLS = ("physical", "fire", "frost", "arcane", "nature", "shadow",
           "holy", "magic")
for _s in SCHOOLS:
    TALENT_ONLY[f"{_s}_spell_damage"] = "damage_dealt_pct (POINTS)"
    TALENT_ONLY[f"{_s}_damage_pct"] = "damage_dealt_pct (POINTS)"
    TALENT_ONLY[f"{_s}_crit_damage_pct"] = "no status equivalent"


def specs_of(node):
    spec = (node.get("proc") or {}).get("apply_effect")
    if not spec:
        return []
    return spec if isinstance(spec, list) else [spec]


def main():
    report = "--report" in sys.argv
    dead, unknown, rows = [], [], []
    checked = 0

    for path in sorted((ROOT / "data/talents").glob("*.json")):
        for node in json.loads(path.read_text())["nodes"]:
            for spec in specs_of(node):
                for key, val in (spec.get("stat_mods") or {}).items():
                    checked += 1
                    rows.append((path.name, node["talent_id"], key, val))
                    if key.startswith("ability_"):
                        dead.append((path.name, node["talent_id"], key, val,
                                     "ability-scoped keys are read via "
                                     "_talent only"))
                    elif key in TALENT_ONLY:
                        dead.append((path.name, node["talent_id"], key, val,
                                     TALENT_ONLY[key]))
                    elif key not in STATUS_READABLE:
                        unknown.append((path.name, node["talent_id"], key,
                                        val))

    print(f"  {checked} stat_mod keys across all proc apply_effect specs")
    print(f"  {len(STATUS_READABLE)} keys known status-readable, "
          f"{len(TALENT_ONLY)} known talent-only")

    if report:
        print("\n  talent                                        key")
        for _f, tid, key, val in rows:
            mark = ("DEAD" if key in TALENT_ONLY
                    else "ok  " if key in STATUS_READABLE else "????")
            print(f"  {mark} {tid:44s} {key}={val}")

    if not dead and not unknown:
        print("\n  0 PROC stat_mods CARRY A TALENT-ONLY KEY\n\nPASS")
        return 0

    if dead:
        print(f"\n  {len(dead)} PROC stat_mods CARRY A TALENT-ONLY KEY")
        print("  Each is SILENT DEAD DATA: the key has read sites, but not "
              "from a status\n  effect, so the buff does nothing and every "
              "other check passes.\n")
        for _f, tid, key, val, better in dead:
            print(f"    {tid:46s} {key}={val}")
            print(f"      {'':46s} -> use {better}")

    if unknown:
        print(f"\n  {len(unknown)} KEYS NOT ON EITHER LIST - verify before "
              f"trusting")
        print("  Not necessarily wrong; this vocabulary is not closed. "
              "Measure it.\n")
        for _f, tid, key, val in unknown:
            print(f"    {tid:46s} {key}={val}")

    print("\nFAIL" if dead else "\nPASS (with unverified keys)")
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
