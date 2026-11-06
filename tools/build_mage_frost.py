#!/usr/bin/env python3
"""Rebuild Mage Frost, preserving Kyle's Cryotherapist healing branch.

    PYTHONPATH=. python3 tools/build_mage_frost.py

SOURCE: data/reference/wotlk/mage.json (from Spell.dbc), plus Kyle's
homebrew Cryotherapist branch, which is NOT from WotLK and is preserved
exactly.

KYLE, 5 Nov 2026: "The frost mage has HOME BREW cryotherapist healing
talents." This was already the BEST-SHAPED tree in the project - 8 of 32
nodes carried no proc and no unlock, against a project median far worse -
and the Cryotherapist is the most complete homebrew system in the game.
So this rebuild is conservative by design: the healing branch is untouched
and the real WotLK Frost talents are corrected around it.

THE CRYOTHERAPIST, VERIFIED BEFORE BEING TOUCHED. Nine nodes on their own
column at hex_x 5-7, chained tier 0 to tier 6, with their own icon art:

    Cryobolt / Cryolance (t0)  ->  Spirit Frost (t1)
      ->  Cryotherapy (t2)  ->  Cryotherapist (t3)
      ->  Frozen Light / Lesser Frozen Light (t4)
      ->  Icy Penance (t5)  ->  Frostfall (t6)

13 points. Every trigger and key was measured live: cryo_convert_frostbolt
and cryo_convert_ice_lance turn the mage's nukes into smart-heals
(character.py:1928), on_heal_cast and on_damage_cast are real triggers,
smart_heal is a real payload, and healing_done_pct inside a status effect
is read at abilities.py:1661. Nothing here is changed - same ids
(mage_cryotherapist_*, hence raw_id), effects, procs, values, tiers,
column, links and icon_ids.

TWO OF ITS NODES CARRY MANDATORY UNLOCKS: mage_icy_penance and
mage_frostfall are requires_talent and unlocked only from this branch, so
it cannot be dropped even if someone wanted to.

CAST TIMES: Improved Frostbolt, Icy Veins' pushback clause, Brain Freeze
and Empowered Frostbolt's cast-time clause all depend on a system that
does not exist. Each pays out as throughput.

FREEZING IS THE OTHER WALL. Frost's identity in WotLK is Chill and Frozen
effects - Frostbite, Shatter, Fingers of Frost, Deep Freeze and Improved
Blizzard all read whether the target is frozen, and NOTHING in this engine
reads a debuff on the target. Each becomes an unconditional version at a
smaller number, recorded per node.

ABILITIES THE REAL TREE WANTS AND WE LACK: Frostfire Bolt, Deep Freeze,
Summon Water Elemental, Ice Block, Frost Armor/Ice Armor as distinct
spells. Summon Water Elemental and Enduring Winter are DROPPED - there is
no water elemental and no pet for this class.

UNIT CONVENTIONS: crit_chance_spell / hit_rating / haste are PERCENTAGE
POINTS; frost_spell_damage / spell_damage_taken_pct / healing_done /
crit_damage_spell are FRACTIONS; frost_spell_damage is built by f-string
(abilities.py:1371) so grep cannot see it and it is LIVE - the family that
caused arcane_spell_damage to be wrongly declared dead here.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

#: The Cryotherapist column lives here, away from the Frost body.
CRYO_X = 6

T = Tree("mage_frost", "Mage Frost",
         "Ice and control - and, for those who learn it, the Light held in "
         "frozen form.")

# =====================================================================
# THE FROST BODY - real 3.3.5a Frost
# =====================================================================

# ----------------------------------------------------------------- tier 0
T.node("frostbite", "Frostbite",
       "Your Frost spells have a 5% chance per rank to freeze the target "
       "for 2 turns.",
       0, -5, 3,
       proc={"trigger": "on_damage_cast", "chance": 5, "icd": 1,
             "apply_effect": {"effect_id": "frostbite", "name": "Frostbite",
                              "effect_type": "debuff", "duration": 2,
                              "is_stun": True}},
       source="WotLK row 0: 'Gives your Chill effects a 5%/10%/15% chance "
              "to freeze the target for 5 sec.' Built as a real stun - "
              "is_stun is this engine's only incapacitate and is exactly "
              "what 'freeze the target' means. DEPARTURE on the source: "
              "there are no Chill effects to attach to, so it fires on any "
              "Frost damage cast. icd 1 holds it to once a turn. The "
              "outgoing node had an EMPTY effects dict and no proc - it did "
              "nothing for 3 points.")

T.node("improved_frostbolt", "Improved Frostbolt",
       "Increases the damage of your Frostbolt by 3% per rank and its "
       "critical chance by 1% per rank.",
       0, -3, 5,
       effects={"ability_mage_frostbolt_damage": 0.03,
                "ability_mage_frostbolt_crit": 1.0},
       source="WotLK row 0: 'Reduces the casting time of your Frostbolt "
              "spell by 0.1-0.5 sec.' DEPARTURE - no cast times. A shorter "
              "cast is more throughput, so it is delivered as damage plus a "
              "little crit. Kept from the outgoing tree at the same "
              "values.")

T.node("ice_floes", "Ice Floes",
       "Reduces the cooldown of your Frost Nova, Cone of Cold and Icy Veins "
       "by 1 turn per rank.",
       0, -1, 3,
       effects={"ability_mage_frost_nova_cooldown": 1,
                "ability_mage_cone_of_cold_cooldown": 1,
                "ability_mage_icy_veins_cooldown": 1},
       source="WotLK row 0, NEW to our tree: 'Reduces the cooldown of your "
              "Frost Nova, Cone of Cold, Ice Block and Icy Veins spells by "
              "7%/13%/20%.' Ice Block does not exist; the other three do. "
              "Authored as FLAT turns rather than the real percentage "
              "because _cooldown_pct would compound awkwardly across three "
              "different cooldowns. talented_cooldown clamps at 1 turn.")

# ----------------------------------------------------------------- tier 1
T.node("ice_shards", "Ice Shards",
       "Increases the critical damage of your spells by 20% per rank.",
       1, -7, 3, effects={"crit_damage_spell": 0.20},
       connected_to=["frostbite"],
       source="WotLK row 1: 'Increases the critical strike damage bonus of "
              "your Frost spells by 33%/66%/100%.' Built as school-wide "
              "spell crit damage - crit_damage_spell is a FRACTION, read at "
              "abilities.py:1460 inside a ternary (so the probe finds no "
              "literal read site and it is nonetheless live), and it cannot "
              "be scoped to one school. NOTE it is DEAD inside a status "
              "effect; only the talent-effect form works, which is what "
              "this is. The outgoing node had an EMPTY effects dict.")

T.node("piercing_ice", "Piercing Ice",
       "Increases your Frost spell damage by 2% per rank.",
       1, -5, 3, effects={"frost_spell_damage": 0.02},
       connected_to=["frostbite"],
       source="WotLK row 1: 'Increases the damage done by your Frost spells "
              "by 2%/4%/6%.' USES THE PER-SCHOOL KEY DELIBERATELY. "
              "frost_spell_damage is built as f'{school}_spell_damage' at "
              "abilities.py:1371, so a literal grep cannot see it - the "
              "exact family that caused arcane_spell_damage to be WRONGLY "
              "declared dead in this project, published in a commit and a "
              "doc before correction. It is LIVE and it is the right key "
              "for a school-scoped talent. The outgoing version used the "
              "school-agnostic spell_damage, which also lifted the mage's "
              "Fire and Arcane damage.")

T.node("frost_warding", "Frost Warding",
       "Increases the absorption of your Ice Barrier by 15% per rank.",
       1, -3, 2,
       effects={"ability_mage_ice_barrier_potency": 0.15},
       connected_to=["improved_frostbolt"],
       source="WotLK row 1: 'Increases the armor and resistances given by "
              "your Frost Armor and Ice Armor spells by 25%/50%.' DEPARTURE "
              "- neither Armor spell exists as a distinct Frost spell "
              "(mage_armor is generic). Ice Barrier is this tree's real "
              "protective spell, so the potency lands there. Kept from the "
              "outgoing tree.")

T.node("icy_veins", "Icy Veins",
       "Teaches Icy Veins, hastening your casting.",
       1, -1, 1, node_type="active",
       effects={"unlock_ability": "mage_icy_veins"},
       connected_to=["improved_frostbolt"],
       source="WotLK row 1, kept - the ONLY unlock for mage_icy_veins, "
              "which is requires_talent. Its pushback-reduction clause has "
              "nothing to act on.")

T.node("precision", "Elemental Precision",
       "Increases your chance to hit by 1% per rank and reduces your spell "
       "costs by 2% per rank.",
       1, 1, 3,
       effects={"hit_rating": 1.0, "all_ability_cost_pct": 0.02},
       connected_to=["ice_floes"],
       source="WotLK row 1 ('Precision'): 'Reduces the mana cost and "
              "increases your chance to hit with spells by 1%/2%/3%.' Built "
              "with BOTH halves, where the outgoing version had hit_rating "
              "alone. The display name keeps the outgoing tree's 'Elemental "
              "Precision' so nothing referring to it by name breaks. "
              "all_ability_cost_pct is a FRACTION where POSITIVE IS A "
              "REDUCTION and FLIPS to points inside a status effect.")

T.node("permafrost", "Permafrost",
       "Increases the duration of your Blizzard and Frost Nova by 1 turn "
       "per rank.",
       1, 3, 3,
       effects={"ability_mage_blizzard_duration": 1,
                "ability_mage_frost_nova_duration": 1},
       connected_to=["ice_floes"],
       source="WotLK row 1: 'Increases the duration of your Chill effects "
              "by 1-3 secs, reduces the target's speed by an additional "
              "4%-10%.' DEPARTURE - there are no Chill effects and no "
              "movement speed. Delivered as duration on the tree's two "
              "control spells, which is the nearest real reading. "
              "ability_<id>_duration is FLAT turns and POSITIVE EXTENDS. "
              "Kept from the outgoing tree.")

# ----------------------------------------------------------------- tier 2
T.node("arctic_reach", "Arctic Reach",
       "Increases the damage of your Ice Lance and Blizzard by 8% per rank.",
       2, -7, 2,
       effects={"ability_mage_ice_lance_damage": 0.08,
                "ability_mage_blizzard_damage": 0.08},
       connected_to=["ice_shards"],
       source="WotLK row 2: 'Increases the range of your Frostbolt, Ice "
              "Lance, Deep Freeze and Blizzard spells.' DEPARTURE - there "
              "is no range. A longer reach is more casts landed, so it is "
              "delivered as damage on the two of the four that are not "
              "already covered by Improved Frostbolt. The outgoing version "
              "granted flat frost_spell_power, which is Piercing Ice's "
              "territory.")

T.node("frost_channeling", "Frost Channeling",
       "Reduces the cost of your spells by 3% per rank and the threat they "
       "generate by 3% per rank.",
       2, -5, 3,
       effects={"all_ability_cost_pct": 0.03,
                "threat_generation_pct": -0.03},
       connected_to=["piercing_ice"],
       source="WotLK row 2, built verbatim with both halves: 'Reduces the "
              "mana cost of all spells by 4%/7%/10% and reduces the threat "
              "caused by your Frost spells by 4%/7%/10%.' There is no "
              "per-school threat key, only the global "
              "threat_generation_pct, which is a FRACTION. Stacks with "
              "Elemental Precision on cost. The outgoing version was flat "
              "per-ability cost cuts.")

T.node("cold_snap", "Cold Snap",
       "Teaches Cold Snap, finishing the cooldown on your Frost spells.",
       2, -3, 1, node_type="active",
       effects={"unlock_ability": "mage_cold_snap"},
       connected_to=["frost_warding"],
       source="WotLK row 2, kept - the ONLY unlock for mage_cold_snap, "
              "which is requires_talent. It is Ice Barrier's and Cold as "
              "Ice's prerequisite in the real tree, both preserved below.")

T.node("shatter", "Shatter",
       "Increases your spell critical chance by 2% per rank.",
       2, -1, 3, effects={"crit_chance_spell": 2.0},
       connected_to=["icy_veins"],
       source="WotLK row 2: 'Increases the critical strike chance of all "
              "your spells against frozen targets by 17%/34%/50%.' "
              "DEPARTURE - NOTHING in this engine reads a debuff on the "
              "target, so 'against frozen targets' cannot be checked. "
              "Delivered unconditionally at a far smaller value, since it "
              "is now always on rather than situational. Frost's whole "
              "frozen-target identity runs into this wall - see also "
              "Fingers of Frost and Deep Freeze. The outgoing node had an "
              "EMPTY effects dict.")

T.node("improved_cone_of_cold", "Improved Cone of Cold",
       "Increases the damage of your Cone of Cold by 12% per rank.",
       2, 1, 3,
       effects={"ability_mage_cone_of_cold_damage": 0.12},
       connected_to=["precision"],
       source="WotLK row 2, NEW to our tree, built verbatim: 'Increases the "
              "damage dealt by your Cone of Cold spell by 15%/25%/35%.' 12% "
              "per rank reaches 36%, the nearest whole percent per rank.")

T.node("frozen_core", "Frozen Core",
       "Reduces spell damage taken by 2% per rank.",
       2, 3, 3, effects={"spell_damage_taken_pct": -0.02},
       connected_to=["permafrost"],
       source="WotLK row 2, built verbatim: 'Reduces the damage taken from "
              "all spells by 2%/4%/6%.' spell_damage_taken_pct is a "
              "FRACTION as a talent effect and NEGATIVE reduces. The "
              "outgoing version used low_health_damage_reduction_pct AND "
              "low_health_threshold_pct, which is a different talent "
              "entirely (Fiery Payback, in Fire) and put this class one "
              "node from a summing-threshold breach.")

# ----------------------------------------------------------------- tier 3
T.node("cold_as_ice", "Cold as Ice",
       "Reduces the cooldown of your Cold Snap and Ice Barrier by 1 turn "
       "per rank.",
       3, -3, 2,
       effects={"ability_mage_cold_snap_cooldown": 1,
                "ability_mage_ice_barrier_cooldown": 1},
       connected_to=["cold_snap"],
       source="WotLK row 3, NEW to our tree: 'Reduces the cooldown of your "
              "Cold Snap, Ice Barrier and Summon Water Elemental spells by "
              "10%/20%.' Summon Water Elemental does not exist. The real "
              "talent requires Cold Snap, which connected_to reproduces.")

T.node("winters_chill", "Winter's Chill",
       "Increases the critical chance of your Frostbolt by 1% per rank and "
       "your Frost spell damage by 1% per rank.",
       3, -1, 5,
       effects={"ability_mage_frostbolt_crit": 1.0,
                "frost_spell_damage": 0.01},
       connected_to=["shatter"],
       source="WotLK row 3: 'Increases your chance to critically hit with "
              "Frostbolt by an additional 1%/2%/3% and gives your Frost "
              "damage spells a chance to apply the Winter's Chill effect, "
              "increasing the chance of a critical strike against the "
              "target.' The self-crit half is built; the target-debuff half "
              "needs something to read a debuff on the target, which does "
              "not exist, so a small Frost damage bonus stands in. The "
              "outgoing version was flat spell_damage.")

# ----------------------------------------------------------------- tier 4
T.node("shattered_barrier", "Shattered Barrier",
       "Your Ice Barrier has a 50% chance per rank to freeze nearby "
       "enemies for 1 turn.",
       4, -5, 2,
       proc={"trigger": "on_cast", "chance": 50, "icd": 0,
             "ability_filter": ["mage_ice_barrier"],
             "apply_effect": {"effect_id": "shattered_barrier",
                              "name": "Shattered Barrier",
                              "effect_type": "debuff", "duration": 1,
                              "is_stun": True}},
       connected_to=["cold_as_ice"],
       source="WotLK row 4, NEW to our tree: 'Gives your Ice Barrier spell "
              "a 50%/100% chance to freeze all enemies within 10 yds for 8 "
              "sec when it is destroyed.' DEPARTURE on the trigger - there "
              "is no event for an absorb shield being CONSUMED or an effect "
              "EXPIRING, so it fires when the barrier is CAST instead. A "
              "1-turn stun rather than 8 seconds, because a stun that lands "
              "on cast rather than on break is far easier to arrange. The "
              "real talent requires Ice Barrier, which connected_to "
              "reproduces.")

T.node("ice_barrier", "Ice Barrier",
       "Teaches Ice Barrier, shielding you in ice.",
       4, -3, 1, node_type="active",
       effects={"unlock_ability": "mage_ice_barrier"},
       connected_to=["cold_snap"],
       source="WotLK row 4, kept - the ONLY unlock for mage_ice_barrier, "
              "which is requires_talent. The real talent requires Cold "
              "Snap, which connected_to reproduces.")

T.node("empowered_frostbolt", "Empowered Frostbolt",
       "Increases the damage of your Frostbolt by 5% per rank and its "
       "critical chance by 2% per rank.",
       4, -1, 2,
       effects={"ability_mage_frostbolt_damage": 0.05,
                "ability_mage_frostbolt_crit": 2.0},
       connected_to=["winters_chill"],
       source="WotLK row 4: 'Increases the damage of your Frostbolt spell "
              "by an amount equal to 5%/10% of your spell power and reduces "
              "its cast time.' Spell-power coefficients are not exposed to "
              "talents and there are no cast times, so it is direct damage "
              "plus crit. Kept from the outgoing tree, which ALSO carried "
              "frost_spell_power=40 inside a proc's stat_mods - verified "
              "live as readable, so that was not the dead-key problem, but "
              "it is dropped here as duplicating Piercing Ice.")

T.node("arctic_winds", "Arctic Winds",
       "Increases your Frost spell damage by 1% per rank.",
       4, 1, 5, effects={"frost_spell_damage": 0.01},
       connected_to=["winters_chill"],
       source="WotLK row 4: 'Increases all Frost damage you cause by 1%-5% "
              "and reduces the chance melee and ranged attacks will hit "
              "you.' The damage half is built verbatim with the per-school "
              "key. There is no caster-side miss chance for INCOMING "
              "attacks - hit_chance_spell is a dead talent key, set once in "
              "Character.__init__. The outgoing node had an EMPTY effects "
              "dict.")

T.node("fingers_of_frost", "Fingers of Frost",
       "Your Frost spells have a 7% chance per rank to grant a guaranteed "
       "critical strike window.",
       4, 3, 2,
       proc={"trigger": "on_damage_cast", "chance": 7, "icd": 0,
             "apply_effect": {"effect_id": "fingers_of_frost",
                              "name": "Fingers of Frost",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"crit_chance_spell": 50},
                              "on_target": False}},
       connected_to=["arctic_winds"],
       source="WotLK row 4: 'Gives your Chill effects a 7%/15% chance to "
              "grant you the Fingers of Frost effect, which treats your "
              "next 2 spells as if the target were frozen.' DEPARTURE - "
              "nothing reads whether a target is frozen, so 'as if frozen' "
              "has no referent. What being frozen BUYS in the real game is "
              "Shatter's enormous crit bonus, so this grants crit chance "
              "directly - which is the same payoff by the only route the "
              "engine has. 'Next 2 spells' becomes a 2-turn window. The "
              "outgoing node had an EMPTY effects dict.")

# ----------------------------------------------------------------- tier 5
T.node("brain_freeze", "Brain Freeze",
       "Your Frost spells have a 5% chance per rank to make your next "
       "spells cheaper and sharper for 2 turns.",
       5, -3, 3,
       proc={"trigger": "on_damage_cast", "chance": 5, "icd": 0,
             "apply_effect": {"effect_id": "brain_freeze",
                              "name": "Brain Freeze",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"all_ability_cost_pct": 100.0,
                                            "crit_chance_spell": 10},
                              "on_target": False}},
       connected_to=["shattered_barrier"],
       source="WotLK row 5: 'Your Frost damage spells with chilling effects "
              "have a 5%/10%/15% chance to cause your next Fireball or "
              "Frostfire Bolt spell to be instant cast and cost no mana.' "
              "DEPARTURE - no cast times and no Frostfire Bolt. The "
              "'cost no mana' clause IS buildable and is the real payoff, "
              "so all_ability_cost_pct 100 inside the status effect makes "
              "the window free. MIND THE FLIP: that key is PERCENTAGE "
              "POINTS inside a status effect and a FRACTION as a talent "
              "effect. The outgoing node had an EMPTY effects dict.")

T.node("chilled_to_the_bone", "Chilled to the Bone",
       "Increases the damage of your Frostbolt and Ice Lance by 1% per rank.",
       5, -1, 5,
       effects={"ability_mage_frostbolt_damage": 0.01,
                "ability_mage_ice_lance_damage": 0.01},
       connected_to=["empowered_frostbolt"],
       source="WotLK row 5: 'Increases the damage caused by your Frostbolt, "
              "Frostfire Bolt and Ice Lance spells by 1%-5% and reduces the "
              "movement speed of all chilled targets.' Frostfire Bolt does "
              "not exist and there is no movement speed. The outgoing "
              "version was flat spell_damage.")

T.node("deep_freeze", "Deep Freeze",
       "Your Frost spells have a 5% chance per rank to stun the target.",
       5, 1, 3,
       proc={"trigger": "on_damage_cast", "chance": 5, "icd": 2,
             "apply_effect": {"effect_id": "deep_freeze",
                              "name": "Deep Freeze",
                              "effect_type": "debuff", "duration": 2,
                              "is_stun": True}},
       connected_to=["fingers_of_frost"],
       source="WotLK row 10 in the real tree, moved here: 'Stuns the target "
              "for 5 sec. Only usable on Frozen targets.' DEPARTURE - there "
              "is no mage_deep_freeze ability to unlock, and 'only usable "
              "on Frozen targets' cannot be checked. Delivered as a chance "
              "to stun off any Frost cast, with icd 2 so it is not "
              "permanent control. It sits at tier 5 rather than 6 because "
              "the capstone row belongs to the Cryotherapist's Frostfall. "
              "The outgoing node had an EMPTY effects dict.")

# =====================================================================
# KYLE'S HOMEBREW CRYOTHERAPIST BRANCH - preserved exactly, not WotLK
#
# Same ids (mage_cryotherapist_*, hence raw_id), effects, procs, values,
# tiers, column at hex_x 5-7, links and icon_ids. Two of its nodes carry
# MANDATORY unlocks for mage_icy_penance and mage_frostfall.
# =====================================================================
_HB = ("KYLE'S HOMEBREW CRYOTHERAPIST, preserved exactly through the Frost "
       "rebuild of 5 Nov 2026 - same talent_id, effects, proc, values, "
       "tier, column, links and icon_id. NOT a WotLK talent. The whole "
       "branch was verified live before anything was touched: "
       "cryo_convert_frostbolt and cryo_convert_ice_lance are read at "
       "character.py:1928 and turn the mage's nukes into smart-heals; "
       "on_heal_cast and on_damage_cast are real triggers; smart_heal is a "
       "real payload; healing_done_pct inside a status effect is read at "
       "abilities.py:1661. ")

T.node("mage_cryotherapist_cryobolt", "Cryobolt",
       "Your Frostbolt also heals your neediest ally for part of the damage "
       "it deals.",
       0, CRYO_X - 1, 1, raw_id=True,
       effects={"cryo_convert_frostbolt": 1},
       raw_links=["mage_cryotherapist_spirit_frost"],
       icon_id="mage_cryotherapist_cryobolt",
       source=_HB + "This is the entry point of the healing branch and the "
                    "reason the Cryotherapist works at all.")

T.node("mage_cryotherapist_cryolance", "Cryolance",
       "Your Ice Lance also heals your neediest ally for part of the damage "
       "it deals.",
       0, CRYO_X + 1, 1, raw_id=True,
       effects={"cryo_convert_ice_lance": 1},
       raw_links=["mage_cryotherapist_spirit_frost"],
       icon_id="mage_cryotherapist_cryolance",
       source=_HB + "The second entry point; both feed Spirit Frost.")

T.node("mage_cryotherapist_spirit_frost", "Spirit Frost",
       "Every heal you cast returns 40 Mana.",
       1, CRYO_X, 1, raw_id=True,
       proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 40}},
       raw_links=["mage_cryotherapist_cryotherapy"],
       icon_id="mage_cryotherapist_spirit_frost",
       source=_HB + "Its effects dict is empty and all its work is in the "
                    "proc, which is legitimate.")

T.node("mage_cryotherapist_cryotherapy", "Cryotherapy",
       "Increases your healing by 5% per rank. Your heals also have a 33% "
       "chance per rank to spill over, healing your neediest ally for a "
       "further 60.",
       2, CRYO_X, 3, raw_id=True,
       effects={"healing_done": 0.05},
       proc={"trigger": "on_heal_cast", "chance": 33, "icd": 0,
             "smart_heal": 60},
       raw_links=["mage_cryotherapist_keystone"],
       icon_id="mage_cryotherapist_cryotherapy",
       source=_HB + "Carries BOTH effects and a proc, which the engine "
                    "supports and which this node is the clearest example "
                    "of in the project.")

T.node("mage_cryotherapist_keystone", "Cryotherapist",
       "Increases your healing by 10%. Your damaging spells now mend as "
       "they wound, healing your neediest ally for 50.",
       3, CRYO_X, 1, raw_id=True,
       effects={"healing_done": 0.1},
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 2,
             "smart_heal": 50},
       raw_links=["mage_cryotherapist_frozen_light",
                  "mage_cryotherapist_lesser_frozen_light"],
       icon_id="mage_cryotherapist_keystone",
       source=_HB + "The branch's keystone - the node that turns a Frost "
                    "mage into a healer rather than a mage who sometimes "
                    "heals.")

T.node("mage_cryotherapist_frozen_light", "Frozen Light",
       "Casting a heal wreathes you in Frozen Light for 3 turns, increasing "
       "your healing done by 30%.",
       4, CRYO_X - 1, 1, raw_id=True,
       proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
             "apply_effect": {"effect_id": "frozen_light_buff",
                              "name": "Frozen Light",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"healing_done_pct": 30},
                              "on_target": False}},
       raw_links=["mage_cryotherapist_icy_penance"],
       icon_id="mage_cryotherapist_frozen_light",
       source=_HB + "healing_done_pct inside a status effect is the "
                    "status-channel healing key, read at "
                    "abilities.py:1661 in PERCENTAGE POINTS - correct "
                    "here, and NOT the same as healing_done, which is "
                    "talent-channel only and would be dead in this "
                    "position.")

T.node("mage_cryotherapist_lesser_frozen_light", "Lesser Frozen Light",
       "Your heals have a 33% chance per rank to grant Lesser Frozen Light "
       "for 2 turns, increasing your healing done by 10%.",
       4, CRYO_X + 1, 3, raw_id=True,
       proc={"trigger": "on_heal_cast", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "lesser_frozen_light_buff",
                              "name": "Lesser Frozen Light",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"healing_done_pct": 10},
                              "on_target": False}},
       raw_links=["mage_cryotherapist_icy_penance"],
       icon_id="mage_cryotherapist_lesser_frozen_light",
       source=_HB + "The multi-rank sibling of Frozen Light, ranked by "
                    "chance - which is the only thing a talent proc can "
                    "scale with points.")

T.node("mage_cryotherapist_icy_penance", "Icy Penance",
       "Teaches Icy Penance, striking an enemy with frozen light while "
       "smart-healing your neediest allies.",
       5, CRYO_X, 1, raw_id=True, node_type="active",
       effects={"unlock_ability": "mage_icy_penance"},
       raw_links=["mage_cryotherapist_frostfall"],
       icon_id="mage_cryotherapist_icy_penance",
       source=_HB + "MANDATORY: the ONLY unlock for mage_icy_penance, "
                    "which is requires_talent.")

T.node("mage_cryotherapist_frostfall", "Frostfall",
       "Teaches Frostfall, calling icy stars that damage every enemy and "
       "heal your whole party.",
       6, CRYO_X, 1, raw_id=True, node_type="active",
       effects={"unlock_ability": "mage_frostfall"},
       icon_id="mage_cryotherapist_frostfall",
       source=_HB + "MANDATORY: the ONLY unlock for mage_frostfall, which "
                    "is requires_talent. It is the branch's capstone and "
                    "the tree's tier-6 node, which is why the real Frost "
                    "capstone Deep Freeze sits at tier 5.")

# The Blizzard unlock belongs to the Frost body but is placed last so the
# Cryotherapist column reads as one block above.
T.node("blizzard", "Blizzard",
       "Teaches Blizzard, pelting an area with ice over several turns.",
       2, -9, 1, node_type="active",
       effects={"unlock_ability": "mage_blizzard"},
       connected_to=["ice_shards"],
       source="Kept - the ONLY unlock for mage_blizzard, which is "
              "requires_talent. Blizzard is a TRAINED spell in real "
              "3.3.5a rather than a talent, so this node is a Frontier "
              "addition; it stays because dropping it would strand the "
              "ability. Improved Blizzard IS a real Frost talent (row 1) "
              "but adds a Chill effect, which does not exist, so it is not "
              "built.")


def main():
    return T.write(was="32 nodes, 83 points - 11 proc, 11 homebrew cryo, "
                       "8 with no proc and no unlock (the BEST-shaped tree "
                       "in the project before this)")


if __name__ == "__main__":
    sys.exit(main())
