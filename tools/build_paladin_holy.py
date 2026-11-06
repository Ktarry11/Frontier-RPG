#!/usr/bin/env python3
"""Rebuild Paladin Holy from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_paladin_holy.py

SOURCE: data/reference/wotlk/paladin.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/paladin.md.

ROLE: the single-target healer. Holy Light and Flash of Light, Holy Shock,
and Judgement as the mana engine.

WHAT THIS TREE RUNS INTO. Holy is the tree most dependent on systems this
engine does not have, and it is worth stating the count: SEVEN of its 26
real talents are written on cast times or spell pushback (Spiritual Focus,
Light's Grace, Infusion of Light), on AURAS (Aura Mastery, Improved
Concentration Aura), or on the Hand spells (Blessed Hands). None of those
exist - there are no cast times at all, no auras, and no Hand of Freedom /
Sacrifice / Salvation / Protection.

Auras deserve a note of their own because three trees reference them and
Kyle already ruled on the shape: the CoA aura abilities were converted to
target_type "party" rather than modelled as a persistent aura slot. There
is still no aura SYSTEM for a talent to improve, so aura talents here pay
out as the thing the aura was for.

STAT CONVERSION IS USED, and the unit is the trap. Holy Guidance is
"+20% spell power from Intellect", which is exactly what
spell_power_from_intellect_pct does - but the key is read as
`gained = source_stat * pct` (character.py:1551), so it is a RAW
MULTIPLIER, not a percentage. Authoring 20 would have granted twenty times
the paladin's Intellect as spell power; measured live, 50 gave +2400 spell
power off 48 Intellect. It is authored as 0.04 per rank here.

Valid conversion targets include spell_power / spell_damage / healing_power
and valid sources include intellect / strength / ap - so these pairings are
real. hit_rating and stamina are NOT valid targets, which has cost this
project ten nodes half their text already.

UNIT CONVENTIONS, probed:

    mp5                            FLAT, lands on the attribute
    intellect_pct                  PERCENTAGE POINTS (read off `bonuses`
                                   and divided by 100, so the probe finds
                                   no literal read site)
    crit_chance_spell              PERCENTAGE POINTS
    healing_done, healing_taken_pct  FRACTION
    magic_damage_taken_pct         FRACTION as a talent effect, NEGATIVE
                                   reduces
    damage_taken_pct               RAW on both sides
    all_ability_cost_pct           FRACTION, POSITIVE IS A REDUCTION
    stun_duration_reduction_pct    FRACTION
    hit_rating                     PERCENTAGE POINTS
    *_from_*_pct                   FRACTION (raw multiplier of the source)
    ability_<id>_healing           FRACTION - and this is the key 18
                                   talents across four classes got WRONG by
                                   using _damage on a heal, so every heal
                                   node here uses _healing
    ability_<id>_potency           FRACTION, scales the ability's own
                                   stat_mods

KEPT MANDATORY: Holy Shock is the only unlock for paladin_holy_shock,
which is requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("paladin_holy", "Paladin Holy",
         "Healing light - sustained single-target restoration.")

# ----------------------------------------------------------------- tier 0
T.node("spiritual_focus", "Spiritual Focus",
       "Restores 5 mana every 5 seconds per rank.",
       0, -1, 5, effects={"mp5": 5},
       source="WotLK row 0: 'Reduces the pushback suffered from damaging "
              "attacks while casting Flash of Light and Holy Light by "
              "14%-70%.' DEPARTURE - there are no cast times in this "
              "engine, so there is no pushback to suffer or reduce. The "
              "talent exists so a healer keeps casting under pressure; "
              "delivered as mana regeneration, which is what keeps a healer "
              "casting here. Kept from the outgoing tree. mp5 is FLAT and "
              "lands on the attribute.")

T.node("seals_of_the_pure", "Seals of the Pure",
       "Increases the damage of your Seal of Righteousness by 3% per rank.",
       0, 1, 5,
       effects={"ability_paladin_seal_of_righteousness_potency": 0.03},
       source="WotLK row 0: 'Increases the damage done by your Seal of "
              "Righteousness, Seal of Vengeance and Seal of Corruption and "
              "their Judgement effects by 3%-15%.' Only Seal of "
              "Righteousness exists here. Built at the real 3% per rank. "
              "ability_<id>_potency scales the ability's own stat_mods, "
              "which is the right key for a seal. The outgoing version was "
              "a proc with an empty effects dict.")

# ----------------------------------------------------------------- tier 1
T.node("healing_light", "Healing Light",
       "Increases the healing of your Holy Light, Flash of Light and Holy "
       "Shock by 4% per rank.",
       1, -5, 3,
       effects={"ability_paladin_holy_light_healing": 0.04,
                "ability_paladin_flash_of_light_healing": 0.04,
                "ability_paladin_holy_shock_healing": 0.04},
       connected_to=["spiritual_focus"],
       source="WotLK row 1, built verbatim across all three real spells: "
              "'Increases the amount healed by your Holy Light, Flash of "
              "Light and the effectiveness of Holy Shock spells by "
              "4%/8%/12%.' USES _healing, NOT _damage - a heal's "
              "per-ability key is ability_<id>_healing, and 18 talents "
              "across four classes shipped silently dead using _damage on "
              "a heal. The outgoing version covered two of the three at 8% "
              "per rank.")

T.node("aura_mastery", "Aura Mastery",
       "Reduces magic damage taken by 4%.",
       1, -3, 1, effects={"magic_damage_taken_pct": -0.04},
       connected_to=["spiritual_focus"],
       source="WotLK row 1: 'Causes your Concentration Aura to make all "
              "affected targets immune to Silence and Interrupt effects and "
              "improve the effect of all other auras by 100%. Lasts 6 sec.' "
              "DEPARTURE - there is no aura system, no silence and no "
              "interrupt key. What survives is magical protection for the "
              "paladin. Kept from the outgoing tree. "
              "magic_damage_taken_pct is a FRACTION as a talent effect and "
              "NEGATIVE reduces, which is the opposite sign to its meaning "
              "inside a status effect.")

T.node("divine_intellect", "Divine Intellect",
       "Increases your Intellect by 2% per rank.",
       1, -1, 5, effects={"intellect_pct": 2.0},
       connected_to=["seals_of_the_pure"],
       source="WotLK row 1: 'Increases your total Intellect by 2%-10%.' "
              "Built verbatim and kept from the outgoing tree. "
              "intellect_pct is PERCENTAGE POINTS, read off the `bonuses` "
              "dict and divided by 100 - the probe finds no literal read "
              "site for it and it is nonetheless live. This node feeds Holy "
              "Guidance at tier 4.")

T.node("illumination", "Illumination",
       "Your critical heals have a 20% chance per rank to restore 150 mana.",
       1, 1, 5,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 150}},
       connected_to=["seals_of_the_pure"],
       source="WotLK row 1: 'After getting a critical effect from your Flash "
              "of Light, Holy Light, or Holy Shock heal spell you have a "
              "20%-100% chance to gain mana equal to 30% of the base cost "
              "of the spell.' Built as the real mechanic with the real "
              "chance curve. Mana-as-a-percentage-of-the-spell's-cost is "
              "not available to a proc payload - grant_resource takes a "
              "FLAT amount, with no pct_max - so 150 is a fixed return. "
              "on_crit is not restricted to heals by an ability_filter "
              "because listing the three heals would exclude Holy Shock's "
              "damage mode, which the real talent also counts. Kept as a "
              "proc from the outgoing tree.")

T.node("unyielding_faith", "Unyielding Faith",
       "Reduces the duration of Stun effects against you by 15% per rank.",
       1, 3, 2, effects={"stun_duration_reduction_pct": 0.15},
       connected_to=["divine_intellect"],
       source="WotLK row 1, NEW to our tree: 'Reduces the duration of all "
              "Fear and Disorient effects by 15%/30%.' DEPARTURE - there is "
              "no Fear and no Disorient; is_stun is this engine's only "
              "incapacitate, so the reduction applies to that instead. "
              "stun_duration_reduction_pct is a FRACTION, not points, and "
              "it floors a stun at 1 turn so it can shorten but never "
              "negate.")

T.node("improved_lay_on_hands", "Improved Lay on Hands",
       "Reduces the cooldown of your Lay on Hands by 3 turns per rank.",
       1, 5, 2,
       effects={"ability_paladin_lay_on_hands_cooldown": 3},
       connected_to=["illumination"],
       source="WotLK row 1: 'Grants the target of your Lay on Hands spell "
              "10%/20% reduced physical damage taken for 15 sec. In "
              "addition, the cooldown for your Lay on Hands spell is "
              "reduced by 2/4 min.' The cooldown half is built - "
              "ability_<id>_cooldown is FLAT turns. The damage-reduction "
              "half cannot be built: a talent effect can never reach an "
              "ally, and nothing lets a talent attach a rider to an "
              "ability's cast. Kept from the outgoing tree.")

# ----------------------------------------------------------------- tier 2
T.node("improved_concentration_aura", "Improved Concentration Aura",
       "Reduces magic damage taken by 2% per rank.",
       2, -5, 3, effects={"magic_damage_taken_pct": -0.02},
       connected_to=["healing_light"],
       source="WotLK row 2: 'Increases the effect of your Concentration "
              "Aura by an additional 5%-15% and while any Aura is active "
              "reduces the duration of any Silence or Interrupt effect used "
              "against you by 50%.' DEPARTURE - no aura system, no silence, "
              "no interrupt. Stacks with Aura Mastery one row above, as the "
              "real pair does through the aura it improves. The outgoing "
              "version was stun_duration_reduction_pct, which is Unyielding "
              "Faith's job in the real tree.")

T.node("pure_of_heart", "Pure of Heart",
       "Increases all healing you receive by 5% per rank.",
       2, -3, 2, effects={"healing_taken_pct": 0.05},
       connected_to=["aura_mastery"],
       source="WotLK row 2: 'Reduces the duration of Curse, Disease and "
              "Poison effects by 15%/30%.' DEPARTURE - nothing modifies an "
              "incoming effect's duration by dispel school; dispel_type "
              "marks what CAN be removed and no key shortens it. The talent "
              "is about shrugging off what lands on you, delivered as "
              "healing received. The outgoing version was "
              "magic_damage_taken_pct, duplicating two other nodes in the "
              "same tree.")

T.node("divine_favor", "Divine Favor",
       "Increases your spell critical strike chance by 5%.",
       2, -1, 1, effects={"crit_chance_spell": 5.0},
       connected_to=["divine_intellect"],
       source="WotLK row 2: 'When activated, gives your next Flash of "
              "Light, Holy Light, or Holy Shock spell a 100% critical "
              "effect chance.' DEPARTURE - there is no guaranteed-crit key "
              "and no ability to unlock, and nothing consumes a buff on "
              "use. Delivered as a flat crit chance. Kept from the outgoing "
              "tree. The real talent requires Illumination and is Holy "
              "Shock's prerequisite; connected_to keeps it upstream of Holy "
              "Shock below. crit_chance_spell is PERCENTAGE POINTS.")

T.node("improved_blessing_of_wisdom", "Improved Blessing of Wisdom",
       "Increases the effect of your Blessing of Wisdom by 10% per rank.",
       2, 1, 2,
       effects={"ability_paladin_blessing_of_wisdom_potency": 0.10},
       connected_to=["illumination"],
       source="WotLK row 2, NEW to our tree, built verbatim: 'Increases the "
              "effect of your Blessing of Wisdom spell by 10%/20%.'")

T.node("sanctified_light", "Sanctified Light",
       "Increases the critical chance of your Holy Light and Holy Shock by "
       "2% per rank.",
       2, 3, 3,
       effects={"ability_paladin_holy_light_crit": 2.0,
                "ability_paladin_holy_shock_crit": 2.0},
       connected_to=["improved_lay_on_hands"],
       source="WotLK row 2, built verbatim across both real spells: "
              "'Increases the critical effect chance of your Holy Light and "
              "Holy Shock spells by 2%/4%/6%.' The outgoing version was 4% "
              "per rank on Holy Light alone. ability_<id>_crit is "
              "PERCENTAGE POINTS.")

T.node("blessed_hands", "Blessed Hands",
       "Reduces the mana cost of your Cleanse by 10 per rank.",
       2, 5, 2, effects={"ability_paladin_cleanse_cost": 10},
       connected_to=["improved_lay_on_hands"],
       source="WotLK row 2: 'Reduces the mana cost of Hand of Freedom, Hand "
              "of Sacrifice and Hand of Salvation by 15%/30%...' DEPARTURE "
              "- none of the three Hand spells exist here. Cleanse is the "
              "paladin's remaining utility spell, so the cost cut lands "
              "there. Kept from the outgoing tree. ability_<id>_cost is "
              "FLAT.")

# ----------------------------------------------------------------- tier 3
T.node("purifying_power", "Purifying Power",
       "Reduces the mana cost of your Cleanse and Consecration by 5% per "
       "rank and the cooldown of your Exorcism by 1 turn per rank.",
       3, -1, 2,
       effects={"ability_paladin_cleanse_cost_pct": 0.05,
                "ability_paladin_consecration_cost_pct": 0.05,
                "ability_paladin_exorcism_cooldown": 1},
       connected_to=["divine_favor"],
       source="WotLK row 3, built verbatim: 'Reduces the mana cost of your "
              "Cleanse, Purify and Consecration spells by 5%/10% and "
              "reduces the cooldown of your Exorcism and Holy Wrath spells "
              "by 16%/33%.' Purify and Holy Wrath do not exist; the rest is "
              "real. _cost_pct is a FRACTION where POSITIVE MEANS A "
              "REDUCTION. The outgoing version was Holy Shock damage, which "
              "is nothing to do with this talent.")

T.node("holy_power", "Holy Power",
       "Increases your spell critical strike chance by 1% per rank.",
       3, 1, 5, effects={"crit_chance_spell": 1.0},
       connected_to=["sanctified_light"],
       source="WotLK row 3: 'Increases the critical effect chance of your "
              "Holy spells by 1%-5%.' Built verbatim - scoping crit to one "
              "school is not available (crit_chance_spell covers all "
              "spells), and every Paladin spell here is Holy anyway, so the "
              "distinction is academic for this class. The outgoing version "
              "was per-ability healing, duplicating Healing Light.")

# ----------------------------------------------------------------- tier 4
T.node("lights_grace", "Light's Grace",
       "Reduces the mana cost of your Holy Light by 5 per rank.",
       4, -5, 3, effects={"ability_paladin_holy_light_cost": 5},
       connected_to=["purifying_power"],
       source="WotLK row 4: 'Gives your Holy Light spell a 33%-100% chance "
              "to reduce the cast time of your next Holy Light spell by 0.5 "
              "sec.' DEPARTURE - there are no cast times. The talent exists "
              "to make Holy Light cheaper to chain; delivered as mana cost. "
              "Kept from the outgoing tree.")

T.node("sacred_cleansing", "Sacred Cleansing",
       "Your Cleanse has a 30% chance per rank to shield the target against "
       "magic for 3 turns.",
       4, -3, 3,
       proc={"trigger": "on_cast", "chance": 30, "icd": 0,
             "ability_filter": ["paladin_cleanse"],
             "apply_effect": {"effect_id": "sacred_cleansing",
                              "name": "Sacred Cleansing",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"magic_damage_taken_pct": -10.0},
                              "on_target": False}},
       connected_to=["purifying_power"],
       source="WotLK row 4: 'Your Cleanse spell has a 10%/20%/30% chance to "
              "increase the target's resistance to Disease, Magic and Poison "
              "by 30% for 10 sec.' Built as the real mechanic with the real "
              "chance and the real 10 seconds (3 turns). Per-school dispel "
              "resistances do not exist, so it becomes magic damage "
              "reduction. MIND THE SIGN AND UNIT: inside a status effect "
              "magic_damage_taken_pct is PERCENTAGE POINTS (so -10.0 is "
              "-10%), the opposite convention to the same key as a talent "
              "effect, where it is a fraction. on_target is False because a "
              "talent-sourced effect cannot be aimed at the Cleanse's "
              "target. The outgoing version was flat healing_done.")

T.node("holy_shock", "Holy Shock",
       "Teaches Holy Shock, striking an enemy or mending an ally with raw "
       "Light.",
       4, -1, 1, node_type="active",
       effects={"unlock_ability": "paladin_holy_shock"},
       connected_to=["divine_favor"],
       source="WotLK row 4, kept - the ONLY unlock for paladin_holy_shock, "
              "which is requires_talent. The real talent requires Divine "
              "Favor, which connected_to reproduces.")

T.node("blessed_life", "Blessed Life",
       "Reduces all damage you take by 2% per rank.",
       4, 1, 3, effects={"damage_taken_pct": -0.02},
       connected_to=["holy_power"],
       source="WotLK row 4, NEW to our tree: 'All attacks against you have "
              "a 4%/7%/10% chance to cause half damage.' DEPARTURE - a proc "
              "on on_damage_taken fires AFTER the hit resolves and cannot "
              "reduce the damage that triggered it, so a chance-to-halve "
              "cannot be built. Delivered as a smaller permanent reduction, "
              "which is the same expected value shape without the variance. "
              "damage_taken_pct is read RAW on both sides.")

T.node("holy_guidance", "Holy Guidance",
       "Increases your spell power by 4% of your Intellect per rank.",
       4, 3, 5,
       effects={"spell_power_from_intellect_pct": 0.04},
       connected_to=["holy_power"],
       source="WotLK row 4, NEW to our tree, built verbatim: 'Increases "
              "your spell power by 4%-20% of your total Intellect.' This is "
              "a real STAT CONVERSION - spell_power is a valid target and "
              "intellect a valid source. THE UNIT IS A TRAP: the key is "
              "read as `gained = source * pct` (character.py:1551), so it "
              "is a RAW MULTIPLIER and not a percentage. Authoring 20 would "
              "have granted twenty times the paladin's Intellect; measured "
              "live, 50 gave +2400 spell power off 48 Intellect. 0.04 per "
              "rank reaches the real 20%. Pairs with Divine Intellect two "
              "tiers up, exactly as the real tree intends.")

# ----------------------------------------------------------------- tier 5
T.node("divine_illumination", "Divine Illumination",
       "Reduces the mana cost of all your abilities by 10%.",
       5, -3, 1, effects={"all_ability_cost_pct": 0.10},
       connected_to=["sacred_cleansing"],
       source="WotLK row 5: 'Reduces the mana cost of all spells by 50% for "
              "15 sec.' DEPARTURE - there is no ability to unlock and no "
              "way to grant a temporary global cost reduction from a "
              "talent. Delivered as a permanent but much smaller cut. MIND "
              "THE KEY: all_ability_cost_pct is a FRACTION as a talent "
              "effect where POSITIVE MEANS A REDUCTION, and it FLIPS to "
              "percentage POINTS inside a status effect - audit_talents has "
              "caught that flip being got wrong in this project before. "
              "The outgoing version was a proc.")

T.node("infusion_of_light", "Infusion of Light",
       "Your Holy Shock critical hits increase the critical chance of your "
       "next heals by 20% for 2 turns.",
       5, -1, 2,
       proc={"trigger": "on_crit", "chance": 50, "icd": 0,
             "ability_filter": ["paladin_holy_shock"],
             "apply_effect": {"effect_id": "infusion_of_light",
                              "name": "Infusion of Light",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"crit_chance_spell": 20},
                              "on_target": False}},
       connected_to=["holy_shock"],
       source="WotLK row 5: 'Your Holy Shock critical hits reduce the cast "
              "time of your next Flash of Light by 0.75/1.5 sec or increase "
              "the critical chance of your next Holy Light by 10%/20%.' The "
              "SECOND clause is real and buildable, so that is the one "
              "built, at the real 20%; the cast-time clause has nothing to "
              "act on. ability_filter on Holy Shock is exact. 'Next spell' "
              "becomes a 2-turn window, since nothing consumes a buff on "
              "use. The real talent requires Holy Shock, reproduced. Kept "
              "as a proc from the outgoing tree.")

T.node("judgements_of_the_pure", "Judgements of the Pure",
       "Increases the damage of your Judgement by 5% per rank, and casting "
       "it quickens you by 15% for 3 turns.",
       5, 1, 5,
       effects={"ability_paladin_judgement_damage": 0.05},
       proc={"trigger": "on_cast", "chance": 100, "icd": 0,
             "ability_filter": ["paladin_judgement"],
             "apply_effect": {"effect_id": "judgements_of_the_pure",
                              "name": "Judgements of the Pure",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"haste": 15},
                              "on_target": False}},
       connected_to=["holy_guidance"],
       source="WotLK row 5, built with BOTH halves - a node may carry "
              "effects AND a proc: 'Increases the damage done by your Seal "
              "and Judgement spells by 5%-25%, and your Judgement spells "
              "increase your casting and melee haste by 15% for 1 min.' The "
              "real 5% per rank and the real 15% haste. 1 minute becomes 3 "
              "turns. The Seal half is covered by Seals of the Pure at tier "
              "0. The outgoing version was a proc with an empty effects "
              "dict.")

T.node("enlightened_judgements", "Enlightened Judgements",
       "Increases your chance to hit by 2% per rank.",
       5, 3, 2, effects={"hit_rating": 2.0},
       connected_to=["holy_guidance"],
       source="WotLK row 5: 'Increases the range of your Judgement of Light "
              "and Judgement of Wisdom spells by 10/30 yards and increases "
              "your chance to hit by 2%/4%.' The hit half is built verbatim "
              "- range does not exist. hit_rating is PERCENTAGE POINTS and "
              "is NOT a valid STAT_CONVERSION_TARGET, so it can be granted "
              "directly like this but never converted into. The outgoing "
              "version was Judgement damage, which is Judgements of the "
              "Pure's job.")

# ----------------------------------------------------------------- tier 6
T.node("beacon_of_light", "Beacon of Light",
       "Your heals spill over, mending your neediest ally as well.",
       6, 1, 1,
       proc={"trigger": "on_heal_cast", "chance": 100, "icd": 1,
             "smart_heal": 80},
       connected_to=["judgements_of_the_pure"],
       source="WotLK row 10, the capstone: 'The target becomes a Beacon of "
              "Light... Any heals you cast on party or raid members will "
              "also heal the Beacon for the same amount.' DEPARTURE - a "
              "talent cannot designate an ally as a target, and there is no "
              "heal-mirroring mechanic. smart_heal is the engine's real "
              "'heal whoever needs it most' payload, so the capstone "
              "becomes a second, automatic heal on every cast - which is "
              "the real talent's EFFECT (one cast, two targets healed) "
              "reached from the other direction. icd 1 keeps it to once a "
              "turn. Kept as a proc from the outgoing tree.")


def main():
    return T.write(was="23 nodes, 66 points - 6 proc, 8 ability-scoped, "
                       "8 flat stat, 1 unlock")


if __name__ == "__main__":
    sys.exit(main())
