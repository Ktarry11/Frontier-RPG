#!/usr/bin/env python3
"""Rebuild Priest Shadow from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_priest_shadow.py

SOURCE: data/reference/wotlk/priest.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/priest.md.

ROLE: Shadow damage over time. Shadow Word: Pain and Vampiric Touch
ticking while Mind Flay and Mind Blast do the direct work.

THIS TREE HAS FIVE MANDATORY UNLOCKS - more than any other in the project:
priest_shadowform, priest_silence, priest_mind_flay, priest_mind_sear and
priest_vampiric_touch are all requires_talent and all unlocked only from
here. Dropping any node would strand an ability
(qa_abilities_obtainable).

shadow_spell_damage IS LIVE AND GREP CANNOT SEE IT. It is built as
f"{real}_spell_damage" at abilities.py:1371, inside _school_damage_bonus,
which walks EVERY component of a school list - so a combined school like
['shadow','fire'] receives both keys. This is the exact family that caused
arcane_spell_damage to be WRONGLY declared dead in this project, published
in a commit message and a project doc before being corrected. Darkness
uses it deliberately.

SHADOWFORM IS A REAL FORM HERE, so require_form "shadowform" works on a
talent - three existing talents in the project already use it. Improved
Shadowform is gated on it.

STACKING IS THE WALL. Shadow Weaving ("stacks up to 5 times") and the real
Vengeance-style stacking talents cannot be built: max_stacks exists on
StatusEffect but NOTHING in this engine reads a stack count, so a 5-stack
effect is indistinguishable from a 1-stack one. Shadow Weaving is built as
a single-application buff at the full stacked value.

ABILITIES THE REAL TREE WANTS AND WE LACK: Shadow Word: Death, Devouring
Plague, Mind Control, Shadowfiend, Psychic Horror. Talents on those are
re-aimed or dropped; Psychic Horror is DROPPED (it is a weapon-drop
mechanic, and there are no weapons to drop).

UNIT CONVENTIONS: hit_rating / crit_chance_spell / spirit_pct / haste are
PERCENTAGE POINTS; shadow_spell_damage / spell_damage /
threat_generation_pct / ability_<id>_crit_damage are FRACTIONS;
ability_<id>_crit is PERCENTAGE POINTS; *_from_*_pct is a FRACTION read as
a raw multiplier.

THE DAMAGE KEY INSIDE A PROC'S stat_mods MUST BE damage_dealt_pct, IN
PERCENTAGE POINTS. all_damage, physical_damage, spell_damage and the
per-school <school>_spell_damage keys are read through
get_talent_effect (abilities.py:1606-1610), which sums TALENTS AND THE
CURRENT STANCE and nothing else - a status effect's stat_mods go to
get_status_stat_mod instead, and the damage path reads exactly one key
from there: damage_dealt_pct (abilities.py:1680-1683, divided by 100).
So a proc-applied buff carrying all_damage is SILENT DEAD DATA. Stances
look like a counter-example and are not: stance stat_mods are folded
into get_talent_effects (character.py:628), so they reach the talent
bus. Proc-applied buffs are not.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

#: The Mind spells, for Focused Mind and Mind Melt.
MIND = ["priest_mind_blast", "priest_mind_flay", "priest_mind_sear"]

T = Tree("priest_shadow", "Priest Shadow",
         "Shadow magic - creeping damage over time and the mind as a "
         "weapon.")

# ----------------------------------------------------------------- tier 0
T.node("spirit_tap", "Spirit Tap",
       "A killing blow floods you with Spirit for 3 turns.",
       0, -2, 3,
       proc={"trigger": "on_kill", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "spirit_tap",
                              "name": "Spirit Tap",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"spirit": 40},
                              "on_target": False}},
       source="WotLK row 0: 'Gives you a 33%-100% chance to gain a 100% "
              "bonus to your Spirit after killing a target that yields "
              "experience or honor.' Built with the real chance curve on "
              "the real trigger. Doubling Spirit is not expressible from a "
              "proc payload - spirit inside status stat_mods is FLAT - so "
              "+40 stands in. Kept as a proc from the outgoing tree, which "
              "had it at 5 ranks with flat spirit on the node itself. It is "
              "Improved Spirit Tap's prerequisite, preserved below.")

T.node("improved_spirit_tap", "Improved Spirit Tap",
       "Increases your Spirit by 2% per rank.",
       0, 0, 2, effects={"spirit_pct": 2.0},
       connected_to=["spirit_tap"],
       source="WotLK row 0, NEW to our tree: 'Your Mind Blast and Shadow "
              "Word: Death critical strikes have a 100% chance and your "
              "Mind Flay critical strikes have a 50% chance to increase "
              "your Spirit by 5%/10% for 8 sec.' DEPARTURE - the real "
              "talent needs per-ability crit triggers with different "
              "chances, and on_crit cannot be split that way. Delivered as "
              "a permanent Spirit increase at the real magnitude. "
              "spirit_pct is PERCENTAGE POINTS. The real talent requires "
              "Spirit Tap, which connected_to reproduces, and it feeds "
              "Twisted Faith at tier 5.")

T.node("darkness", "Darkness",
       "Increases your Shadow spell damage by 2% per rank.",
       0, 2, 5, effects={"shadow_spell_damage": 0.02},
       source="WotLK row 0, built verbatim: 'Increases your Shadow spell "
              "damage by 2%-10%.' USES THE PER-SCHOOL KEY DELIBERATELY. "
              "shadow_spell_damage is built as f'{school}_spell_damage' at "
              "abilities.py:1371, so a literal grep cannot see it - this is "
              "the exact family that led to arcane_spell_damage being "
              "WRONGLY declared dead in this project, published in a commit "
              "and a project doc before correction. It is LIVE, and it is "
              "the right key for a school-scoped damage talent. The "
              "outgoing version used the school-agnostic spell_damage, "
              "which also lifted the priest's Holy damage.")

# ----------------------------------------------------------------- tier 1
T.node("shadow_affinity", "Shadow Affinity",
       "Reduces the threat you generate by 8% per rank.",
       1, -6, 3, effects={"threat_generation_pct": -0.08},
       connected_to=["spirit_tap"],
       source="WotLK row 1: 'Reduces the threat generated by your Shadow "
              "spells by 8%-25%, and you receive 15% of your base mana when "
              "your Shadow Word: Pain is dispelled.' The threat half is "
              "built - there is no per-school threat key. There is no "
              "dispel trigger either. The outgoing version granted flat "
              "shadow_resistance, which is a defensive stat and not this "
              "talent.")

T.node("improved_psychic_scream", "Improved Psychic Scream",
       "Reduces the cooldown of your Psychic Scream by 1 turn per rank.",
       1, -4, 2,
       effects={"ability_priest_psychic_scream_cooldown": 1},
       connected_to=["spirit_tap"],
       source="WotLK row 1: 'Reduces the cooldown of your Psychic Scream "
              "spell by 2/4 sec.' Built verbatim as cooldown; the outgoing "
              "version increased its DURATION instead. It is Silence's "
              "prerequisite, preserved below.")

T.node("improved_shadow_word_pain", "Improved Shadow Word: Pain",
       "Increases the damage of your Shadow Word: Pain by 3% per rank.",
       1, -2, 2,
       effects={"ability_priest_shadow_word_pain_damage": 0.03},
       connected_to=["improved_spirit_tap"],
       source="WotLK row 1: 'Increases the damage of your Shadow Word: Pain "
              "spell by 3%/6%.' Built verbatim over the real 2 ranks; the "
              "outgoing version had 5 ranks of 5%, reaching 25%.")

T.node("improved_mind_blast", "Improved Mind Blast",
       "Reduces the cooldown of your Mind Blast by 1 turn per rank.",
       1, 0, 5,
       effects={"ability_priest_mind_blast_cooldown": 1},
       connected_to=["improved_spirit_tap"],
       source="WotLK row 1: 'Reduces the cooldown of your Mind Blast spell "
              "by 0.5-2.5 sec.' Built as cooldown, which is what the real "
              "talent does - 2.5 seconds is roughly 1 turn, and "
              "talented_cooldown clamps the result at 1 so five ranks "
              "cannot drive it to zero. The outgoing version increased Mind "
              "Blast's damage, which is Twisted Faith's clause.")

T.node("shadow_focus", "Shadow Focus",
       "Increases your chance to hit by 1% per rank and reduces the cost of "
       "your Mind spells by 2% per rank.",
       1, 2, 3,
       effects={"hit_rating": 1.0,
                "ability_priest_mind_blast_cost_pct": 0.02,
                "ability_priest_mind_flay_cost_pct": 0.02},
       connected_to=["darkness"],
       source="WotLK row 1, built with both halves: 'Increases your chance "
              "to hit with your Shadow spells by 1%/2%/3%, and reduces the "
              "mana cost of your Shadow spells by 2%/4%/6%.' hit_rating is "
              "PERCENTAGE POINTS and is NOT a valid STAT_CONVERSION_TARGET. "
              "Kept from the outgoing tree, corrected from 5 ranks to the "
              "real 3.")

T.node("mind_flay", "Mind Flay",
       "Teaches Mind Flay, assaulting the target's mind with Shadow energy.",
       1, 4, 1, node_type="active",
       effects={"unlock_ability": "priest_mind_flay"},
       connected_to=["darkness"],
       source="WotLK row 1, kept - the ONLY unlock for priest_mind_flay, "
              "which is requires_talent. Moved from tier 3 to its real "
              "row, which matters because four later talents in this tree "
              "modify Mind Flay.")

# ----------------------------------------------------------------- tier 2
T.node("silence", "Silence",
       "Teaches Silence, stilling an enemy's voice.",
       2, -6, 1, node_type="active",
       effects={"unlock_ability": "priest_silence"},
       connected_to=["improved_psychic_scream"],
       source="WotLK row 2, kept - the ONLY unlock for priest_silence, "
              "which is requires_talent. The real talent requires Improved "
              "Psychic Scream, which connected_to reproduces. Note the "
              "ENGINE has no silence key - the ability itself is where that "
              "is modelled, and there is nothing for a talent to add.")

T.node("veiled_shadows", "Veiled Shadows",
       "Reduces the cooldown of your Fade by 1 turn per rank.",
       2, -4, 2,
       effects={"ability_priest_fade_cooldown": 1},
       connected_to=["improved_psychic_scream"],
       source="WotLK row 2, NEW to our tree: 'Decreases the cooldown of "
              "your Fade ability by 3/6 sec, and reduces the cooldown of "
              "your Shadowfiend ability by 1/2 minutes.' Shadowfiend does "
              "not exist. 6 seconds is 2 turns over 2 ranks.")

T.node("vampiric_embrace", "Vampiric Embrace",
       "Your Shadow damage heals you for a fifth of what it deals.",
       2, -2, 1,
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
             "leech_pct": 0.20},
       connected_to=["improved_shadow_word_pain"],
       source="WotLK row 2: 'Fills you with the embrace of Shadow energy, "
              "causing you to be healed for 15% and other party members to "
              "be healed for 3% of any Shadow spell damage you deal.' Built "
              "with leech_pct, which is one of only THREE payloads that "
              "read the triggering hit's amount (the others being bonus_pct "
              "and smart heals) - so this is one of the few talents in the "
              "project that can scale off damage dealt. The party clause is "
              "dropped: a talent effect can never reach an ally. 20% "
              "against the real 15% compensates for losing that half. It is "
              "Improved Vampiric Embrace's and Shadowform's prerequisite, "
              "both preserved. The outgoing version granted "
              "max_health_pct.")

T.node("improved_vampiric_embrace", "Improved Vampiric Embrace",
       "Increases the healing you receive by 5% per rank.",
       2, 0, 2, effects={"healing_taken_pct": 0.05},
       connected_to=["vampiric_embrace"],
       source="WotLK row 2, NEW to our tree: 'Increases the healing "
              "received from Vampiric Embrace by 33%/67%.' DEPARTURE - "
              "nothing modifies a PROC's payload magnitude from outside it, "
              "so the leech cannot be scaled by another talent. Delivered "
              "as healing received, which lifts the leech along with "
              "everything else. The real talent requires Vampiric Embrace, "
              "reproduced.")

T.node("shadow_weaving", "Shadow Weaving",
       "Your Shadow damage weaves itself stronger, increasing Shadow damage "
       "by 10% for 4 turns.",
       2, 2, 3,
       proc={"trigger": "on_damage_cast", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "shadow_weaving",
                              "name": "Shadow Weaving",
                              "effect_type": "buff", "duration": 4,
                              "stat_mods": {"damage_dealt_pct": 10.0},
                              "on_target": False}},
       connected_to=["shadow_focus"],
       source="WotLK row 2: 'Your Shadow damage spells have a 33%-100% "
              "chance to increase the Shadow damage you deal by 2% for 15 "
              "sec. Stacks up to 5 times.' STACKING IS NOT BUILDABLE - "
              "max_stacks exists on StatusEffect but NOTHING in this engine "
              "reads a stack count, so a 5-stack effect is "
              "indistinguishable from a 1-stack one. Built as a single "
              "application at the FULL stacked value (5 x 2% = 10%), which "
              "reaches the same ceiling without the ramp. The real chance "
              "curve is kept. 15 seconds is 4 turns. Kept as a proc from "
              "the outgoing tree.")

T.node("focused_mind", "Focused Mind",
       "Reduces the cost of your Mind Blast, Mind Flay and Mind Sear by 5% "
       "per rank.",
       2, 4, 3,
       effects={"ability_priest_mind_blast_cost_pct": 0.05,
                "ability_priest_mind_flay_cost_pct": 0.05,
                "ability_priest_mind_sear_cost_pct": 0.05},
       connected_to=["mind_flay"],
       source="WotLK row 2: 'Reduces the mana cost of your Mind Blast, Mind "
              "Control, Mind Flay and Mind Sear spells by 5%/10%/15%.' "
              "Built verbatim for the three that exist. Kept from the "
              "outgoing tree, which used the FLAT _cost key on two of "
              "them.")

# ----------------------------------------------------------------- tier 3
T.node("mind_melt", "Mind Melt",
       "Increases the critical chance of your Mind spells by 2% per rank.",
       3, -1, 2,
       effects={"ability_priest_mind_blast_crit": 2.0,
                "ability_priest_mind_flay_crit": 2.0,
                "ability_priest_mind_sear_crit": 2.0},
       connected_to=["shadow_weaving"],
       source="WotLK row 3, NEW to our tree: 'Increases the critical strike "
              "chance of your Mind Blast, Mind Flay and Mind Sear spells by "
              "2%/4%, and increases the periodic damage of Mind Flay.' The "
              "crit half is built verbatim across all three real abilities. "
              "ability_<id>_crit is PERCENTAGE POINTS.")

T.node("improved_devouring_plague", "Improved Devouring Plague",
       "Increases the damage of your Shadow Word: Pain and Mind Sear by 5% "
       "per rank.",
       3, 1, 3,
       effects={"ability_priest_shadow_word_pain_damage": 0.05,
                "ability_priest_mind_sear_damage": 0.05},
       connected_to=["focused_mind"],
       source="WotLK row 3: 'Increases the periodic damage done by your "
              "Devouring Plague by 5%/10%/15%, and when you cast Devouring "
              "Plague you instantly deal damage equal to 10%/20%/30% of its "
              "total periodic effect.' DEPARTURE - Devouring Plague does "
              "not exist. Its role here is Shadow Word: Pain (the "
              "maintained Shadow dot) and Mind Sear (the AoE), so the "
              "periodic half lands on both. The instant-damage clause "
              "cannot be built - nothing front-loads a dot. Kept from the "
              "outgoing tree, which was a 1-point proc on Mind Sear.")

# ----------------------------------------------------------------- tier 4
T.node("improved_shadowform", "Improved Shadowform",
       "While in Shadowform, reduces the cooldown of your Fade by 1 turn "
       "per rank.",
       4, -5, 2,
       effects={"ability_priest_fade_cooldown": 1},
       require_form="shadowform",
       connected_to=["mind_melt"],
       source="WotLK row 4, NEW to our tree: 'Your Fade ability now has a "
              "100% chance to remove all movement impairing effects when "
              "used while in Shadowform, and reduces the cooldown of your "
              "Fade.' BUILT WITH THE REAL FORM CONDITION - shadowform is a "
              "real form id here and three existing talents in the project "
              "already gate on it, so require_form works. Movement "
              "impairment does not exist. The real talent requires "
              "Shadowform, which connected_to reproduces via the unlock "
              "node below.")

T.node("shadowform", "Shadowform",
       "Teaches Shadowform, wrapping you in Shadow.",
       4, -3, 1, node_type="active",
       effects={"unlock_ability": "priest_shadowform"},
       connected_to=["vampiric_embrace"],
       source="WotLK row 4, kept - the ONLY unlock for priest_shadowform, "
              "which is requires_talent. The real talent requires Vampiric "
              "Embrace, which connected_to reproduces. Moved from tier 2 to "
              "its real row. It is Vampiric Touch's prerequisite, "
              "preserved below.")

T.node("shadow_power", "Shadow Power",
       "Increases the critical damage of your Mind Blast and Mind Flay by "
       "20% per rank.",
       4, -1, 5,
       effects={"ability_priest_mind_blast_crit_damage": 0.20,
                "ability_priest_mind_flay_crit_damage": 0.20},
       connected_to=["shadowform"],
       source="WotLK row 4: 'Increases the critical strike damage bonus of "
              "your Mind Blast, Mind Flay, and Shadow Word: Death spells by "
              "20%-100%.' Built verbatim for the two that exist. "
              "ability_<id>_crit_damage is a FRACTION - and note this is "
              "the suffix whose parse must try the LONGEST match first, or "
              "ability_X_crit_damage reads as ability 'X_crit' plus field "
              "'damage'. The outgoing version granted flat crit CHANCE and "
              "flat shadow_spell_power, neither of which is this talent.")

T.node("misery", "Misery",
       "Increases your chance to hit by 1% per rank and your spell damage "
       "by 1% per rank.",
       4, 1, 3,
       effects={"hit_rating": 1.0, "spell_damage": 0.01},
       connected_to=["improved_devouring_plague"],
       source="WotLK row 4: 'Your Shadow Word: Pain, Mind Flay and Vampiric "
              "Touch spells also increase the chance for harmful spells to "
              "hit by 1%/2%/3%.' DEPARTURE - the real talent is a DEBUFF on "
              "the target that helps the whole raid; a talent effect can "
              "never reach an ally and nothing applies a hit-chance debuff "
              "to an enemy. Delivered as the priest's own accuracy, with a "
              "small damage rider since the raid-wide half is lost. Kept "
              "from the outgoing tree, which was per-ability damage only.")

# ----------------------------------------------------------------- tier 5
T.node("vampiric_touch", "Vampiric Touch",
       "Teaches Vampiric Touch, a wound that feeds on the mind.",
       5, -3, 1, node_type="active",
       effects={"unlock_ability": "priest_vampiric_touch"},
       connected_to=["shadowform"],
       source="WotLK row 5, kept - the ONLY unlock for "
              "priest_vampiric_touch, which is requires_talent. The real "
              "talent requires Shadowform, which connected_to reproduces. "
              "Moved from tier 4 to its real row. It is Dispersion's "
              "prerequisite, preserved below.")

T.node("pain_and_suffering", "Pain and Suffering",
       "Increases the damage of your Shadow Word: Pain by 4% per rank, and "
       "your Mind Flay refreshes it.",
       5, -1, 3,
       effects={"ability_priest_shadow_word_pain_damage": 0.04},
       proc={"trigger": "on_cast", "chance": 33, "icd": 0,
             "ability_filter": ["priest_mind_flay"],
             "cast_ability": "priest_shadow_word_pain"},
       connected_to=["shadow_power"],
       source="WotLK row 5, built with BOTH halves: 'Your Mind Flay has a "
              "33%-100% chance to refresh the duration of your Shadow Word: "
              "Pain on the target, and reduces the damage done to you by "
              "your own Shadow Word: Death.' DEPARTURE on the mechanism - "
              "nothing can refresh an existing effect's duration from a "
              "proc, so cast_ability RE-CASTS Shadow Word: Pain instead, "
              "which refreshes it by re-applying it (a same-effect_id "
              "application refreshes duration, status_effects.py). "
              "cast_ability does NOT check that the caster learned the "
              "ability, and Shadow Word: Pain is baseline, so this is safe. "
              "Shadow Word: Death does not exist. Kept as a proc from the "
              "outgoing tree, which had the damage half only.")

T.node("twisted_faith", "Twisted Faith",
       "Increases your spell power by 4% of your Spirit per rank and the "
       "damage of your Mind Flay and Mind Blast by 1% per rank.",
       5, 1, 5,
       effects={"spell_power_from_spirit_pct": 0.04,
                "ability_priest_mind_flay_damage": 0.01,
                "ability_priest_mind_blast_damage": 0.01},
       connected_to=["misery"],
       source="WotLK row 5, built verbatim with both halves: 'Increases "
              "your spell power by 4%-20% of your total Spirit, and your "
              "damage done by your Mind Flay and Mind Blast is increased by "
              "1%-5%.' A REAL stat conversion - spell_power is a valid "
              "target and spirit a valid source - and THE UNIT IS A RAW "
              "MULTIPLIER (character.py:1551: `gained = source * pct`), so "
              "0.04 per rank reaches the real 20%. This is the payoff for "
              "Improved Spirit Tap at tier 0. The outgoing version granted "
              "FLAT spell_power and FLAT spirit, which is neither clause.")

# ----------------------------------------------------------------- tier 6
T.node("dispersion", "Dispersion",
       "While badly wounded, you disperse into Shadow, taking 25% less "
       "damage.",
       6, -1, 1,
       effects={"low_health_damage_reduction_pct": 0.25},
       connected_to=["vampiric_touch"],
       source="WotLK row 10: 'You disperse into pure Shadow energy, "
              "reducing all damage taken by 90%. You are unable to attack "
              "or cast spells, but you regenerate 6% mana every second for "
              "6 sec.' DEPARTURE - there is no ability to unlock and no way "
              "to forbid acting. Delivered as mitigation conditioned on "
              "being in trouble, which is when the real spell is used. "
              "low_health_damage_reduction_pct reads the ACTOR's own health "
              "and defaults to a 50% threshold, so "
              "low_health_threshold_pct is NOT authored. The real talent "
              "requires Vampiric Touch, reproduced. The outgoing version "
              "was a proc on Fade's duration.")

T.node("mind_sear", "Mind Sear",
       "Teaches Mind Sear, searing the minds of everything around your "
       "target.",
       6, 1, 1, node_type="active",
       effects={"unlock_ability": "priest_mind_sear"},
       connected_to=["twisted_faith"],
       source="Kept - the ONLY unlock for priest_mind_sear, which is "
              "requires_talent. Mind Sear is a trained spell in real "
              "3.3.5a rather than a talent, so this node is a Frontier "
              "addition; it stays because dropping it would strand the "
              "ability, and a second tier-6 node also gives the capstone "
              "row a choice rather than a single forced point.")


def main():
    return T.write(was="23 nodes, 70 points - 7 proc, 6 ability-scoped, "
                       "3 flat stat, 5 unlock, 3 mixed")


if __name__ == "__main__":
    sys.exit(main())
