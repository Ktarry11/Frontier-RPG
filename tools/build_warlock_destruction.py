#!/usr/bin/env python3
"""Rebuild Warlock Destruction from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_warlock_destruction.py

SOURCE: data/reference/wotlk/warlock.json (from Spell.dbc) - the real 26
talents and 75 points, with every row read out of the reference and every
ambiguous talent's RANK TEXT read before authoring, not recalled. (The
first draft of the Demonology builder was written from memory, invented a
talent that does not exist in WotLK and missed two that do; that is why
every Warlock tree now reads the reference first.)

ROLE: direct damage. Shadow Bolt and Incinerate into Chaos Bolt, with
Conflagrate eating the Immolate.

DESTRUCTION IS THE BEST-SHAPED WARLOCK TREE FOR THIS ENGINE. Six of its
real talents are literally chance-based ('has a 30% chance', 'all
critical hits have a chance to'), so the proc count holds up instead of
collapsing the way Demonology's honestly did.

FOUR MANDATORY UNLOCKS, all at their real rows and all the ONLY source
for a requires_talent ability: Shadowburn (row 2), Conflagrate (row 6),
Shadowfury (row 8), Chaos Bolt (row 10, the capstone).

THE RECURRING BLOCKERS IN THIS TREE:
  - NO CAST TIMES, so Bane, Intensity and Backdraft all lose their real
    content. Each is retargeted rather than dropped, and each says how.
  - NOTHING READS A DEBUFF ON THE TARGET, which guts Fire and Brimstone.
  - PETS NEVER FIRE PROCS (no fire_proc_trigger in entities/pet.py), so
    Empowered Imp's crit-feedback half is unbuildable.
  - proc['school'] only TYPES a damage_flat payload - it is NOT a
    trigger-side filter - so Nether Protection cannot be school-specific.
  - A TALENT EFFECT CAN NEVER REACH AN ALLY (only a party-targeted
    ABILITY can, abilities.py:2064), so Improved Soul Leech loses its
    raid half.

UNIT CONVENTIONS USED HERE: crit_chance_spell and ability_<id>_crit are
PERCENTAGE POINTS; crit_damage_spell, fire_spell_damage,
physical_damage_taken_pct (as a TALENT effect), dot_damage and every
ability_<id>_damage are FRACTIONS; spell_damage_taken_pct INSIDE A STATUS
EFFECT is POINTS, which is the opposite of its talent-effect form;
damage_dealt_pct is the only damage key a status effect can carry and is
POINTS.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("warlock_destruction", "Warlock Destruction",
         "Shadow and fire, spent all at once - the fastest damage a "
         "warlock can throw.")

# ----------------------------------------------------- tier 0 (row 0)
T.node("improved_shadow_bolt", "Improved Shadow Bolt",
       "Your Shadow Bolt crits leave the target taking 4% more damage for 3 "
       "turns.",
       0, -2, 5,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "ability_filter": ["warlock_shadow_bolt"],
             "apply_effect": {"effect_id": "improved_shadow_bolt",
                              "name": "Shadow Vulnerability",
                              "effect_type": "debuff", "duration": 3,
                              "stat_mods": {"damage_taken_pct": 0.04}}},
       source="WotLK row 0, built close to verbatim: 'Your Shadow Bolt "
              "critical strikes increase Shadow damage dealt to the target "
              "by 4%-20%.' KEPT AS A PROC because the real text is "
              "trigger-shaped. The chance IS scaled by points by the engine "
              "(capped 100, only when max_points > 1) while the PAYLOAD IS "
              "NOT, which is this project's multi-rank proc idiom - so five "
              "ranks buy reliability rather than size. There is no "
              "shadow-specific damage-TAKEN key, so it is bare "
              "damage_taken_pct, which is read RAW ON BOTH SIDES (0.04 is "
              "4%) and is one of only eight stat_mods A MONSTER CAN READ.")

T.node("bane", "Bane",
       "Increases the damage of your Shadow Bolt, Immolate and Chaos Bolt "
       "by 2% per rank.",
       0, 0, 5,
       effects={"ability_warlock_shadow_bolt_damage": 0.02,
                "ability_warlock_immolate_damage": 0.02,
                "ability_warlock_chaos_bolt_damage": 0.02},
       source="WotLK row 0: 'Reduces the casting time of your Shadow Bolt, "
              "Chaos Bolt and Immolate spells by 0.5 sec and your Soul Fire "
              "spell by 2 sec.' DEPARTURE - THERE ARE NO CAST TIMES in this "
              "engine, so the talent has no content to port. Faster casting "
              "is more damage per fight, so it becomes damage on exactly "
              "the three spells the real talent names (Soul Fire does not "
              "exist). This is the first of three cast-time talents in this "
              "tree, and all three are retargeted rather than dropped.")

# ----------------------------------------------------- tier 1 (rows 1-2)
T.node("aftermath", "Aftermath",
       "Increases the periodic damage of your Immolate by 3% per rank.",
       1, -6, 2,
       effects={"ability_warlock_immolate_damage": 0.03},
       connected_to=["improved_shadow_bolt"],
       source="WotLK row 1: 'Increases the periodic damage done by your "
              "Immolate by 3%/6%, and your Conflagrate has a 100% chance to "
              "daze the target for 5 sec.' The Immolate half is VERBATIM. "
              "The daze is unbuildable - there is no movement speed, and no "
              "snare or root system of any kind - and a daze is not a stun, "
              "so is_stun would be the wrong substitute rather than a near "
              "one. Rank text read from the reference before authoring; the "
              "name alone would not have revealed either half.")

T.node("molten_skin", "Molten Skin",
       "Reduces physical damage taken by 2% per rank.",
       1, -4, 3,
       effects={"physical_damage_taken_pct": -0.02},
       connected_to=["improved_shadow_bolt"],
       source="WotLK row 1, built verbatim: 'Reduces all physical damage "
              "taken by 2%/4%/6%.' physical_damage_taken_pct is A FRACTION "
              "AS A TALENT EFFECT and POINTS inside a status effect - the "
              "same key, two conventions, and audit_talents is the only "
              "thing that catches the wrong one. It is read via the "
              "f-string f'{damage_type}_damage_taken_pct' at monster.py:743 "
              "and character.py:2781, so grep cannot see the read site and "
              "the key is nonetheless LIVE.")

T.node("cataclysm", "Cataclysm",
       "Reduces the cost of your direct damage spells by 4% per rank.",
       1, -2, 3,
       effects={"ability_warlock_shadow_bolt_cost_pct": 0.04,
                "ability_warlock_immolate_cost_pct": 0.04,
                "ability_warlock_searing_pain_cost_pct": 0.04},
       connected_to=["bane"],
       source="WotLK row 1, built verbatim for the spells that exist: "
              "'Reduces the Mana cost of your Destruction spells by "
              "4%/7%/10%.' _cost_pct is A FRACTION and POSITIVE IS A "
              "REDUCTION, which is the opposite sign to every other _pct "
              "key in this file.")

T.node("demonic_power", "Demonic Power",
       "Increases your demon's damage by 5% per rank.",
       1, 0, 2, effects={"pet_damage": 0.05},
       connected_to=["bane"],
       source="WotLK row 2: 'Reduces the cooldown of your Succubus' Lash of "
              "Pain by 6 sec and reduces the casting time of your Imp's "
              "Firebolt by 0.5 sec.' Individual PET ABILITIES are not "
              "addressable and there are no cast times, so it becomes "
              "pet_damage - one of only THREE live pet keys (pet_damage, "
              "pet_health, pet_armor; pet.py:139-146). pet_crit and "
              "pet_haste are DEAD, measured on a live pet.")

T.node("shadowburn", "Shadowburn",
       "Teaches Shadowburn, a soul spent for an instant kill.",
       1, 2, 1, node_type="active",
       effects={"unlock_ability": "warlock_shadowburn"},
       connected_to=["bane"],
       source="WotLK row 2, kept - the ONLY unlock for warlock_shadowburn, "
              "which is requires_talent. At its real row.")

T.node("ruin", "Ruin",
       "Increases the critical damage of your spells by 8% per rank.",
       1, 4, 5, effects={"crit_damage_spell": 0.08},
       connected_to=["shadowburn"],
       source="WotLK row 2, built close to verbatim: 'Increases the "
              "critical strike damage bonus of your Destruction spells by "
              "20%-100%.' Scaled down hard: the real 100% assumes an 80-"
              "level raid environment, and Frontier fights run 2-3 turns on "
              "trash and 5-6 on a boss, so a doubled crit bonus would make "
              "a single lucky Shadow Bolt the whole encounter. "
              "crit_damage_spell IS LIVE - it is read at abilities.py:1460 "
              "INSIDE A TERNARY, which is why a literal read-site probe "
              "reports nothing for it and why it was nearly declared dead.")

# ----------------------------------------------------- tier 2 (rows 3-4)
T.node("intensity", "Intensity",
       "Reduces the cost of your Immolate and Searing Pain by 5% per rank.",
       2, -6, 2,
       effects={"ability_warlock_immolate_cost_pct": 0.05,
                "ability_warlock_searing_pain_cost_pct": 0.05},
       connected_to=["molten_skin"],
       source="WotLK row 3: 'Reduces the pushback suffered from damaging "
              "attacks while casting or channeling any Destruction spell by "
              "70%.' DEPARTURE - there are no cast times and therefore NO "
              "PUSHBACK to reduce. Being able to keep channelling becomes "
              "being able to afford it, which is the SAME PRECEDENT used "
              "for Fel Concentration in warlock_affliction - the two "
              "pushback talents in this class are translated the same way "
              "deliberately, so the pattern is legible rather than "
              "ad-hoc. Second of three cast-time talents.")

T.node("destructive_reach", "Destructive Reach",
       "Reduces the threat your spells generate by 10% per rank.",
       2, -4, 2,
       effects={"threat_multiplier": -0.10},
       connected_to=["molten_skin"],
       source="WotLK row 3, built for the half that works: 'Increases the "
              "range of your Destruction spells by 10%/20% and reduces "
              "threat caused by 5%/10%.' THERE IS NO RANGE OR POSITIONING "
              "in this engine at all, so only the threat half survives, at "
              "the doubled rate to keep the node worth two points. "
              "threat_multiplier is TALENT-CHANNEL ONLY - it would be "
              "SILENT DEAD DATA inside a proc's stat_mods, which is the "
              "single most common bug class in this project.")

T.node("improved_searing_pain", "Improved Searing Pain",
       "Increases the critical strike chance of your Searing Pain by 4% per "
       "rank.",
       2, -2, 3,
       effects={"ability_warlock_searing_pain_crit": 4.0},
       connected_to=["cataclysm"],
       source="WotLK row 3, built verbatim: 'Increases the critical strike "
              "chance of your Searing Pain spell by 4%/7%/10%.' "
              "ability_<id>_crit is PERCENTAGE POINTS while "
              "ability_<id>_crit_damage next door is a FRACTION - and a "
              "greedy regex in probe_talent_key.py once mis-split this very "
              "key family, falsely accusing all 20 legitimate _crit_damage "
              "keys in the project.")

T.node("backlash", "Backlash",
       "Increases your spell critical strike chance by 1% per rank, and "
       "being struck has a 8% chance to empower your next spells.",
       2, 0, 3,
       effects={"crit_chance_spell": 1.0},
       proc={"trigger": "on_damage_taken", "chance": 8, "icd": 1,
             "apply_effect": {"effect_id": "backlash", "name": "Backlash",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"damage_dealt_pct": 15.0},
                              "on_target": False}},
       connected_to=["cataclysm"],
       source="WotLK row 4, both halves built: 'Increases your critical "
              "strike chance with spells by 1%-3% and gives you a 8%-25% "
              "chance when hit by a physical attack to reduce the cast time "
              "of your next Shadow Bolt or Incinerate by 100%.' The crit "
              "half is verbatim. The instant-cast half becomes damage, "
              "since there are no cast times - but THE TRIGGER IS REAL and "
              "is kept, which is what makes this a proc rather than another "
              "flat node. crit_chance_spell is POINTS as a talent effect; "
              "the proc's damage_dealt_pct is POINTS TOO but is the ONLY "
              "damage key a status effect can carry (abilities.py:1680) - "
              "spell_damage there would be silently dead.")

T.node("improved_immolate", "Improved Immolate",
       "Increases the damage of your Immolate by 5% per rank.",
       2, 2, 3,
       effects={"ability_warlock_immolate_damage": 0.05},
       connected_to=["ruin"],
       source="WotLK row 4, built verbatim: 'Increases the initial damage "
              "of your Immolate spell by 5%/10%/15%.' Stacks with Aftermath "
              "and Bane, as all three real talents do.")

T.node("devastation", "Devastation",
       "Increases your spell critical strike chance by 5%.",
       2, 4, 1, effects={"crit_chance_spell": 5.0},
       connected_to=["ruin"],
       source="WotLK row 4, built verbatim: 'Increases the critical strike "
              "chance of your Destruction spells by 5%.' A 1-point node for "
              "5 points of crit is the real tree's own shape and is the "
              "natural prerequisite for Emberstorm above it. "
              "crit_chance_spell is PERCENTAGE POINTS - note hit_chance_"
              "spell, by contrast, IS DEAD as a talent key.")

# ----------------------------------------------------- tier 3 (row 5)
T.node("nether_protection", "Nether Protection",
       "Being hit by a spell has a 10% chance per rank to reduce spell "
       "damage taken by 20% for 2 turns.",
       3, -2, 3,
       proc={"trigger": "on_damage_taken", "chance": 10, "icd": 1,
             "apply_effect": {"effect_id": "nether_protection",
                              "name": "Nether Protection",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"spell_damage_taken_pct": -20.0},
                              "on_target": False}},
       connected_to=["backlash"],
       source="WotLK row 5, built close to verbatim: 'After being hit with "
              "a spell, you have a 10%-30% chance to gain Nether "
              "Protection, reducing all damage by that spell school by 30% "
              "for 8 sec.' DEPARTURE on ONE clause: it cannot be "
              "school-specific, because proc['school'] only TYPES a "
              "damage_flat payload and is NOT a trigger-side filter, and "
              "there is no on-hit-by-school trigger. So it reduces spell "
              "damage generally, at 20% rather than 30% to pay for being "
              "broader. CRITICAL: spell_damage_taken_pct is POINTS INSIDE A "
              "STATUS EFFECT (hence -20.0) and a FRACTION as a talent "
              "effect - Molten Skin two tiers down uses the fraction form "
              "of its sibling key. 8 sec is 2 turns.")

T.node("emberstorm", "Emberstorm",
       "Increases your Fire spell damage by 2% per rank.",
       3, 0, 5, effects={"fire_spell_damage": 0.02},
       connected_to=["devastation"],
       source="WotLK row 5, built verbatim: 'Increases the damage done by "
              "your Fire spells by 2%-10%.' USES THE PER-SCHOOL KEY "
              "DELIBERATELY: fire_spell_damage is built as "
              "f'{school}_spell_damage' at abilities.py:1371, which walks "
              "EVERY COMPONENT of a school list, so a literal grep cannot "
              "see it. This is the family that caused arcane_spell_damage "
              "to be WRONGLY DECLARED DEAD earlier in this project. It is "
              "LIVE and is the correct key for a school-scoped talent.")

# ----------------------------------------------------- tier 4 (rows 6-7)
T.node("conflagrate", "Conflagrate",
       "Teaches Conflagrate, consuming your Immolate for a burst of fire.",
       4, -4, 1, node_type="active",
       effects={"unlock_ability": "warlock_conflagrate"},
       connected_to=["nether_protection"],
       source="WotLK row 6, kept - the ONLY unlock for "
              "warlock_conflagrate, which is requires_talent. At its real "
              "row; the outgoing tree had it two tiers lower.")

T.node("soul_leech", "Soul Leech",
       "Your direct damage spells have a 10% chance per rank to heal you "
       "for 20% of the damage.",
       4, -2, 3,
       proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
             "ability_filter": ["warlock_shadow_bolt", "warlock_immolate",
                                "warlock_searing_pain",
                                "warlock_conflagrate"],
             "leech_pct": 0.20},
       connected_to=["nether_protection"],
       source="WotLK row 6, built close to verbatim: 'Gives your Shadow "
              "Bolt, Shadowburn, Soul Fire, Incinerate, Conflagrate, Chaos "
              "Bolt and Searing Pain spells a 10%-30% chance to return "
              "health equal to 20% of the damage caused.' The chance, the "
              "20% return and the ability list (for the spells that exist) "
              "are all real. leech_pct is one of only THREE payloads that "
              "read the triggering hit's amount, so this genuinely scales "
              "off damage dealt. ability_filter is validated by the kit "
              "against the real ability list, which is what catches a typo "
              "here instead of it silently never firing.")

T.node("pyroclasm", "Pyroclasm",
       "Your Conflagrate and Searing Pain crits raise your damage by 2% per "
       "rank for 3 turns.",
       4, 0, 3,
       proc={"trigger": "on_crit", "chance": 34, "icd": 1,
             "ability_filter": ["warlock_conflagrate",
                                "warlock_searing_pain"],
             "apply_effect": {"effect_id": "pyroclasm", "name": "Pyroclasm",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"damage_dealt_pct": 6.0},
                              "on_target": False}},
       connected_to=["soul_leech"],
       source="WotLK row 6, built close to verbatim: 'Your Conflagrate, "
              "Searing Pain and Soul Fire spells have a 100% chance to "
              "increase the damage you deal with all spells by 2%-6% for 10 "
              "sec.' Soul Fire does not exist. CHANCE IS 34, NOT THE REAL 100%, "
              "and that is a deliberate correction: a proc's PAYLOAD cannot "
              "scale with points, only its CHANCE can, so a 3-rank node at "
              "100% would make ranks 2 and 3 BUY LITERALLY NOTHING. The "
              "first draft of this file did exactly that and wrote a source "
              "note defending it; check_talent_balance.py caught all four "
              "such nodes across the three Warlock trees. 34 x 3 = 102, "
              "clamped to 100, so full rank reaches the real certainty while "
              "each point buys a third of it. An icd of 1 stops a crit streak "
              "stacking it. 10 sec is 3 turns, inside the measured window.")

T.node("shadow_and_flame", "Shadow and Flame",
       "Your Shadow Bolt has a 8% chance per rank to grant 60 spell power "
       "for 3 turns.",
       4, 2, 5,
       proc={"trigger": "on_damage_cast", "chance": 8, "icd": 0,
             "ability_filter": ["warlock_shadow_bolt"],
             "apply_effect": {"effect_id": "shadow_and_flame",
                              "name": "Shadow and Flame",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"spell_power": 60},
                              "on_target": False}},
       connected_to=["emberstorm"],
       source="WotLK row 7, built close to verbatim: 'Your Shadow Bolt and "
              "Incinerate spells have a 20%-100% chance to increase spell "
              "power by 180 for 10 sec.' Incinerate does not exist. The "
              "chance is rank-scaled (8 x 5 = 40% at full rank, well under "
              "the real 100% because 180 spell power is an 80-level raid "
              "number and 60 is sized for 60). spell_power is FLAT in a "
              "status effect, and it IS status-readable - "
              "_recalculate_derived_stats folds status effects into the "
              "SAME `bonuses` pool as gear and talents (character.py:1218), "
              "which is the measurement that cleared ten keys wrongly "
              "accused by the first draft of qa_proc_stat_mods.py.")

T.node("improved_soul_leech", "Improved Soul Leech",
       "Your direct damage spells have a 8% chance per rank to restore 80 "
       "mana.",
       4, 4, 2,
       proc={"trigger": "on_damage_cast", "chance": 8, "icd": 0,
             "ability_filter": ["warlock_shadow_bolt", "warlock_immolate",
                                "warlock_searing_pain",
                                "warlock_conflagrate"],
             "grant_resource": {"resource": "mana", "amount": 80}},
       connected_to=["soul_leech"],
       source="WotLK row 7: 'Your Soul Leech effect also restores mana to "
              "you and your summoned demon equal to 2% of maximum mana, and "
              "has a 100% chance to grant up to 10 party or raid members "
              "mana regeneration.' THREE DEPARTURES, all forced: a NESTED "
              "proc inside apply_effect works but nothing can trigger off "
              "ANOTHER PROC firing, so this is its own trigger on the same "
              "ability list rather than a rider on Soul Leech; demons have "
              "NO RESOURCE; and A TALENT EFFECT CAN NEVER REACH AN ALLY "
              "(only a party-targeted ABILITY can, abilities.py:2064), so "
              "the raid half is lost. grant_resource takes a FLAT amount - "
              "there is no pct_max - so the real 2% cannot be expressed and "
              "80 is sized against a level-60 warlock's pool. Warlock "
              "resource confirmed MANA before authoring, per the standing "
              "check-the-resource-first rule.")

# ----------------------------------------------------- tier 5 (rows 8-9)
T.node("backdraft", "Backdraft",
       "Your Conflagrate quickens your casting by 10% per rank for 2 turns.",
       5, -4, 3,
       proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
             "ability_filter": ["warlock_conflagrate"],
             "apply_effect": {"effect_id": "backdraft", "name": "Backdraft",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 30},
                              "on_target": False}},
       connected_to=["soul_leech"],
       source="WotLK row 8: 'When you cast Conflagrate, the cast time and "
              "global cooldown of your next three Destruction spells is "
              "reduced by 10%-30%.' DEPARTURE - no cast times and no global "
              "cooldown, and NOTHING COUNTS 'your next three spells' "
              "either (there is no cast counter, streak or accumulator of "
              "any kind in this engine). Delivered as haste on a timer "
              "instead, which is the nearest thing the engine has to "
              "casting faster. Third and last of the three cast-time "
              "talents. CHANCE IS 34, NOT THE REAL 100%, for the same reason "
              "as Pyroclasm above: only a proc's chance scales with points, "
              "so a 3-rank node at 100% gives ranks 2 and 3 nothing at all. "
              "34 x 3 clamps to 100 at full rank.")

T.node("shadowfury", "Shadowfury",
       "Teaches Shadowfury, slamming the ground to stun everything near.",
       5, -2, 1, node_type="active",
       effects={"unlock_ability": "warlock_shadowfury"},
       connected_to=["backdraft"],
       source="WotLK row 8, kept - the ONLY unlock for warlock_shadowfury, "
              "which is requires_talent. At its real row.")

T.node("empowered_imp", "Empowered Imp",
       "Increases your demon's damage by 10% per rank.",
       5, 0, 3, effects={"pet_damage": 0.10},
       connected_to=["shadow_and_flame"],
       source="WotLK row 8: 'Increases the damage done by your Imp by "
              "10%-30%, and all critical hits done by your Imp have a 100% "
              "chance to increase your spell critical hit chance for your "
              "next spell by 100%.' The damage half is VERBATIM. The crit "
              "feedback half is unbuildable at the root: PETS NEVER FIRE "
              "PROCS - there is no fire_proc_trigger anywhere in "
              "entities/pet.py - and there is no guaranteed-crit key "
              "either, so both halves of that clause are blocked.")

T.node("fire_and_brimstone", "Fire and Brimstone",
       "Increases the damage of your Chaos Bolt and Conflagrate by 3% per "
       "rank.",
       5, 2, 5,
       effects={"ability_warlock_chaos_bolt_damage": 0.03,
                "ability_warlock_conflagrate_damage": 0.03},
       connected_to=["shadow_and_flame"],
       source="WotLK row 9: 'Increases the damage of your Incinerate and "
              "Chaos Bolt on targets afflicted by your Immolate by 2%-10%, "
              "and the critical strike chance of your Conflagrate by "
              "2%-10%.' DEPARTURE - NOTHING READS A DEBUFF ON THE TARGET, "
              "which is one of the hardest confirmed engine limits and the "
              "same gap that blocks conditional talents in four other "
              "classes. The Immolate condition is therefore dropped and the "
              "bonus is unconditional, at 3% per rank rather than the real "
              "2% because it no longer has a setup cost. Conflagrate takes "
              "damage rather than crit so the node reads as one effect.")

# ----------------------------------------------------- tier 6 (row 10)
T.node("chaos_bolt", "Chaos Bolt",
       "Teaches Chaos Bolt, a bolt that cannot be resisted.",
       6, 0, 1, node_type="active",
       effects={"unlock_ability": "warlock_chaos_bolt"},
       connected_to=["fire_and_brimstone"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "warlock_chaos_bolt, which is requires_talent. At its real "
              "row.")


def main():
    return T.write(was="23 nodes, 66 points - 8 proc, 8 ability-scoped, "
                       "3 flat stat, 4 unlock")


if __name__ == "__main__":
    sys.exit(main())
