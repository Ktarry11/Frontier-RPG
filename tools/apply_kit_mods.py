#!/usr/bin/env python3
"""Give inert personal-kit abilities real stat_mods, from a HAND-WRITTEN table.

    PYTHONPATH=. python3 tools/apply_kit_mods.py [--apply]

Idempotent: an ability that already has stat_mods is skipped, so a re-run
after hand-editing the data changes nothing.

=============================================================================
WHY THIS TABLE IS WRITTEN OUT BY HAND
=============================================================================

tools/repair_personal_kits.py tried to derive these from each ability's
description with regex. Of the 28 it proposed, a third were wrong, because the
descriptions make distinctions a pattern cannot see:

    "Sondre's spells DEAL 20% less damage"   -> his own output, a drawback
    "Pasang TAKES 25% less damage"           -> his own mitigation, a benefit
    "every ENEMY DEALS 25% less damage"      -> the enemies' output

All three are "20-25% less damage". The regex read the second reading into the
first, which turned Sondre's deliberate drawback into a defensive buff.

So that tool is analysis-only now and this one holds the decisions. Every row
below was read against its own description and its target_type.

=============================================================================
THE KEYS, AND WHAT THEY REALLY DO
=============================================================================

Verified by reading the code, not from the convention doc, because several of
these are wider or narrower than the doc implies:

    damage_dealt_pct        PERCENT POINTS. The caster's whole outgoing
                            damage. combat/abilities.py:1710 - and it is
                            SCHOOL-AGNOSTIC on purpose: the school-specific
                            names (fire_damage_pct, shadow_damage_pct, ...)
                            were folded into this one key during the
                            stat-vocabulary cleanup, so there is no
                            fire-only channel to put Skye's rule in.
    healing_done_pct        PERCENT POINTS. Same path, healing school.
    physical_/magic_damage_taken_pct
                            PERCENT POINTS, and read by Monster as well as
                            Character (entities/monster.py:1067).
    damage_taken_pct        FRACTION. Not used below - the two per-school
                            keys cover "damage of any kind" and keep one
                            unit across the table.
    threat_generation_pct   PERCENT POINTS, via combat_engine. "Triple
                            threat" is +200, not 300.
    all_ability_cost_pct    FRACTION, positive REDUCES. abilities.py:1257.
    taunt                   A real flag, not a stat: abilities.py:1931 turns
                            it into level*500 threat, enough to top the
                            table outright. This is why several abilities
                            below get their "attacks only X" half for free.
    haste                   PERCENT POINTS. Negative is a real slow.

=============================================================================
WHAT IS DELIBERATELY LEFT UNDONE, AND WHY THAT IS NOT THE SAME AS BROKEN
=============================================================================

Three rows deliver their effect while their COST goes unpaid - Kesten's and
Karim's health price, Eino's "gains nothing from any ally's buffs". The
headline effect is the ability; the price is a mechanic the engine has no hook
for. Shipping the effect makes them strong rather than inert, which is a
balance note Kyle can see and tune, not a silent no-op. Each is flagged in the
output so the number is visible.

One row is NOT here and should be looked at: Gianluca's "Defused More Fights
With a Joke", target_type all_enemies, "every enemy deals 25% less damage".
Monsters take only a FLAT attack_power swing from buffs and debuffs
(entities/monster.py:865) - there is no percentage on their output anywhere.
The identical outcome is "the party takes 25% less damage", but that means
changing the ability's target_type to party, which moves where the icon sits
and what can dispel it. That is a design call, not a repair.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "data" / "npcs" / "personal_kits.json"

#: ability_id -> StatusEffect scaling spec, for abilities written as a RATE
#: rather than a flat value. stat_mods below stay PER UNIT and this supplies
#: the count - see StatusEffect.scaling_multiplier. `cap` caps the
#: MULTIPLIER, not the final percentage, so Pasang's "up to 24%" at -4 per
#: turn is cap 6.
#:
#: Authoring the per-unit number as a flat value instead is what the
#: abandoned regex pass did, and it delivers a quarter of what the tooltip
#: promises while looking repaired.
SCALING = {
    "personal_dan_four_men_long_shifts": {"source": "living_allies", "cap": 4},
    "personal_owen_something_answered": {"source": "missing_health_pct",
                                         "divisor": 2, "cap": 50},
    "personal_pasang_day_four": {"source": "turns_active", "cap": 6},
    "personal_nicolas_toward_what_everyone_goes_away_from": {
        "source": "missing_health_pct", "divisor": 3, "cap": 33},
}

#: ability_id -> damage-sharing spec. The buff lands on each RECIPIENT and
#: points back at the caster, so the victim's take_damage knows where to send
#: a share - see Character._share_damage_out.
#:
#: `pct` is the share of each landed hit that moves. `reduction_pct` is a
#: discount on what the GUARDIAN pays, not on what the victim saves: Marco's
#: "redirected to Marco, reduced by 33%" means the ally loses the whole blow
#: and Marco takes two thirds of it. `uses` limits how many hits move, for
#: the ones written as "the NEXT attack".
DAMAGE_SHARE = {
    "personal_pasang_he_carried_loads": {"pct": 30},
    "personal_nicolas_soaking_what_is_aimed": {"pct": 35},
    "personal_elias_an_air_of_mild_apology": {"pct": 30, "heal_pct": 10},
    "personal_marco_somebody_had_to": {"pct": 100, "reduction_pct": 33},
    "personal_saoirse_expecting_to_be_run_at": {"pct": 100, "reduction_pct": 40},
    "personal_dan_stand_in_front": {"pct": 100, "reduction_pct": 50, "uses": 1},
    "personal_dan_shift_change": {"pct": 100, "uses": 1},
}

#: ability_id -> death-prevention spec. `pct` or `hp` is the health level the
#: blow is clamped to. `lethal_only` false catches any blow that crosses the
#: line rather than only a killing one, which is Henrik's wording.
DEATH_PREVENT = {
    # "the next hit that would reduce Henrik BELOW 20% instead leaves him at
    # 20%" - a threshold, not a killing blow, which is the one of the four
    # that is not lethal_only.
    "personal_henrik_he_does_not_approach_them": {"pct": 20,
                                                  "lethal_only": False},
    "personal_minh_the_one_in_which_nobody_dies": {"hp": 1},
    "personal_pieter_nine_men_in_three_years": {"pct": 15},
    "personal_saoirse_teach_them_to_fall_properly": {"pct": 20},
}

#: ability_id -> reflect spec. Callum's is returned as NATURE regardless of
#: what hit him, and only off melee, which is why school and melee_only are
#: separate from the percentage.
REFLECT = {
    "personal_callum_the_thing_that_bites_back": {
        "pct": 40, "school": "nature", "melee_only": True},
    "personal_matias_standing_still_in_a_crowd": {"pct": 30},
}

#: ability_id -> low-health trigger. `pct` arms it, and the payout is either
#: a heal or a shield, both as a percent of the holder's MAXIMUM health.
ON_LOW_HEALTH = {
    "personal_amber_a_mistake_corrects_itself": {"pct": 35, "heal_pct": 30},
    "personal_ileana_first_on_her_feet": {"pct": 30, "shield_pct": 25},
    "personal_vuk_a_second_bowl": {"pct": 25, "heal_pct": 50},
}

#: ability_id -> immediate turn-meter grant, as a FRACTION of TURN_THRESHOLD.
#: 1.0 fills the meter, which means "acts next" in this engine's meter-based
#: order and - because consume_turn carries the overflow forward - is also
#: how an extra action is expressed.
TURN_METER_BOOST = {
    "personal_rosa_four_seconds": 1.0,
    "personal_sondre_first_awake_every_morning": 1.0,
    "personal_camille_twenty_two_minutes": 1.0,
    "personal_nizar_holding_the_order_of_things": 1.0,
    "personal_emre_one_door_closes": 1.0,
    "personal_sophia_simultaneous": 1.0,
}

#: ability_id -> flat absorb shield. `absorb` is an EXISTING, fully wired
#: Ability field consumed by the shield branch at the top of take_damage, so
#: these three needed no engine work at all - only the number, which was
#: already sitting in each one's effect_value.
ABSORB = {
    "personal_henrik_certain_it_will_hold": 220,
    "personal_tarek_he_calls_it_building": 70,
    "personal_alonso_made_a_cup_badly": 180,
}

#: ability_id -> incoming damage converted into a shield.
DAMAGE_TO_SHIELD = {
    "personal_owen_he_gets_sentences": {"pct": 40, "school": "magic"},
}

#: ability_id -> incoming damage healed back. Sibling to DAMAGE_TO_SHIELD.
DAMAGE_TO_HEAL = {
    "personal_alonso_feels_a_draught": {"pct": 30, "school": "fire"},
}

#: ability_id -> True suppresses DOT ticks on the recipient for the duration.
DOT_IMMUNE = {
    "personal_thiago_without_making_it_worse": True,
}

#: ability_id -> a heal-over-time armed on taking any damage, as distinct
#: from ON_LOW_HEALTH, which waits for a threshold.
ON_DAMAGE_HOT = {
    "personal_delroy_the_weather_in_the_dough": {"potency": 30, "duration": 3},
}

#: ability_id -> effect_type override. Two of these were authored as `buff`
#: with an empty stat_mods when the text describes a plain heal-over-time,
#: and `hot` is a full effect_type the engine has supported all along - the
#: tick path, the tooltip and the stacking scale are already written and
#: tested. Re-categorising them uses that rather than adding a second
#: per-turn-healing mechanism beside it.
EFFECT_TYPE = {
    "personal_thiago_without_making_it_worse": "hot",
    "personal_osvaldo_just_sitting_there": "hot",
}

#: ability_id -> (max_stacks, what earns a stack). stat_mods below are PER
#: STACK, the convention stacking effects and talent ranks already use, so
#: the cap is the number of STACKS and not the final percentage: Nizar's
#: "15% more, stacking to 75%" is 15 per stack with max_stacks 5.
STACKING = {
    "personal_imelda_ten_fights_a_year": (5, "attack"),
    "personal_driss_a_wrong_turn": (3, "repeat"),
    "personal_nizar_the_same_proof_for_the_ninth_time": (5, "repeat"),
}

#: ability_id -> (stat_mods, what the row delivers, what it still cannot do)
TABLE = {
    # --- stacks earned from events -----------------------------------------
    "personal_imelda_ten_fights_a_year": (
        {"healing_done_pct": 8},
        "+8% healing done per landed attack, stacking to 40%", None),
    "personal_driss_a_wrong_turn": (
        {"physical_damage_taken_pct": 15, "magic_damage_taken_pct": 15},
        "the target takes 15% more damage per ability it repeats, to 45%",
        None),
    "personal_nizar_the_same_proof_for_the_ninth_time": (
        {"damage_dealt_pct": 15},
        "+15% damage per repeat of the same spell, stacking to 75%", None),

    # --- the healing family -------------------------------------------------
    "personal_alonso_feels_a_draught": (
        {}, "fire damage taken by the party heals them for 30% of it", None),
    "personal_thiago_without_making_it_worse": (
        {}, "that ally takes no damage over time and is healed each turn",
        None),
    "personal_osvaldo_just_sitting_there": (
        {}, "the chosen ally heals each turn",
        "Osvaldo healing them MORE on a turn he does not attack"),
    "personal_delroy_the_weather_in_the_dough": (
        {}, "the next damage each ally takes starts a 3-turn heal", None),

    # --- absorb shields, all three data-only -------------------------------
    # "cannot be broken early" is already true of an absorb shield here -
    # nothing in the engine strips one - so Henrik's is complete.
    "personal_henrik_certain_it_will_hold": (
        {}, "a 220-point shield on an ally for 4 turns", None),
    "personal_tarek_he_calls_it_building": (
        {}, "a 70-point shield on the party", None),
    "personal_alonso_made_a_cup_badly": (
        {}, "a 180-point shield on an ally for 5 turns",
        "what remains of the shield surviving past the buff's expiry"),

    "personal_owen_he_gets_sentences": (
        {}, "40% of the magic damage Owen takes comes back as a shield",
        None),

    # --- turn order and extra actions --------------------------------------
    "personal_rosa_four_seconds": (
        {}, "Rosa acts next, before every enemy", None),
    "personal_sondre_first_awake_every_morning": (
        {}, "the whole party acts before every enemy", None),
    # The -40% is the price of the second action and lasts as long as the
    # buff, which is what the text describes.
    "personal_camille_twenty_two_minutes": (
        {"damage_dealt_pct": -40},
        "acts again immediately, at 40% less damage for the duration", None),
    "personal_nizar_holding_the_order_of_things": (
        {}, "the party acts first",
        "LOCKING the turn order against other effects"),
    "personal_emre_one_door_closes": (
        {}, "Emre takes another action",
        "triggering automatically on a killing blow rather than on cast"),
    # "a second spell this turn at 60% damage" - the extra action is real;
    # the penalty applying to only that one cast is not expressible, so it
    # rides the buff's duration instead and is flagged.
    "personal_sophia_simultaneous": (
        {"damage_dealt_pct": -40},
        "casts again immediately, at reduced damage",
        "confining the reduction to the extra cast alone"),

    # --- damage returned to whoever dealt it -------------------------------
    "personal_callum_the_thing_that_bites_back": (
        {}, "returns 40% of melee damage taken as nature damage", None),
    "personal_matias_standing_still_in_a_crowd": (
        {}, "every attacker takes 30% of the damage back", None),

    # --- armed on dropping below a health threshold ------------------------
    "personal_amber_a_mistake_corrects_itself": (
        {}, "first drop below 35% heals that ally for 30% of their maximum",
        None),
    "personal_ileana_first_on_her_feet": (
        {}, "first drop below 30% shields each ally for 25% of their maximum",
        None),
    # Party-scoped, so each ally carries their own one-use copy. The text is
    # "sets aside a heal" for whoever drops first - ONE heal across the
    # party - which a per-ally effect cannot express without a shared
    # counter, so this is more generous than written.
    "personal_vuk_a_second_bowl": (
        {}, "first drop below 25% heals that ally for 50% of their maximum",
        "reserving a SINGLE heal for the party rather than one per ally"),

    # --- a blow that would kill is held at a floor instead -----------------
    # No stat_mods: the whole effect is the floor. Minh's and Saoirse's are
    # party-scoped, so each ally carries their own one-use floor, which is
    # exactly Minh's "Once per ally".
    "personal_henrik_he_does_not_approach_them": (
        {}, "the next blow that would take him below 20% leaves him at 20%",
        None),
    "personal_minh_the_one_in_which_nobody_dies": (
        {}, "the first killing blow on each ally leaves them at 1 health",
        None),
    "personal_pieter_nine_men_in_three_years": (
        {}, "the first killing blow on that ally leaves them at 15%", None),
    "personal_saoirse_teach_them_to_fall_properly": (
        {}, "the first killing blow on each ally leaves them at 20%", None),

    # --- a guardian soaking hits aimed at other people ---------------------
    # These carry NO stat_mods: the whole effect is the share, which lives in
    # DAMAGE_SHARE above. An empty stat_mods on a buff normally means inert,
    # so is_active_kit_ability() in this file is what decides, not the
    # emptiness of the dict.
    "personal_pasang_he_carried_loads": (
        {}, "absorbs 30% of all damage dealt to the party", None),
    "personal_nicolas_soaking_what_is_aimed": (
        {}, "takes 35% of all damage dealt to the party", None),
    "personal_elias_an_air_of_mild_apology": (
        {}, "takes 30% of the party's damage and heals for a tenth of it",
        None),
    "personal_marco_somebody_had_to": (
        {}, "the chosen ally's damage comes to Marco at a 33% discount",
        None),
    "personal_saoirse_expecting_to_be_run_at": (
        {}, "takes every blow aimed at the chosen ally, reduced by 40%",
        None),
    "personal_dan_stand_in_front": (
        {}, "the next attack on any ally comes to Dan, halved", None),
    "personal_dan_shift_change": (
        {}, "the attack already aimed at that ally hits Dan instead",
        "swapping row position with the ally"),

    # --- written as a RATE; the count comes from SCALING above -------------
    "personal_dan_four_men_long_shifts": (
        {"physical_damage_taken_pct": -6, "magic_damage_taken_pct": -6},
        "takes 6% less damage per living ally, to -24% at full party",
        "forcing all enemies onto him at full party; a cooldown that starts "
        "on expiry"),

    "personal_owen_something_answered": (
        {"damage_dealt_pct": 1},
        "deals 1% more damage per 2% of health missing, to +50%", None),

    "personal_pasang_day_four": (
        {"physical_damage_taken_pct": -4, "magic_damage_taken_pct": -4},
        "takes 4% less damage per turn the buff has been up, to -24%", None),

    "personal_nicolas_toward_what_everyone_goes_away_from": (
        {"damage_dealt_pct": 1, "physical_damage_taken_pct": -1,
         "magic_damage_taken_pct": -1},
        "1% more dealt and 1% less taken per 3% of health missing", None),

    # --- fully expressible: every clause of the description lands ------------
    "personal_pasang_he_has_the_names": (
        {"physical_damage_taken_pct": -25, "magic_damage_taken_pct": -25,
         "damage_dealt_pct": 25},
        "takes 25% less damage of either kind, deals 25% more", None),

    "personal_pieter_shouted_at_by_thousands": (
        {"threat_generation_pct": 200, "physical_damage_taken_pct": -20,
         "magic_damage_taken_pct": -20},
        "triple threat, takes 20% less damage", None),

    "personal_matias_clicks_it_twice": (
        {"damage_dealt_pct": 25, "physical_damage_taken_pct": -15,
         "magic_damage_taken_pct": -15},
        "deals 25% more, takes 15% less", None),

    "personal_giorgi_completely_unhurried": (
        # "acts at half speed" is the drawback and haste expresses it, so
        # this is the one trade-off row where both sides are real.
        {"damage_dealt_pct": 40, "physical_damage_taken_pct": -35,
         "magic_damage_taken_pct": -35, "haste": -50},
        "deals 40% more, takes 35% less, acts at half speed", None),

    "personal_elias_four_walls_and_a_roof": (
        # target_type party already scopes it; no party loop needed here.
        {"physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20},
        "party takes 20% less damage",
        "immunity to weather and terrain effects"),

    # --- the taunt half is real, the percentage half is not -----------------
    # Both of these read "the target attacks only X". That IS implemented -
    # taunt generates level*500 threat and tops the table. What cannot be
    # expressed is the percentage riding along with it, because it applies to
    # a MONSTER's output and monsters have no outgoing-damage multiplier.
    # Both clauses now. The second needed a percentage on MONSTER output,
    # which did not exist until Monster.damage_output_multiplier was added -
    # see that property for Kyle's "enemies are different that players".
    "personal_fiona_unbearable_until_somebody_checks": (
        {"taunt": 1, "damage_dealt_pct": -20},
        "the target attacks only Fiona and deals 20% less damage", None),

    # --- unlocked by the monster-side output multiplier --------------------
    "personal_gianluca_defused_with_a_joke": (
        {"damage_dealt_pct": -25},
        "every enemy deals 25% less damage", None),

    "personal_pieter_exclusion_zone": (
        # enemy_aoe reaches the pack rather than one row; the row-scoping
        # half still wants real row targeting, so it stays flagged.
        {"damage_dealt_pct": -30},
        "enemies deal 30% less damage",
        "limiting it to a single enemy ROW (needs row-scoped targeting)"),

    # taunt on all_enemies - the flag was already live, this ability just
    # never carried it.
    "personal_callum_youre_enormous": (
        {"taunt": 1},
        "every enemy attacks Callum and nobody else",
        "the boss exemption its text promises"),

    "personal_vuk_too_irritated_to_leave_it_alone": (
        # The +25% belongs to Vuk, but this ability lands on the enemy, so a
        # damage_dealt_pct here would buff the target instead of him. Wrong
        # actor, so it stays off.
        {"taunt": 1},
        "the target attacks only Vuk",
        "Vuk's own +25% against it (lands on the wrong actor from here)"),

    "personal_gianluca_a_running_commentary": (
        # target_type party, so a taunt would land on his allies.
        {"physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20},
        "party takes 20% less damage",
        "enemies targeting Gianluca first (taunt needs a self/enemy target)"),

    # --- one clause real, the rest needs engine work ------------------------
    "personal_diego_working_in_the_dark": (
        {"all_ability_cost_pct": 0.30},
        "abilities cost 30% less",
        "immunity to blind, silence and interrupt"),

    "personal_skye_a_rule_she_tells_nobody": (
        # Generic rather than fire-only because the engine has no per-school
        # dealt channel at all. Skye casts fire and little else, so in her
        # hands the generic key is what the text describes.
        {"damage_dealt_pct": 45},
        "deals 45% more damage",
        "never striking an ally (no friendly-fire logic); not fire-specific"),

    # --- the row the regex got exactly backwards ----------------------------
    # "Sondre's spells DEAL 20% less damage and cannot miss" is a trade: a
    # real drawback bought with reliability. The regex read "20% less damage"
    # as mitigation and gave him magic_damage_taken_pct -20, turning the
    # drawback into a defensive buff.
    #
    # Both halves are expressible, which is why this is here rather than in
    # the left-alone pile: damage_dealt_pct carries the cost, and hit_rating
    # is a live stat that drives base_miss_chance down via
    # max(0.0, BASE_MISS - hit_rating) (character.py:1410) for BOTH the spell
    # and physical lines, so a saturating 100 is a real "cannot miss" with no
    # new engine code. Shipping only the drawback would have been worse than
    # inert - an ability that actively harms the caster.
    # Fully expressible, all three clauses. spell_penetration 30 is not a
    # magic number: Kyle, 7 Nov - "a creature at end game could have 60
    # resistance, which allowed for 75% resistance to a school... 1 spell pen
    # = 2 resistance override, so getting 30 spell pen means a fire mage
    # could do 100% damage to something with 60 fire res". The engine already
    # names it, SPELL_PEN_USEFUL_MAX = RESIST_MAX // SPELL_PEN_PER_RESIST
    # (character.py:2860), so 30 IS "cannot be resisted".
    "personal_sondre_control_not_power": (
        {"damage_dealt_pct": -20, "hit_rating": 100, "spell_penetration": 30},
        "deals 20% less damage, cannot miss, cannot be resisted", None),

    # --- the two I wrongly parked as needing engine work -------------------
    # Both keys were ALREADY wired, at Kyle's own instruction, and I reported
    # them dead this morning because I grepped combat/ for the consumption
    # while both live in entities/. apply_spell_penetration is
    # character.py:2926 (used at :3244 and :3259, and monster.py:942);
    # expertise is monster.py:1028-1034, which computes
    # dodge = max(0.0, self.dodge - expertise) and the same for parry - the
    # exact dodge/parry roll. Checking only one directory is the same
    # instrument failure the conventions doc keeps a tally of.
    "personal_sophia_a_grammar_of_this_world": (
        {"spell_penetration": 30},
        "spells ignore enemy resistance entirely", None),

    # Expertise is percent points subtracted from the target's dodge and
    # parry and floored at 0. The highest base_dodge and base_parry anywhere
    # in creature data are 10 and 8, so 50 clears any reachable total with
    # room for a creature buff on top - "cannot be dodged or parried" as
    # written, without inventing a flag the engine does not have.
    "personal_carolina_feel_the_bottom": (
        {"expertise": 50},
        "attacks cannot be dodged or parried", None),

    # --- resistance debuffs, which needed no engine work at all -------------
    # Monster.get_resistance already folds status stat_mods in - its own
    # docstring says the value holds "however the number arrived - template
    # baseline, cast affinity, A STATUS EFFECT, or a hand-authored value" -
    # and Character.get_resistance does the same. Measured: a level-60
    # creature at 60 fire resistance drops to 20 under a -40 debuff.
    #
    # Only the two abilities naming a FIXED school and amount are here. The
    # two that pick a school at runtime - Marta's "the target's LOWEST
    # resistance" and Ryan's "the target's HIGHEST resistance" - need the
    # dynamic scaling work and stay inert rather than being flattened into
    # an all-schools debuff, which would be strictly stronger than written.
    "personal_kourosh_characterising_it": (
        {"arcane_resistance": -40},
        "target's arcane resistance reduced by 40", None),

    "personal_kesten_if_you_know_the_hand": (
        {"fire_resistance": -20, "frost_resistance": -20, "nature_resistance": -20,
         "shadow_resistance": -20, "arcane_resistance": -20, "holy_resistance": -20},
        "all six of the target's resistances reduced by 20",
        "SHOWING the target's resistances and ability set (a UI reveal)"),

    # --- effect delivered, COST UNPAID. Flagged in the output. --------------
    "personal_kesten_reading_his_own_entry": (
        {"damage_dealt_pct": 25},
        "deals 25% more damage",
        "COST UNPAID: spends 15% of his health"),

    "personal_eino_six_months_of_dark": (
        {"damage_dealt_pct": 25},
        "deals 25% more damage",
        "COST UNPAID: gains nothing from any ally's buffs"),

    "personal_karim_the_fastest_route_to_useful": (
        {"threat_generation_pct": 200, "damage_dealt_pct": 30},
        "triple threat, deals 30% more damage",
        "COST UNPAID: spends 20% of his health"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    doc = json.loads(KITS.read_text())
    done, skipped, unseen = [], [], set(TABLE)
    rescaled = []

    # PASS 0 - the same double-scaling bug on abilities this table never
    # touches. tools/qa_kit_mods.py found nine kit abilities that shipped
    # WITH stat_mods and an effect_value between 1 and 99, so they have been
    # delivering a fraction of their own tooltip since they were authored:
    #
    #   Ryan Murphy, "Clause by Clause"        30% -> 9%, -40% taken -> -12%
    #   Stelios Dukas, "The Steadiest Person"  15 shadow resist -> 2, and
    #                                          cc_immune 1 -> 0, so the
    #                                          immunity flag was erased
    #   Driss Alaoui, "He Asked the Land"      20 dodge -> 4
    #   Marisol Quintero, "The Habit of..."    -20% taken -> -4%
    #   Ivan Petrov, "Directing Traffic"       15 haste -> 2
    #   Ratih Pranoto, "A Silence Where..."    everything x0.08
    #
    # Nothing on screen disagreed with anything: the tooltip builds from
    # stat_mods and showed the full number throughout.
    #
    # effect_value 0 is LEFT ALONE - abilities.py:1548 reads that as "apply
    # the mods as written" on purpose, so it is already correct.
    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            if a.get("effect_type") not in ("buff", "debuff"):
                continue
            if not a.get("stat_mods") or a.get("ability_id") in TABLE:
                continue
            for r in (a.get("ranks") or []):
                ev = r.get("effect_value") or 0
                if ev not in (0, 100):
                    rescaled.append((kit.get("name"), a.get("name"), ev))
                    if args.apply:
                        r["effect_value"] = 100

    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            aid = a.get("ability_id")
            if aid not in TABLE:
                continue
            unseen.discard(aid)
            mods, delivers, gap = TABLE[aid]
            # TABLE IS AUTHORITATIVE FOR ITS OWN ROWS. Skipping anything that
            # already has mods meant a corrected or extended row could never
            # land: Sondre gained a spell_penetration clause after his first
            # apply and the re-run silently kept the old two-key version.
            # Only an exact match is a skip, so the tool stays idempotent
            # while a table edit still takes effect.
            want_scaling = SCALING.get(aid)
            want_share = DAMAGE_SHARE.get(aid)
            want_floor = DEATH_PREVENT.get(aid)
            if (a.get("stat_mods") == mods
                    and a.get("scaling") == want_scaling
                    and a.get("damage_share") == want_share
                    and a.get("death_prevent") == want_floor
                    and a.get("reflect") == REFLECT.get(aid)
                    and a.get("on_low_health") == ON_LOW_HEALTH.get(aid)
                    and (a.get("turn_meter_boost") or 0)
                        == TURN_METER_BOOST.get(aid, 0)
                    and (a.get("absorb") or 0) == ABSORB.get(aid, 0)
                    and a.get("damage_to_shield") == DAMAGE_TO_SHIELD.get(aid)
                    and a.get("damage_to_heal") == DAMAGE_TO_HEAL.get(aid)
                    and bool(a.get("dot_immune")) == DOT_IMMUNE.get(aid, False)
                    and a.get("on_damage_hot") == ON_DAMAGE_HOT.get(aid)
                    and (EFFECT_TYPE.get(aid) is None
                         or a.get("effect_type") == EFFECT_TYPE[aid])
                    and ((a.get("max_stacks") or 1), a.get("stack_on"))
                        == STACKING.get(aid, ((a.get("max_stacks") or 1),
                                              a.get("stack_on")))):
                skipped.append((kit.get("name"), a.get("name")))
                continue
            done.append((kit.get("name"), a.get("name"), mods, delivers, gap))
            if args.apply:
                a["stat_mods"] = dict(mods)
                if want_scaling:
                    a["scaling"] = dict(want_scaling)
                if want_share:
                    a["damage_share"] = dict(want_share)
                if want_floor:
                    a["death_prevent"] = dict(want_floor)
                if REFLECT.get(aid):
                    a["reflect"] = dict(REFLECT[aid])
                if ON_LOW_HEALTH.get(aid):
                    a["on_low_health"] = dict(ON_LOW_HEALTH[aid])
                if TURN_METER_BOOST.get(aid):
                    a["turn_meter_boost"] = TURN_METER_BOOST[aid]
                if ABSORB.get(aid):
                    a["absorb"] = ABSORB[aid]
                if DAMAGE_TO_SHIELD.get(aid):
                    a["damage_to_shield"] = dict(DAMAGE_TO_SHIELD[aid])
                if DAMAGE_TO_HEAL.get(aid):
                    a["damage_to_heal"] = dict(DAMAGE_TO_HEAL[aid])
                if DOT_IMMUNE.get(aid):
                    a["dot_immune"] = True
                if ON_DAMAGE_HOT.get(aid):
                    a["on_damage_hot"] = dict(ON_DAMAGE_HOT[aid])
                if EFFECT_TYPE.get(aid):
                    a["effect_type"] = EFFECT_TYPE[aid]
                if STACKING.get(aid):
                    a["max_stacks"], a["stack_on"] = STACKING[aid]
                # EVERY rank is forced to 100, not just the zero ones.
                #
                # _stat_mod_scalar multiplies the authored mods by
                # effect_value/100, and these ranks already carried the
                # description's own number there - Skye's rank said 45, so a
                # 45 in stat_mods came out as 20.25, and Karim's 200 threat
                # became 60. The magnitude was being applied twice.
                #
                # It read as 100 before only because the mods were EMPTY and
                # abilities.py:1548 falls back to 1.0 in that case. Filling
                # the mods in is exactly what takes that fallback away, so
                # the two changes have to land together.
                #
                # 100 is the dominant convention (74 of the nine original
                # classes' buff ranks are exactly 100) and effect_value is
                # not read anywhere else for a buff - the tooltip builds from
                # stat_mods (abilities.py:1055), not from the scalar.
                for r in (a.get("ranks") or []):
                    r["effect_value"] = 100
                # Only ever REPLACE an engine note, never delete one. These
                # notes are authored design intent - Pasang's says "needs:
                # on-ally-death trigger with a duration", which is still true
                # after the mods land, because the mods make the ability work
                # when cast, not when an ally actually falls.
                if gap:
                    a["engine"] = f"needs: {gap}"

    print(f"  {len(done)} abilities given real stat_mods"
          + (f", {len(skipped)} already had some" if skipped else ""))
    if rescaled:
        print(f"  {len(rescaled)} already-live ability rank(s) were scaling "
              f"their own mods down; effect_value -> 100:")
        for who, name, ev in rescaled:
            print(f"    {str(who)[:15]:17}{str(name)[:34]:36}was {ev} "
                  f"(x{ev / 100:.2f})")
    if unseen:
        print(f"  !! {len(unseen)} table row(s) matched no ability: {sorted(unseen)}")

    print()
    for who, name, mods, delivers, gap in done:
        print(f"  {str(who)[:15]:17}{str(name)[:30]:32}{delivers}")
        print(f"  {'':17}{json.dumps(mods)}")
        if gap:
            print(f"  {'':17}still missing: {gap}")
    costs = [d for d in done if d[4] and d[4].startswith("COST UNPAID")]
    if costs:
        print(f"\n  {len(costs)} deliver their effect while the price goes unpaid - "
              f"a balance note, not a no-op:")
        for who, name, _m, _d, gap in costs:
            print(f"    {str(who)[:15]:17}{str(name)[:30]:32}{gap[13:]}")

    if args.apply:
        KITS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        print(f"\n  wrote {KITS.relative_to(ROOT)}")
    else:
        print("\n  dry run - pass --apply to write")
    return 1 if unseen else 0


if __name__ == "__main__":
    sys.exit(main())
