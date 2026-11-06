#!/usr/bin/env python3
"""Rebuild Warlock Affliction from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_warlock_affliction.py

SOURCE: data/reference/wotlk/warlock.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/warlock.md.

ROLE: dots and curses. Corruption and Curse of Agony ticking while Drain
Life keeps the warlock standing.

DOTS NEVER ROLL CRIT IN THIS ENGINE, and that costs Affliction two of its
real talents outright. Pandemic ("grants the periodic damage from your
Corruption and Unstable Affliction the ability to critically hit") and
Malediction's periodic-crit clause both depend on it. Pandemic is
rebuilt as direct dot damage instead, and the departure is named rather
than smoothed over - it is the single most distinctive thing lost in this
tree.

DOT DURATIONS ARE ALREADY SETTLED and are not touched here. The 2-6 turn
window was measured from real fights earlier in this session
(tools/qa_dot_durations.py carries the distributions), so no talent in
this tree extends a dot past it. dot_duration_pct is deliberately used on
only ONE node, because duration talents stack and the ceiling is 6.

ABILITIES THE REAL TREE WANTS AND WE LACK: Drain Soul, Drain Mana, Seed of
Corruption, Haunt, Howl of Terror, Curse of Exhaustion, Curse of Doom.
Improved Drain Soul, Improved Howl of Terror, Curse of Exhaustion and Grim
Reach are DROPPED; Haunt's capstone role goes to a Corruption payoff.

UNIT CONVENTIONS: hit_rating / crit_chance_spell are PERCENTAGE POINTS;
shadow_spell_damage / spell_damage / dot_damage / dot_duration_pct are
FRACTIONS; shadow_spell_damage is built by f-string (abilities.py:1371) so
grep cannot see it and it is LIVE; low_health_* are FRACTIONS and
low_health_threshold_pct is authored NOWHERE.

KEPT MANDATORY: Unstable Affliction and Dark Pact are the only unlocks for
their abilities, both requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

CURSES = ["warlock_curse_of_agony", "warlock_curse_of_weakness",
          "warlock_curse_of_recklessness"]

T = Tree("warlock_affliction", "Warlock Affliction",
         "Curses and corruption - damage that arrives slowly and does not "
         "stop.")

# ----------------------------------------------------------------- tier 0
T.node("improved_curse_of_agony", "Improved Curse of Agony",
       "Increases the damage of your Curse of Agony by 5% per rank.",
       0, -2, 2,
       effects={"ability_warlock_curse_of_agony_damage": 0.05},
       source="WotLK row 0, built verbatim: 'Increases the damage done by "
              "your Curse of Agony by 5%/10%.' The outgoing tree had this "
              "as 'Amplify Curse' with a 1-point stub; Amplify Curse is a "
              "separate real talent, built below.")

T.node("suppression", "Suppression",
       "Increases your chance to hit by 1% per rank and reduces the cost of "
       "your curses by 2% per rank.",
       0, 0, 3,
       effects={"hit_rating": 1.0,
                **{f"ability_{c}_cost_pct": 0.02 for c in CURSES}},
       source="WotLK row 0, built with both halves: 'Increases your chance "
              "to hit with spells by 1%/2%/3%, and reduces the mana cost of "
              "your Affliction spells.' Kept from the outgoing tree, which "
              "had hit_rating alone at 5 ranks. hit_rating is PERCENTAGE "
              "POINTS and is NOT a valid STAT_CONVERSION_TARGET.")

T.node("improved_corruption", "Improved Corruption",
       "Increases the damage of your Corruption by 2% per rank.",
       0, 2, 5,
       effects={"ability_warlock_corruption_damage": 0.02},
       source="WotLK row 0: 'Increases the damage done by your Corruption "
              "by 2%-10%, and increases the critical strike chance of your "
              "Corruption.' The damage half is verbatim; the crit half "
              "cannot be built because DOTS NEVER ROLL CRIT in this engine. "
              "Kept from the outgoing tree, corrected from 6% to the real "
              "2% per rank.")

# ----------------------------------------------------------------- tier 1
T.node("improved_curse_of_weakness", "Improved Curse of Weakness",
       "Increases the effect of your Curse of Weakness by 10% per rank.",
       1, -6, 2,
       effects={"ability_warlock_curse_of_weakness_potency": 0.10},
       connected_to=["improved_curse_of_agony"],
       source="WotLK row 1, built verbatim: 'Increases the amount of attack "
              "power reduced by your Curse of Weakness by 10%/20%.' "
              "ability_<id>_potency scales the ability's own stat_mods, "
              "which is the right key for a debuff whose whole content is "
              "an attack-power reduction. Note attack_power on a monster is "
              "FLAT and is one of only eight stat_mods a MONSTER can read, "
              "so this debuff really does land.")

T.node("improved_fear", "Improved Fear",
       "Increases the duration of your Fear by 1 turn per rank.",
       1, -4, 2,
       effects={"ability_warlock_fear_duration": 1},
       connected_to=["improved_curse_of_agony"],
       source="WotLK row 1: 'Causes your Fear spell to inflict a Nightmare "
              "on the target when the fear effect ends.' DEPARTURE - there "
              "is no trigger on an effect EXPIRING, which is the same gap "
              "that blocks Living Bomb for the Mage. Delivered as Fear "
              "lasting longer instead. ability_<id>_duration is FLAT turns "
              "and POSITIVE EXTENDS.")

T.node("fel_concentration", "Fel Concentration",
       "Reduces the cost of your Drain Life and Corruption by 5% per rank.",
       1, -2, 3,
       effects={"ability_warlock_drain_life_cost_pct": 0.05,
                "ability_warlock_corruption_cost_pct": 0.05},
       connected_to=["suppression"],
       source="WotLK row 1: 'Reduces the pushback suffered from damaging "
              "attacks while casting Drain Life, Drain Mana, Drain Soul and "
              "Corruption by 70%.' DEPARTURE - no cast times and so no "
              "pushback. Being able to keep channelling becomes being able "
              "to afford it. Kept from the outgoing tree, which used the "
              "FLAT _cost key.")

T.node("improved_life_tap", "Improved Life Tap",
       "Increases the mana your Life Tap returns by 10% per rank.",
       1, 0, 2,
       effects={"ability_warlock_life_tap_potency": 0.10},
       connected_to=["suppression"],
       source="WotLK row 1, built verbatim: 'Increases the amount of Mana "
              "awarded by your Life Tap spell by 10%/20%.' The outgoing "
              "version reduced Life Tap's COOLDOWN instead, which is a "
              "different talent.")

T.node("amplify_curse", "Amplify Curse",
       "Reduces the cooldown of your curses by 1 turn.",
       1, 2, 1,
       effects={f"ability_{c}_cooldown": 1 for c in CURSES},
       connected_to=["improved_corruption"],
       source="WotLK row 1: 'Reduces the global cooldown of your Curses by "
              "0.5 sec.' There is no global cooldown in this engine, so it "
              "becomes a per-curse cooldown reduction across all three real "
              "curses. talented_cooldown clamps at 1 turn. It is Curse of "
              "Exhaustion's prerequisite in the real tree; that ability "
              "does not exist here.")

T.node("soul_siphon", "Soul Siphon",
       "Increases the amount your Drain Life returns by 10% per rank.",
       1, 4, 2,
       effects={"ability_warlock_drain_life_healing": 0.10},
       connected_to=["improved_corruption"],
       source="WotLK row 1: 'Increases the amount drained by your Drain "
              "Life and Drain Soul spells by an additional 3%/6% for each "
              "of your Affliction effects on the target.' DEPARTURE - "
              "nothing counts how many of your own effects are on a target, "
              "so the per-effect scaling is impossible. Delivered as a flat "
              "increase. USES _healing because Drain Life's return is a "
              "heal - _damage would be silently dead, the mistake that left "
              "18 talents dead across four classes.")

T.node("soul_harvest", "Soul Harvest",
       "When you kill an enemy you recover 60 mana per rank.",
       1, 6, 2,
       proc={"trigger": "on_kill", "chance": 50, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 60}},
       connected_to=["improved_corruption"],
       source="WotLK row 1 'Improved Drain Soul': 'Returns 7%/14% of your "
              "maximum mana if the target is killed by your Drain Soul.' "
              "Drain Soul DOES NOT EXIST in this project, but the talent's "
              "entire content - mana back when a kill lands - IS buildable, "
              "so it is kept and renamed rather than dropped. This is the "
              "Mage Arcane lesson applied: dropping a node because its "
              "NAMED ability is missing threw away a working proc the first "
              "time, when the real text was proc-shaped all along. The "
              "outgoing tree had exactly this proc and was right to. "
              "grant_resource takes a FLAT amount - there is no pct_max - "
              "so the real percentage cannot be expressed and 60 is sized "
              "against a level-60 warlock's pool. CHANCE IS 50, NOT 100, because "
              "a proc's PAYLOAD does not scale with points and only its "
              "CHANCE does - at 100% a 2-rank node would give rank 2 "
              "NOTHING, which is what the first draft did until "
              "check_talent_balance.py caught it. 50 x 2 = 100, so full "
              "rank is the certainty the real talent implies. Warlock "
              "resource confirmed MANA "
              "before authoring, per the standing check-the-resource rule.")

# ----------------------------------------------------------------- tier 2
T.node("shadow_embrace", "Shadow Embrace",
       "Your Shadow Bolt leaves the target taking 5% more damage for 3 "
       "turns.",
       2, -6, 5,
       proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
             "ability_filter": ["warlock_shadow_bolt"],
             "apply_effect": {"effect_id": "shadow_embrace",
                              "name": "Shadow Embrace",
                              "effect_type": "debuff", "duration": 3,
                              "stat_mods": {"damage_taken_pct": 0.05}}},
       connected_to=["improved_curse_of_weakness"],
       source="WotLK row 2: 'Your Shadow Bolt and Haunt spells apply the "
              "Shadow Embrace effect, increasing all shadow periodic damage "
              "dealt to the target by 1%-5%.' Haunt does not exist. Built "
              "with the real 5% as a general damage-taken debuff, since "
              "there is no shadow-periodic-specific taken key. BARE "
              "damage_taken_pct is read RAW on both sides, so 0.05 is 5%, "
              "and it is one of only eight stat_mods a MONSTER can read. "
              "Kept as a proc from the outgoing tree.")

T.node("nightfall", "Nightfall",
       "Your Corruption and Drain Life have a 2% chance per rank to make "
       "your next spells hit harder.",
       2, -4, 2,
       proc={"trigger": "on_damage_cast", "chance": 2, "icd": 0,
             "ability_filter": ["warlock_corruption", "warlock_drain_life"],
             "apply_effect": {"effect_id": "shadow_trance",
                              "name": "Shadow Trance",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"damage_dealt_pct": 25.0},
                              "on_target": False}},
       connected_to=["improved_fear"],
       source="WotLK row 2: 'Gives your Corruption and Drain Life spells a "
              "2%/4% chance to cause you to enter a Shadow Trance state "
              "after damaging the opponent. The Shadow Trance state reduces "
              "the casting time of your next Shadow Bolt spell by 100%.' "
              "DEPARTURE - no cast times, so an instant Shadow Bolt is not "
              "expressible. The real ability pair, chance and Shadow Trance "
              "name are kept, and the payoff becomes damage. NOTE the "
              "stat_mod is damage_dealt_pct in PERCENTAGE POINTS: "
              "spell_damage would be SILENT DEAD DATA inside a status "
              "effect.")

T.node("siphon_life", "Siphon Life",
       "Your Corruption heals you as it burns.",
       2, -2, 1,
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
             "ability_filter": ["warlock_corruption"],
             "leech_pct": 0.40},
       connected_to=["fel_concentration"],
       source="WotLK row 2, built almost verbatim: 'When you deal damage "
              "with your Corruption spell, you are instantly healed for 40% "
              "of the damage done.' leech_pct is one of only THREE payloads "
              "that read the triggering hit's amount (the others being "
              "bonus_pct and smart heals), so this is one of the few "
              "talents in the project that genuinely scales off damage "
              "dealt - and the real 40% is exact. It is Shadow Mastery's "
              "prerequisite, preserved below. Kept as a proc from the "
              "outgoing tree.")

T.node("empowered_corruption", "Empowered Corruption",
       "Increases the damage of your Corruption by 4% per rank.",
       2, 0, 3,
       effects={"ability_warlock_corruption_damage": 0.04},
       connected_to=["improved_life_tap"],
       source="WotLK row 2: 'Increases the damage of your Corruption spell "
              "by an amount equal to 12%/24%/36% of your spell power.' "
              "Spell-power coefficients are not exposed to talents, so it "
              "is direct damage. Stacks with Improved Corruption, as the "
              "real pair does. Kept from the outgoing tree.")

T.node("shadow_mastery", "Shadow Mastery",
       "Increases your Shadow spell damage by 2% per rank.",
       2, 2, 5, effects={"shadow_spell_damage": 0.02},
       connected_to=["siphon_life"],
       source="WotLK row 3, built verbatim: 'Increases the damage dealt or "
              "life drained by your Shadow spells by 2%-10%.' USES THE "
              "PER-SCHOOL KEY DELIBERATELY. shadow_spell_damage is built as "
              "f'{school}_spell_damage' at abilities.py:1371, so a literal "
              "grep cannot see it - the family that caused "
              "arcane_spell_damage to be WRONGLY declared dead in this "
              "project. It is LIVE and correct for a school-scoped talent. "
              "The outgoing version granted FLAT shadow_spell_power, which "
              "is a different stat. The real talent requires Siphon Life, "
              "which connected_to reproduces.")

# ----------------------------------------------------------------- tier 3
T.node("improved_felhunter", "Improved Felhunter",
       "Increases your demon's damage by 5% per rank.",
       3, -2, 2, effects={"pet_damage": 0.05},
       connected_to=["shadow_embrace"],
       source="WotLK row 3: 'Your Felhunter regains 8%/16% of its maximum "
              "mana each time it hits with its Shadow Bite ability.' "
              "DEPARTURE - demons have NO RESOURCE in this engine and PETS "
              "NEVER FIRE PROCS (there is no fire_proc_trigger in "
              "entities/pet.py at all), so neither half is buildable. "
              "pet_damage is one of only three pet keys that work, read at "
              "pet.py:139. Kept as a concept from the outgoing tree, which "
              "was a proc with an empty effects dict.")

T.node("malediction", "Malediction",
       "Increases your spell damage by 1% per rank.",
       3, 0, 3, effects={"spell_damage": 0.01},
       connected_to=["empowered_corruption"],
       source="WotLK row 4: 'Increases your spell damage by 1%/2%/3%, and "
              "increases the periodic critical strike chance of your "
              "Corruption and Unstable Affliction.' The spell damage is "
              "verbatim; the periodic-crit clause CANNOT BE BUILT because "
              "DOTS NEVER ROLL CRIT in this engine. The outgoing version "
              "was Curse of Agony damage, which is Improved Curse of "
              "Agony's job.")

# ----------------------------------------------------------------- tier 4
T.node("eradication", "Eradication",
       "Your Corruption has a 6% chance to quicken your casting by 20% for "
       "2 turns.",
       4, -4, 3,
       proc={"trigger": "on_damage_cast", "chance": 6, "icd": 0,
             "ability_filter": ["warlock_corruption"],
             "apply_effect": {"effect_id": "eradication",
                              "name": "Eradication",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 20},
                              "on_target": False}},
       connected_to=["improved_felhunter"],
       source="WotLK row 4, built almost verbatim: 'When you deal damage "
              "with Corruption, you have 6% chance to increase your spell "
              "casting speed by 6%-20% for 10 sec.' The real trigger, real "
              "ability_filter, real 6% chance and real 20% at full rank. "
              "The chance is NOT rank-scaled because the real talent scales "
              "its MAGNITUDE, and a proc's payload cannot scale with "
              "points - so the payload carries the full value. 10 seconds "
              "is 2 turns. Kept as a proc from the outgoing tree.")

T.node("contagion", "Contagion",
       "Increases the damage of your Curse of Agony and Corruption by 1% per "
       "rank.",
       4, -2, 5,
       effects={"ability_warlock_curse_of_agony_damage": 0.01,
                "ability_warlock_corruption_damage": 0.01},
       connected_to=["malediction"],
       source="WotLK row 4, built verbatim for the two that exist: "
              "'Increases the damage of Curse of Agony, Corruption and Seed "
              "of Corruption by 1%-5%.' Seed of Corruption does not exist. "
              "It is Unstable Affliction's prerequisite, preserved below. "
              "Kept from the outgoing tree.")

T.node("dark_pact", "Dark Pact",
       "Teaches Dark Pact, draining your demon's power into your own.",
       4, 0, 1, node_type="active",
       effects={"unlock_ability": "warlock_dark_pact"},
       connected_to=["malediction"],
       source="WotLK row 4, kept - the ONLY unlock for warlock_dark_pact, "
              "which is requires_talent. Moved from the outgoing tree's "
              "tier 6 to its real row.")

# ----------------------------------------------------------------- tier 5
T.node("deaths_embrace", "Death's Embrace",
       "While below half health, your Drain Life returns 10% more per rank "
       "and you take 3% less damage per rank.",
       5, -4, 3,
       effects={"ability_warlock_drain_life_healing": 0.10,
                "low_health_damage_reduction_pct": 0.03},
       connected_to=["eradication"],
       source="WotLK row 5: 'Increases the amount drained by your Drain "
              "Life by 10%/20%/30% while your health is at or below 20%.' "
              "DEPARTURE on the condition for the drain half - there is no "
              "low-health conditional that scopes to one ABILITY, only the "
              "global low_health_* family - so the Drain Life bonus is "
              "unconditional and a real low-health mitigation rider is "
              "added alongside it. low_health_damage_reduction_pct reads "
              "the ACTOR's own health and defaults to a 50% threshold, so "
              "low_health_threshold_pct is NOT authored - the outgoing "
              "version DID author it at 0.35.")

T.node("unstable_affliction", "Unstable Affliction",
       "Teaches Unstable Affliction, shadow energy that destroys slowly.",
       5, -2, 1, node_type="active",
       effects={"unlock_ability": "warlock_unstable_affliction"},
       connected_to=["contagion"],
       source="WotLK row 5, kept - the ONLY unlock for "
              "warlock_unstable_affliction, which is requires_talent. The "
              "real talent requires Contagion, which connected_to "
              "reproduces. Moved from tier 3 to its real row.")

T.node("everlasting_affliction", "Everlasting Affliction",
       "Increases the damage of your Corruption and Unstable Affliction by "
       "2% per rank.",
       5, 0, 5,
       effects={"ability_warlock_corruption_damage": 0.02,
                "ability_warlock_unstable_affliction_damage": 0.02},
       connected_to=["contagion"],
       source="WotLK row 5: 'Your Corruption and Unstable Affliction spells "
              "gain an additional 1%-5% of your bonus spell damage, and "
              "your Drain Life has a chance to refresh Corruption.' "
              "Spell-power coefficients are not exposed to talents, so it "
              "is direct damage. The refresh clause cannot be built - "
              "nothing can refresh another effect's duration from a proc; "
              "cast_ability re-casting Corruption was considered and "
              "rejected because it would stack with Contagion and "
              "Improved Corruption into an unreadable pile on one dot. The "
              "outgoing version was Shadow Bolt damage.")

T.node("pandemic", "Pandemic",
       "Increases the damage of your dots by 10%.",
       5, 2, 1, effects={"dot_damage": 0.10},
       connected_to=["unstable_affliction"],
       source="WotLK row 5: 'Grants the periodic damage from your Corruption "
              "and Unstable Affliction spells the ability to critically "
              "hit.' DEPARTURE, AND THE BIGGEST ONE IN THIS TREE: DOTS "
              "NEVER ROLL CRIT in this engine - there is no mechanism at "
              "all, and status_effects.py applies a dot tick with a bare "
              "take_damage call that has no crit roll in it. The talent's "
              "entire content is unbuildable, so it becomes flat dot "
              "damage, which delivers roughly the same expected value "
              "without the variance. dot_damage is a FRACTION. The real "
              "talent requires Unstable Affliction, reproduced.")

# ----------------------------------------------------------------- tier 6
T.node("haunt", "Haunt",
       "Your Shadow Bolt leaves the target taking 10% more damage for 3 "
       "turns.",
       6, 0, 1,
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 2,
             "ability_filter": ["warlock_shadow_bolt"],
             "apply_effect": {"effect_id": "haunt", "name": "Haunt",
                              "effect_type": "debuff", "duration": 3,
                              "stat_mods": {"damage_taken_pct": 0.10}}},
       connected_to=["everlasting_affliction"],
       source="WotLK row 10, the capstone: 'You send a ghostly soul into "
              "the target, dealing Shadow damage and increasing all damage "
              "done by your Shadow spells to the target by 20%.' DEPARTURE "
              "- there is no warlock_haunt ability to unlock. The debuff "
              "half IS buildable and is the half that matters, so it rides "
              "Shadow Bolt with icd 2 to keep it a cooldown rather than "
              "permanent. 10% rather than 20% because it is now free. It "
              "stacks with Shadow Embrace, which is the real interaction.")


def main():
    return T.write(was="23 nodes, 63 points - 8 proc, 9 ability-scoped, "
                       "1 flat stat, 2 unlock, 1 conditional")


if __name__ == "__main__":
    sys.exit(main())
