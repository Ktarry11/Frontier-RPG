#!/usr/bin/env python3
"""Rebuild Rogue Subtlety from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_rogue_subtlety.py

SOURCE: data/reference/wotlk/rogue.json, extracted from the game's own
Spell.dbc (see tools/build_wotlk_reference.py for provenance and the
cross-check). Worksheet: data/reference/wotlk_worksheets/rogue.md.

WHY THIS TREE FIRST. It was the worst in the project - 17 of 23 nodes were
pure scalars, "20 scalar" in the survey, a stat stick wearing Subtlety's
names. Mage Frost, the best tree in the game, is 8 of 32.

ROLE: melee burst from concealment. Builders into finishers, with the
tree's own identity being the opener (Ambush/Garrote/Cheap Shot) and the
Backstab that follows.

COMBO POINTS EXIST NOW, which is why this tree is buildable at all. Seven
of Subtlety's 28 real talents are written in terms of them and the Rogue
had none until 5 Nov 2026 (see tools/wire_rogue_combo_points.py). Four of
those seven - Relentless Strikes, Setup, Initiative, Premeditation - are
rebuilt here as real combo mechanics rather than substitutes.

UNIT CONVENTIONS USED HERE, every one verified with
tools/probe_talent_key.py rather than inferred from the name:

    ability_<id>_cost            FLAT resource
    ability_<id>_cost_pct        FRACTION, POSITIVE IS A REDUCTION
    ability_<id>_cooldown        FLAT turns
    ability_<id>_crit            PERCENTAGE POINTS
    ability_<id>_damage          FRACTION
    armor_penetration_pct        PERCENTAGE POINTS - lands on the attribute
                                 divided by 100, so 3.0 means 3%. Probed;
                                 authoring 0.03 here would have shipped
                                 0.03%.
    crit_taken_reduction         PERCENTAGE POINTS
    attack_power_pct             PERCENTAGE POINTS
    agility_pct                  PERCENTAGE POINTS
    all_damage                   FRACTION
    magic_damage_taken_pct       FRACTION as a talent effect, and NEGATIVE
                                 reduces damage taken
    low_health_damage_pct        FRACTION, reads the TARGET's health

TWO THINGS ABOUT RANKS AND PROCS, which shape half the designs below:

  - `effects` are authored PER RANK and scaled by points_spent.
  - a proc's `chance` is ALSO scaled by points_spent (character.py, in
    _sync_talent_procs, capped at 100) but its PAYLOAD IS NOT. So a
    multi-rank proc scales by growing its chance, not its effect. That is
    the project's existing idiom (Retort: "3% chance per rank") and it is
    why Master of Subtlety below is 33/66/100% chance of a fixed buff
    rather than a 4/7/10% buff at a fixed chance.

NEITHER low_health THRESHOLD IS AUTHORED, deliberately.
low_health_threshold_pct is UNSCALED and SUMS across talents (one node per
CLASS - tools/qa_summing_thresholds.py enforces it), and it is SHARED by
two different conditionals: low_health_damage_pct reads the TARGET's health
and defaults to 0.35, low_health_damage_reduction_pct reads the ACTOR's own
and defaults to 0.5. Dirty Deeds wants exactly 35% on the target and Cheat
Death wants the actor's own, so authoring the shared key on either would
corrupt the other. Both defaults are already correct, so the key is left
off both nodes. The outgoing tree authored it on Cheat Death, which is why
Cheat Death was firing at 35% instead of 50%.

WHAT IS NOT BUILDABLE, and what each became instead. Five of Subtlety's
real talents are stealth talents and this engine has no stealth - no
stealth state, no detection, no break-stealth event:

    Master of Deception   stealth detection -> the openers hit harder
    Camouflage            stealth cooldown  -> Vanish/Sprint come back sooner
    Heightened Senses     stealth detection -> less magic damage taken
    Master of Subtlety    post-stealth window -> an opener grants the window
    Shadow Dance          stealth on demand -> left as its unlock, the
                          ability itself already models it

Three more wanted mechanics the engine lacks:

    Enveloping Shadows    there is NO aoe_damage_taken_pct key anywhere -
                          probed and confirmed dead - so this becomes raw
                          dodge instead of AoE-specific mitigation
    Ghostly Strike        a separate button we have no ability for, so it
                          is delivered as a rider on the builders
    Shadowstep            likewise no ability, and the engine has no
                          positioning; delivered off Sprint, which is the
                          closest thing to stepping through shadows
    Premeditation         no ability, so "adds 2 combo points" is delivered
                          off Vanish - you surface with the points, which
                          is what the real talent is for

Dropped: Sanguinary Vein. It is a CATACLYSM talent, not WotLK Subtlety,
and it was the only node in the outgoing tree with no counterpart in the
real data.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/rogue_subtlety.json"

#: The six combo-point finishers, for Relentless Strikes' filter.
FINISHERS = ["rogue_eviscerate", "rogue_rupture", "rogue_slice_and_dice",
             "rogue_expose_armor", "rogue_kidney_shot", "rogue_envenom"]

#: The three openers. Subtlety's whole identity sits on these.
OPENERS = ["rogue_ambush", "rogue_garrote", "rogue_cheap_shot"]

TREE = {
    "spec_name": "Rogue Subtlety",
    "tree_id": "rogue_subtlety",
    "description": ("Shadow specialist striking from concealment for "
                    "massive burst."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(talent_id, name, description, tier, hex_x, max_points,
         effects=None, proc=None, connected_to=None, node_type="passive",
         source=""):
    TREE["nodes"].append({
        "talent_id": f"rogue_subtlety_{talent_id}",
        "name": name,
        "description": description,
        "node_type": node_type,
        "tier": tier,
        "max_points": max_points,
        "cost_per_point": 1,
        "hex_x": hex_x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "_source": source,
        "connected_to": [f"rogue_subtlety_{c}" for c in (connected_to or [])],
        **({"proc": proc} if proc else {}),
    })


# ----------------------------------------------------------------- tier 0
node("relentless_strikes", "Relentless Strikes",
     "Your finishing moves have a 20% chance per rank to restore 25 "
     "Energy.",
     0, -2, 5,
     proc={"trigger": "on_cast", "chance": 20, "icd": 0,
           "ability_filter": FINISHERS,
           "grant_resource": {"resource": "energy", "amount": 25}},
     source="WotLK row 0: 'Your finishing moves have a 4% chance per combo "
            "point to restore 25 energy.' Built faithfully now that the "
            "Rogue has combo points. Per-combo-point chance is not "
            "expressible - nothing reads a live resource amount - so the "
            "chance is per RANK instead, reaching 100% at 5 points exactly "
            "as the real talent does at 5 combo points. ability_filter "
            "restricts it to the six real finishers; the energy amount is "
            "the real 25. A proc's chance scales with points_spent, its "
            "payload does not, which is why chance carries the rank curve.")

node("master_of_deception", "Master of Deception",
     "Increases the damage of your Ambush, Garrote and Cheap Shot by 7% "
     "per rank.",
     0, 0, 3,
     effects={"ability_rogue_ambush_damage": 0.07,
              "ability_rogue_garrote_damage": 0.07,
              "ability_rogue_cheap_shot_damage": 0.07},
     source="WotLK row 0: 'Reduces the chance enemies have to detect you "
            "while in Stealth mode.' DEPARTURE - this engine has no stealth "
            "at all: no stealth state, no detection roll, no break event. "
            "The talent's PURPOSE is that you get to open on your terms, so "
            "it pays out on the three openers instead. The outgoing version "
            "already did this for two of them at 5 ranks; corrected to the "
            "real 3 ranks and extended to Cheap Shot.")

node("opportunity", "Opportunity",
     "Increases the damage dealt by your Backstab, Mutilate, Garrote and "
     "Ambush abilities by 10% per rank.",
     0, 2, 2,
     effects={"ability_rogue_backstab_damage": 0.10,
              "ability_rogue_mutilate_damage": 0.10,
              "ability_rogue_garrote_damage": 0.10,
              "ability_rogue_ambush_damage": 0.10},
     source="WotLK row 0, built verbatim including all four abilities and "
            "the real 10% per rank over 2 ranks. The outgoing version was "
            "5 ranks of 8% on Backstab alone.")

# ----------------------------------------------------------------- tier 1
node("sleight_of_hand", "Sleight of Hand",
     "Reduces the chance you are critically hit by 1% per rank.",
     1, -3, 2, effects={"crit_taken_reduction": 1.0},
     connected_to=["relentless_strikes"],
     source="WotLK row 1: 'Reduces the chance you are critically hit by "
            "melee and ranged attacks by 1%/2% and increases the threat "
            "reduction of your Feint ability by 10%/20%.' The crit half is "
            "exact - crit_taken_reduction is real, read at abilities.py:1317 "
            "in PERCENTAGE POINTS. The Feint-threat half is dropped: threat "
            "reduction is only expressible globally via "
            "threat_generation_pct, and there is no per-ability threat key, "
            "so scoping it to Feint is impossible. The outgoing version was "
            "flat dodge, which is a different stat entirely.")

node("elusiveness", "Elusiveness",
     "Reduces the cooldown of your Vanish and Blind by 2 turns per rank.",
     1, -1, 2,
     effects={"ability_rogue_vanish_cooldown": 2,
              "ability_rogue_blind_cooldown": 2},
     connected_to=["master_of_deception"],
     source="WotLK row 2: 'Reduces the cooldown of your Vanish and Blind "
            "abilities by 30/60 sec and your Cloak of Shadows by 15/30 "
            "sec.' Vanish and Blind are real abilities here (cd 10 and 12); "
            "Cloak of Shadows does not exist and is dropped. 30 seconds is "
            "re-derived as 2 turns per rank rather than divided by three - "
            "4 turns off a 10-turn cooldown is the same proportion the real "
            "talent gives.")

node("dirty_tricks", "Dirty Tricks",
     "Reduces the Energy cost of your Blind and Sap by 25% per rank.",
     1, 1, 2,
     effects={"ability_rogue_blind_cost_pct": 0.25,
              "ability_rogue_sap_cost_pct": 0.25},
     connected_to=["opportunity"],
     source="WotLK row 1, NEW to our tree: 'Increases the range of your "
            "Blind and Sap abilities by 2/5 yards and reduces the energy "
            "cost of your Blind and Sap abilities by 25%/50%.' The cost "
            "half is exact. Range does not exist in this engine - there is "
            "no positioning - so it is dropped. _cost_pct is a FRACTION "
            "where POSITIVE MEANS A REDUCTION.")

node("ghostly_strike", "Ghostly Strike",
     "Your Backstab and Sinister Strike leave you harder to hit, "
     "increasing dodge by 15% for 2 turns.",
     1, 3, 1,
     proc={"trigger": "on_damage_cast", "chance": 100, "icd": 3,
           "ability_filter": ["rogue_backstab", "rogue_sinister_strike"],
           "apply_effect": {"effect_id": "ghostly_strike",
                            "name": "Ghostly Strike",
                            "effect_type": "buff", "duration": 2,
                            "stat_mods": {"dodge": 15},
                            "on_target": False}},
     connected_to=["opportunity"],
     source="WotLK row 2, NEW to our tree: 'A strike that deals 125% weapon "
            "damage (180% if a dagger is equipped) and increases your "
            "chance to dodge by 15% for 7 sec. Awards 1 combo point.' "
            "DEPARTURE - there is no rogue_ghostly_strike ability to "
            "unlock, and the engine has no weapon-type key for the dagger "
            "clause. Delivered as a RIDER on the two builders it would have "
            "replaced, keeping the part that is actually distinctive: the "
            "real 15% dodge for a real 7 seconds (2 turns). icd 3 stops it "
            "being permanently up.")

node("camouflage", "Camouflage",
     "Reduces the cooldown of your Vanish and Sprint by 1 turn per rank.",
     1, 5, 3,
     effects={"ability_rogue_vanish_cooldown": 1,
              "ability_rogue_sprint_cooldown": 1},
     connected_to=["ghostly_strike"],
     source="WotLK row 1: 'Increases your speed while stealthed by 5%/15% "
            "and reduces the cooldown of your Stealth ability by 2/6 sec.' "
            "DEPARTURE - no stealth and no movement speed. Both halves are "
            "about getting back into position sooner, so it pays out on the "
            "two abilities that do that here. Stacks with Elusiveness on "
            "Vanish, as the real pair does on Stealth.")

node("serrated_blades", "Serrated Blades",
     "Your attacks ignore 3% of your target's armor per rank, and your "
     "Rupture deals 10% more damage per rank.",
     1, 7, 3,
     effects={"armor_penetration_pct": 3.0,
              "ability_rogue_rupture_damage": 0.10},
     connected_to=["camouflage"],
     source="WotLK row 2, built verbatim - both halves and both numbers are "
            "the real ones. armor_penetration_pct is authored in PERCENTAGE "
            "POINTS: probed with tools/probe_talent_key.py, which showed it "
            "landing on the attribute divided by 100, so 3.0 means 3%. "
            "Authoring 0.03 would have shipped 0.03% and looked correct in "
            "every audit. It is read by monster.py:658 via getattr on the "
            "ATTACKER, not through get_talent_effect.")

# ----------------------------------------------------------------- tier 2
node("setup", "Setup",
     "Dodging an attack has a 33% chance per rank to award you a combo "
     "point.",
     2, -3, 3,
     proc={"trigger": "on_dodge", "chance": 33, "icd": 1,
           "grant_resource": {"resource": "combo", "amount": 20}},
     connected_to=["sleight_of_hand"],
     source="WotLK row 3: 'Gives you a 33%/66%/100% chance to add a combo "
            "point to your target after dodging their attack or fully "
            "resisting one of their spells. This cannot happen more than "
            "once per second.' Built faithfully - on_dodge is a real "
            "trigger, the chance curve is exact, and icd 1 is the "
            "once-per-second clause. The resist half is dropped: there is "
            "no full-resist event. The outgoing version was a WORKING "
            "proc, not dead data - 15% per rank on_damage_taken granting "
            "10% dodge - a sensible substitute for a class that had no "
            "combo points to award. Replaced because the real mechanic is "
            "now available, not because the old one was broken.")

node("heightened_senses", "Heightened Senses",
     "Reduces magic damage taken by 2% per rank.",
     2, -1, 2, effects={"magic_damage_taken_pct": -0.02},
     connected_to=["elusiveness"],
     source="WotLK row 4: 'Increases your Stealth detection and reduces the "
            "chance you are hit by spells and ranged attacks by 2%/4%.' "
            "DEPARTURE - no stealth, and no caster-side miss chance for "
            "INCOMING attacks (hit_chance_spell is set once in "
            "Character.__init__ and is a dead talent key). Avoiding spell "
            "damage is expressed as taking less of it. "
            "magic_damage_taken_pct is a FRACTION as a talent effect and "
            "NEGATIVE reduces, the opposite sign to its meaning inside a "
            "status effect. The outgoing version was flat hit_rating, which "
            "is an OFFENSIVE stat - the talent was making the rogue hit "
            "harder, not survive better.")

node("initiative", "Initiative",
     "Your Ambush, Garrote and Cheap Shot have a 33% chance per rank to "
     "award an additional combo point.",
     2, 1, 3,
     proc={"trigger": "on_cast", "chance": 33, "icd": 0,
           "ability_filter": OPENERS,
           "grant_resource": {"resource": "combo", "amount": 20}},
     connected_to=["dirty_tricks"],
     source="WotLK row 3, built verbatim: the real ability list, the real "
            "33%-per-rank curve to 100%, and a real extra combo point. The "
            "outgoing version was a flat 4-energy cost cut on Backstab, "
            "which is not this talent in any respect.")

node("preparation", "Preparation",
     "Teaches Preparation, immediately finishing the cooldown on your "
     "Evasion, Sprint and Vanish.",
     2, 3, 1, node_type="active",
     effects={"unlock_ability": "rogue_preparation"},
     connected_to=["ghostly_strike"],
     source="WotLK row 4, kept as-is from the outgoing tree - it was "
            "already a real unlock of a real ability (rogue_preparation, "
            "effect_type reset_cooldowns). Cold Blood and Shadowstep are in "
            "the real wording; Cold Blood exists here, Shadowstep does not.")

node("improved_ambush", "Improved Ambush",
     "Increases the critical strike chance of your Ambush by 25% per rank.",
     2, 5, 2, effects={"ability_rogue_ambush_crit": 25.0},
     connected_to=["camouflage"],
     source="WotLK row 3, NEW to our tree, built verbatim at the real 25% "
            "per rank over 2 ranks. ability_<id>_crit is PERCENTAGE POINTS, "
            "read at abilities.py:1354 - a key that was authored by several "
            "talents and never read until it was fixed, so it is live now.")

node("dirty_deeds", "Dirty Deeds",
     "Reduces the Energy cost of your Cheap Shot and Garrote by 10 per "
     "rank, and your abilities deal 10% more damage per rank to targets "
     "below 35% health.",
     2, 7, 2,
     effects={"ability_rogue_cheap_shot_cost": 10,
              "ability_rogue_garrote_cost": 10,
              "low_health_damage_pct": 0.10},
     connected_to=["serrated_blades"],
     source="WotLK row 4, built verbatim - both halves, the real 10 Energy "
            "and the real 10% per rank. low_health_damage_pct reads the "
            "TARGET's health (abilities.py:1642) and DEFAULTS to a 35% "
            "threshold, which is exactly what the real talent says, so "
            "low_health_threshold_pct is deliberately NOT authored here: it "
            "is UNSCALED, SUMS across talents, and is shared with Cheat "
            "Death's actor-side conditional. See the module docstring. The "
            "outgoing version was flat damage on Cheap Shot and Kidney "
            "Shot with no conditional at all.")

node("hemorrhage", "Hemorrhage",
     "Teaches Hemorrhage, a strike that makes the target bleed and awards "
     "a combo point.",
     2, 9, 1, node_type="active",
     effects={"unlock_ability": "rogue_hemorrhage"},
     connected_to=["serrated_blades"],
     source="WotLK row 4, kept - a real unlock of a real ability, and the "
            "real talent also requires Serrated Blades, which "
            "connected_to reproduces. rogue_hemorrhage is now a combo "
            "generator, matching 'Awards 1 combo point.' The real 10-charge "
            "physical-damage debuff is not expressible - there is no charge "
            "system - so the ability stays the dot it already is.")

# ----------------------------------------------------------------- tier 3
node("master_of_subtlety", "Master of Subtlety",
     "Opening with Ambush, Garrote or Cheap Shot has a 33% chance per rank "
     "to increase all your damage by 10% for 2 turns.",
     3, -1, 3,
     proc={"trigger": "on_damage_cast", "chance": 33, "icd": 0,
           "ability_filter": OPENERS,
           "apply_effect": {"effect_id": "master_of_subtlety",
                            "name": "Master of Subtlety",
                            "effect_type": "buff", "duration": 2,
                            "stat_mods": {"all_damage": 0.10},
                            "on_target": False}},
     connected_to=["heightened_senses"],
     source="WotLK row 5, NEW to our tree: 'Attacks made while stealthed "
            "and for 6 seconds after breaking stealth cause an additional "
            "4%/7%/10% damage.' DEPARTURE on the trigger only - there is no "
            "stealth, so the window opens when you USE an opener, which is "
            "the moment stealth would have broken. The payoff is the real "
            "10% for the real 6 seconds (2 turns). Ranked by CHANCE rather "
            "than magnitude because a talent proc's chance scales with "
            "points_spent and its payload does not - so 4/7/10% at a fixed "
            "chance is not authorable, while 33/66/100% of a fixed 10% is, "
            "and reaches the same place at full rank.")

node("deadliness", "Deadliness",
     "Increases your attack power by 2% per rank.",
     3, 1, 5, effects={"attack_power_pct": 2.0},
     connected_to=["initiative"],
     source="WotLK row 5, built verbatim - this one really is a pure "
            "scalar in the real game too, 2% attack power per rank over 5 "
            "ranks, and is kept as such. attack_power_pct is PERCENTAGE "
            "POINTS (audit_talents caught this being authored as 0.06 "
            "elsewhere in the project).")

# ----------------------------------------------------------------- tier 4
node("enveloping_shadows", "Enveloping Shadows",
     "Shadows cling to you, increasing dodge by 2% per rank.",
     4, -3, 3, effects={"dodge": 2.0},
     connected_to=["master_of_subtlety"],
     source="WotLK row 6, NEW to our tree: 'Reduces the damage taken by "
            "area of effect attacks by 10%/20%/30%.' DEPARTURE - there is "
            "no aoe_damage_taken_pct key anywhere in this engine. Probed "
            "with tools/probe_talent_key.py: it reaches the talent bus and "
            "nothing reads it, and grep finds zero read sites, so authoring "
            "it would have been silent dead data. Delivered as raw dodge "
            "instead - general avoidance rather than AoE-specific "
            "mitigation, which is a real loss and is recorded as one.")

node("premeditation", "Premeditation",
     "You surface from Vanish with 2 combo points.",
     4, -1, 1,
     proc={"trigger": "on_cast", "chance": 100, "icd": 0,
           "ability_filter": ["rogue_vanish"],
           "grant_resource": {"resource": "combo", "amount": 40}},
     connected_to=["master_of_subtlety"],
     source="WotLK row 6: 'When used, adds 2 combo points to your target. "
            "You must add to or use those combo points within 20 sec or the "
            "combo points are lost.' DEPARTURE - there is no "
            "rogue_premeditation ability to unlock, so the 2 combo points "
            "are delivered off Vanish, which is what the real talent is "
            "FOR: it exists so a rogue re-opening from stealth does not "
            "start from zero. 40 is 2 points on the 20-per-point scale. The "
            "20-second expiry is dropped - nothing expires a resource. The "
            "real talent requires Preparation; connected_to keeps it "
            "downstream of Master of Subtlety instead, because Preparation "
            "sits on a different column here. The outgoing version was a "
            "WORKING proc - Ambush restoring 30 Energy at 100% - which is "
            "what Premeditation has to become when there are no combo "
            "points to add. Replaced with the real thing, not a fix.")

node("sinister_calling", "Sinister Calling",
     "Increases your Agility by 3% per rank and the damage of your Backstab "
     "and Hemorrhage by 2% per rank.",
     4, 1, 5,
     effects={"agility_pct": 3.0,
              "ability_rogue_backstab_damage": 0.02,
              "ability_rogue_hemorrhage_damage": 0.02},
     connected_to=["premeditation"],
     source="WotLK row 7, built verbatim including the real 3% Agility that "
            "the outgoing version omitted entirely (it was 4% damage on two "
            "abilities and nothing else). agility_pct is PERCENTAGE POINTS. "
            "The real talent requires Premeditation, which connected_to "
            "reproduces.")

node("cheat_death", "Cheat Death",
     "While below half health, all damage you take is reduced by 10% per "
     "rank.",
     4, 3, 3, effects={"low_health_damage_reduction_pct": 0.10},
     connected_to=["deadliness"],
     source="WotLK row 6: 'You have a 33%/66%/100% chance that an attack "
            "which would otherwise kill you will instead reduce you to 10% "
            "of your maximum health. In addition, all damage taken will be "
            "reduced by up to 90% for 3 sec.' DEPARTURE - there is no "
            "death-prevention hook, no 'would otherwise kill you' event, so "
            "the cheat-death half cannot be built. The mitigation half is "
            "real and kept. low_health_damage_reduction_pct reads the "
            "ACTOR's own health (combat_engine.py:541) and defaults to a "
            "50% threshold, which is why low_health_threshold_pct is NOT "
            "authored here - the outgoing version DID author it at 0.35, "
            "which both made Cheat Death fire at 35% instead of 50% and put "
            "the class one node away from the summing-threshold breach that "
            "tools/qa_summing_thresholds.py exists to catch.")

node("waylay", "Waylay",
     "Your Ambush and Backstab have a 50% chance per rank to unbalance the "
     "target, slowing its attacks for 2 turns.",
     4, 5, 2,
     proc={"trigger": "on_damage_cast", "chance": 50, "icd": 0,
           "ability_filter": ["rogue_ambush", "rogue_backstab"],
           "apply_effect": {"effect_id": "waylay", "name": "Waylay",
                            "effect_type": "debuff", "duration": 2,
                            "stat_mods": {"haste": -20}}},
     connected_to=["cheat_death"],
     source="WotLK row 7: 'Your Ambush and Backstab hits have a 50%/100% "
            "chance to unbalance a target, increasing the time between "
            "their melee and ranged attacks by 20%, and reducing movement "
            "speed by 50% for 8 sec.' Built faithfully apart from movement "
            "speed, which does not exist. The real ability list, the real "
            "50%-per-rank curve, and the real 20% attack slow as haste -20 "
            "on the target. 8 seconds is 2 turns. The outgoing version was "
            "a flat 12% Backstab damage bonus.")

# ----------------------------------------------------------------- tier 5
node("honor_among_thieves", "Honor Among Thieves",
     "When you critically hit, you have a 33% chance per rank to gain a "
     "combo point.",
     5, -1, 3,
     proc={"trigger": "on_crit", "chance": 33, "icd": 1,
           "grant_resource": {"resource": "combo", "amount": 20}},
     connected_to=["sinister_calling"],
     source="WotLK row 8: 'When anyone in your group critically hits with a "
            "damage or healing spell or ability, you have a 33%/66%/100% "
            "chance to gain a combo point on your current target. This "
            "effect cannot occur more than once every second.' DEPARTURE on "
            "the source only - on_crit fires for the ROGUE's own crits; a "
            "talent effect can never reach an ally and no trigger reports a "
            "party member's crit. Everything else is exact, including icd 1 "
            "for the once-per-second clause. The outgoing version was a "
            "WORKING proc - 25% per rank on_crit for 20 Energy - the "
            "same combo-points-do-not-exist substitution as Setup and "
            "Premeditation. All three are replaced because the resource "
            "arrived, not because they were broken.")

node("shadowstep", "Shadowstep",
     "Sprinting wreathes you in shadow, increasing the damage of your next "
     "strikes by 20% and halving your threat for 1 turn.",
     5, 1, 1,
     proc={"trigger": "on_cast", "chance": 100, "icd": 0,
           "ability_filter": ["rogue_sprint"],
           "apply_effect": {"effect_id": "shadowstep", "name": "Shadowstep",
                            "effect_type": "buff", "duration": 1,
                            "stat_mods": {"all_damage": 0.20,
                                          "threat_generation_pct": -50.0},
                            "on_target": False}},
     connected_to=["sinister_calling"],
     source="WotLK row 8: 'Attempts to step through the shadows and reappear "
            "behind your enemy and increases movement speed by 70% for 3 "
            "sec. The damage of your next ability is increased by 20% and "
            "the threat caused is reduced by 50%. Lasts 10 sec.' DEPARTURE "
            "- no rogue_shadowstep ability and no positioning in this "
            "engine. Delivered off Sprint, the only ability here that means "
            "'close the distance'. The two numbers that matter are the real "
            "ones: +20% damage and -50% threat. 'Next ability' is a 1-turn "
            "buff, since nothing consumes a buff on use. The outgoing "
            "version was +25% Ambush damage and a 20-energy cost cut.\n"
            "NOTE THE MIXED UNITS INSIDE THIS ONE stat_mods DICT, which "
            "audit_talents caught here: all_damage is a FRACTION (0.20 = "
            "20%) while threat_generation_pct is PERCENTAGE POINTS (-50.0 = "
            "-50%). Authored as -0.50 it was a 0.5% threat cut that looked "
            "entirely correct. There is no rule that infers this from the "
            "key name - the only reliable check is audit_talents.")

node("slaughter_from_the_shadows", "Slaughter from the Shadows",
     "Reduces the Energy cost of your Backstab and Ambush by 4 per rank, "
     "and increases all your damage by 1% per rank.",
     5, 3, 5,
     effects={"ability_rogue_backstab_cost": 4,
              "ability_rogue_ambush_cost": 4,
              "all_damage": 0.01},
     connected_to=["waylay"],
     source="WotLK row 9, built verbatim - the real 4 Energy per rank on "
            "both abilities and the real 1% all-damage per rank. The "
            "Hemorrhage cost clause is dropped as the smallest of the "
            "three. The outgoing version had the cost halves but omitted "
            "the all-damage bonus, which is the part that makes a 5-point "
            "capstone-adjacent node worth taking.")

node("filthy_tricks", "Filthy Tricks",
     "Reduces the cooldown of your Kick and Sap by 1 turn per rank, and of "
     "Preparation by 3 turns per rank.",
     5, 5, 2,
     effects={"ability_rogue_kick_cooldown": 1,
              "ability_rogue_sap_cooldown": 1,
              "ability_rogue_preparation_cooldown": 3},
     connected_to=["waylay"],
     source="WotLK row 8: 'Reduces the cooldown by 5/10 sec and energy cost "
            "by 5/10 of your Tricks of the Trade, Distract and Shadowstep "
            "abilities and reduces the cooldown of Preparation by 1.5/3 "
            "min.' Tricks of the Trade, Distract and Shadowstep do not "
            "exist here; Kick and Sap stand in as the utility cooldowns, "
            "which is what the outgoing version already did. The "
            "Preparation clause is the real one and is NEW - a 1.5-minute "
            "cut on a 20-turn cooldown re-derives as 3 turns per rank.")

# ----------------------------------------------------------------- tier 6
node("shadow_dance", "Shadow Dance",
     "Teaches Shadow Dance, letting you strike as though from the shadows.",
     6, 1, 1, node_type="active",
     effects={"unlock_ability": "rogue_shadow_dance"},
     connected_to=["slaughter_from_the_shadows"],
     source="WotLK row 10, the capstone, kept as-is - already a real unlock "
            "of a real ability. The real talent grants the use of opening "
            "abilities without stealth; rogue_shadow_dance is a buff, which "
            "is the nearest this engine gets, and the ability itself is "
            "where that is modelled rather than the talent.")


def main():
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"

    # Every connected_to must name a node in this tree.
    known = set(ids)
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in known, f"{n['talent_id']} connects to unknown {c}"

    # Every ability-scoped key and unlock must name a real ability.
    import glob
    real = set()
    for path in glob.glob(str(ROOT / "data/abilities/*.json")):
        for a in json.loads(Path(path).read_text()).get("abilities", []):
            real.add(a["ability_id"])
    sys.path.insert(0, str(ROOT / "tools"))
    from probe_talent_key import split_ability_key
    for n in TREE["nodes"]:
        for key in n["effects"]:
            if key == "unlock_ability":
                assert n["effects"][key] in real, \
                    f"{n['talent_id']} unlocks missing {n['effects'][key]}"
                continue
            split = split_ability_key(key)
            if split:
                assert split[0] in real, \
                    f"{n['talent_id']}: no ability '{split[0]}' for {key}"
        for spec in [(n.get("proc") or {})]:
            for aid in spec.get("ability_filter") or []:
                assert aid in real, \
                    f"{n['talent_id']}: ability_filter names missing {aid}"

    # low_health_threshold_pct must appear NOWHERE - it sums and is shared
    # between the target-side and actor-side conditionals. See docstring.
    for n in TREE["nodes"]:
        assert "low_health_threshold_pct" not in n["effects"], \
            f"{n['talent_id']} authors the shared summing threshold"

    points = sum(n["max_points"] for n in TREE["nodes"])
    assert points >= 56, f"only {points} points, need 56 for a level-60 pure spec"

    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"  wrote {OUT.relative_to(ROOT)}")
    print(f"  {len(ids)} nodes, {points} points\n")

    # HONEST CLASSIFICATION. A bare "scalar count" measures the wrong
    # thing: a node carrying ability_rogue_rupture_damage has no proc and
    # is not a flat stat either - it is a targeted mechanic. Counting it
    # as a scalar made this rebuild look like it moved 17 to 16 when what
    # actually changed was 3 procs to 9 and 3 flat stats to 4 across five
    # more nodes. The categories below are the ones worth reporting.
    CONDITIONAL = {"low_health_damage_pct", "low_health_damage_reduction_pct",
                   "low_health_healing_pct", "execute_threshold_pct"}

    def classify(n):
        if n.get("proc"):
            return "proc"
        eff = n.get("effects") or {}
        if "unlock_ability" in eff:
            return "unlock"
        if not eff:
            return "EMPTY - does nothing"
        if any(k in CONDITIONAL for k in eff):
            return "conditional"
        scoped = [bool(split_ability_key(k)) for k in eff]
        if all(scoped):
            return "ability-scoped"
        if any(scoped):
            return "mixed"
        return "flat stat"

    from collections import Counter
    counts = Counter(classify(n) for n in TREE["nodes"])
    for kind, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"      {kind:24s} {n}")
    print("\n  was: 23 nodes, 59 points - 3 proc, 13 ability-scoped, "
          "3 flat stat, 3 unlock, 1 conditional")
    assert counts["EMPTY - does nothing"] == 0, "a node does nothing"
    return 0


if __name__ == "__main__":
    sys.exit(main())
