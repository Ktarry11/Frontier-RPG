#!/usr/bin/env python3
"""Rebuild Witch Doctor's Brewing tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_witch_doctor_brewing.py [--check]

SOURCE: data/reference/coa_worksheets/witch-doctor.md and
data/reference/coa/witch-doctor.json - 37 real Brewing talents from
Ascension's own CoA Builder payload. Role: Healer.
coa_playstyles.json: "Primarily Restoration Shaman, with Mistweaver Monk
and a touch of Warlock".

The shipped tree was 23 nodes with FOUR procs and most of the rest bare
numbers.

WHAT THE SPEC IS, AND WHAT CANNOT BE BUILT. Brewing is a LOADOUT spec.
CoA's Witch Doctor brews Ingredients into a Cauldron, and the Cauldron's
contents decide what Potion Toss does when thrown; a Base occupies a
second slot, one at a time; Mojo talents swap the loaded pair outright.
None of that exists here - there is no mode or loadout state a talent can
read or set, no ground-placed object with a radius, and no "while a Base
is active" gate.

What saves the spec is that Frontier already has the Ingredients, both
Bases, Voodoo Cauldron, Tiki Splash, Master Mixologist, Potion Toss,
Splash Potion and Mojo Beam as real castable party abilities. So each
brew is a thing you cast rather than a thing you load, and the talents
that buff a named brew port cleanly as ability_* keys. The ones that
rewrite what another ability turns into (the three Mojo talents, Tiki
Splash, Unstable Concoction) do not, and each says so on its node.

SPIRIT HEALER PORTS WHOLE, which is rare. healing_power and
crit_chance_spell are both in STAT_CONVERSION_TARGETS and spirit is in
STAT_CONVERSION_SOURCES, so both halves of CoA's level 20 passive are
real. This is the same Spirit theme Voodoo converts into spell damage.

CONVENTIONS, which do not agree with each other - and the two that matter
most here sit twelve lines apart in entities/character.py:
  healing_power_pct     percentage POINTS  (character.py:1295, /100)
  max_mana_pct          FRACTION           (character.py:1419, raw)
  spirit_pct, intellect_pct                percentage POINTS
  crit_chance_spell, haste, hit_rating     PERCENT
  healing_done_pct / damage_taken_pct inside a status effect   POINTS
  splash_heal, shield_pct, leech_pct       FRACTION
  smart_heal_pct                           PERCENT
  ability_*_healing, ability_*_crit_damage FRACTION
  ability_*_crit                           PERCENT
  *_cost_pct / *_cooldown_pct   FRACTION, POSITIVE MEANS A REDUCTION
  <target>_from_<source>_pct    FRACTION, listed pairs only

TURN-BASED CUTS. Every cast time, which takes Brewmaster and Sen'jin's
Presence as written, and every yard and radius, which is most of what a
Cauldron is. Channelling (Mojo Beam, Master Mixologist's cast-while-
moving) has no equivalent. "Ticks N sec faster" (Doctor of the Jungle)
has no meaning per-turn.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/witch_doctor_brewing.json"

#: The spec's direct heals.
HEALS = ["witch_doctor_loas_brew", "witch_doctor_potion_toss",
         "witch_doctor_splash_potion", "witch_doctor_mojo_beam"]

#: The three Ingredients, which Frontier has as castable party abilities
#: rather than as a loadout.
INGREDIENTS = ["witch_doctor_ingredient_jungle_shrooms",
               "witch_doctor_ingredient_frog_bones",
               "witch_doctor_ingredient_bloodthistle"]

TREE = {
    "spec_name": "Witch Doctor Brewing",
    "tree_id": "witch_doctor_brewing",
    "description": ("Cauldrons and concoctions - a healer who throws "
                    "potions and turns Spirit into healing power."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 37 real CoA Brewing talents (role "
        "Healer, 'Primarily Restoration Shaman, with Mistweaver Monk and a "
        "touch of Warlock'). Replaces a 23-node tree with 4 procs. Brewing "
        "is a LOADOUT spec in CoA - Ingredients brewed into a Cauldron "
        "decide what Potion Toss does - and this engine has no mode state a "
        "talent can read or set, no ground-placed object with a radius, and "
        "no party aura. Frontier already has every brew as a castable party "
        "ability, so talents that buff a named brew port cleanly; the three "
        "Mojo swaps, Tiki Splash and Unstable Concoction do not and say so "
        "per node. Spirit Healer ports whole - both conversions are legal "
        "pairs."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"witch_doctor_brewing_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"witch_doctor_brewing_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "spirit_healer", "Spirit Healer",
    "Increases your healing power by 25% of your Spirit and your spell "
    "critical strike chance by 10% of your Spirit.",
    0, -5,
    effects={"healing_power_from_spirit_pct": 0.25,
             "crit_chance_spell_from_spirit_pct": 0.10},
    connect=["potent_mixes"],
    source="CoA verbatim: 'Level 20 Passive. Increases healing power by 25% "
           "of Spirit and increases spell critical strike chance by 10% of "
           "Spirit.' PORTS WHOLE, which is rare for a conversion node - "
           "healing_power AND crit_chance_spell are both in "
           "STAT_CONVERSION_TARGETS and spirit is in "
           "STAT_CONVERSION_SOURCES. Compare Voodoo Power on the DPS tree, "
           "whose spell-hit half had to be dropped because hit_rating is not "
           "a target. Both are FRACTIONS."))

N.append(node(
    "potent_mixes", "Potent Mixes",
    "Increases your healing done by 8% and reduces the threat your spells "
    "generate by 15%.",
    0, -3,
    effects={"healing_power_pct": 8.0, "threat_generation_pct": -0.15},
    connect=["mixologist"],
    source="CoA over 2 ranks: 'Increases your healing done by 4% and reduces "
           "the threat generated by your spells by -15%.' Doubled for the two "
           "ranks and authored as the full-investment ceiling. NOTE the two "
           "keys here take different units and are read twelve lines apart in "
           "entities/character.py - healing_power_pct is divided by 100 "
           "(line 1295) so 8.0 is 8%, while threat_generation_pct is a raw "
           "FRACTION where negative reduces."))

N.append(node(
    "mojo_addiction", "Mojo Addiction",
    "Increases your maximum mana by 10%.",
    0, -1,
    effects={"max_mana_pct": 0.10},
    connect=["mixologist"],
    source="CoA over 2 ranks: 'Increases your maximum mana by 5%.' Doubled "
           "for the two ranks. max_mana_pct is a FRACTION - it is NOT "
           "divided by 100 (character.py:1419), unlike healing_power_pct "
           "on the node above it. 10.0 here would have been 1000% mana."))

N.append(node(
    "presence_of_the_loa", "Presence of the Loa",
    "Increases your spell critical strike chance by 4%.",
    0, 1,
    effects={"crit_chance_spell": 4.0},
    connect=["plentiful_potions"],
    source="CoA verbatim: 'Increases your critical strike chance by 4%.' "
           "Routed to the spell side, since every ability this spec casts is "
           "a spell. PERCENT."))

N.append(node(
    "fresh_ingredients", "Fresh Ingredients",
    "Increases the healing of Jungle Shrooms by 30%.",
    0, 3,
    effects={"ability_witch_doctor_ingredient_jungle_shrooms_healing": 0.30},
    connect=["plentiful_potions"],
    source="CoA over 2 ranks: 'Increases the healing of your Jungle Shrooms "
           "from your Cauldron by 15%.' Doubled for the two ranks. 'From your "
           "Cauldron' is the loadout distinction CoA draws between a brewed "
           "and a thrown Ingredient, and there is no loadout state here - "
           "Jungle Shrooms is simply a party ability you cast, so the bonus "
           "applies whenever you cast it."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "mixologist", "Mixologist",
    "Increases the healing of your Ingredients by 15%.",
    1, -4,
    effects={f"ability_{a}_healing": 0.15 for a in INGREDIENTS},
    connect=["splash_on_em"],
    source="CoA's own description for this node is the unresolved token "
           "'$40' - the Builder payload never expands it, so there is no "
           "verbatim text to port and this is NOT a faithful copy. Named for "
           "the spec's core skill and built as broad Ingredient "
           "effectiveness, which is what every other Mixologist-adjacent "
           "talent in the tree does (Potion Boss, Spice: Earthroot, Master "
           "Mixologist). Flagged so a later pass can correct it if the real "
           "text surfaces. All three Ingredients written out because no key "
           "names a group."))

N.append(node(
    "plentiful_potions", "Plentiful Potions",
    "Reduces the mana cost of Loa's Brew and Hexbreak by 10%.",
    1, -2,
    effects={"ability_witch_doctor_loas_brew_cost_pct": 0.10,
             "ability_witch_doctor_hexbreak_cost_pct": 0.10},
    connect=["potion_boss"],
    source="CoA verbatim: 'Reduces the cost of your Loa's Brew and Hexbreak "
           "by -10%.' Both abilities exist in Frontier. POSITIVE reduces, so "
           "CoA's minus sign is dropped - authoring -0.10 here would have "
           "RAISED the cost."))

N.append(node(
    "brewmaster", "Brewmaster",
    "Increases the healing of Loa's Brew by 16%.",
    1, 0,
    effects={"ability_witch_doctor_loas_brew_healing": 0.16},
    connect=["potion_boss"],
    source="CoA over 2 ranks: 'Reduces the cast time of Loa's Brew by 0.25 "
           "sec.' There are no cast times here, so nothing of this talent "
           "survives as written. Rerouted to the healing of the same "
           "ability, which is what a faster cast buys - more Loa's Brew "
           "throughput."))

N.append(node(
    "spice_earthroot", "Spice: Earthroot",
    "Increases the healing of your Ingredients and the Voodoo Cauldron by "
    "30%.",
    1, 2,
    effects={**{f"ability_{a}_healing": 0.30 for a in INGREDIENTS},
             "ability_witch_doctor_voodoo_cauldron_healing": 0.30},
    connect=["jungle_secrets"],
    source="CoA verbatim: 'Infuse your Cauldron with Spice: Earthbloom. "
           "Increases effectiveness of all Cauldron effects and Ingredients "
           "by 30%.' CoA's 30% kept. 'Cauldron effects' is read as the "
           "Voodoo Cauldron ability, the only Cauldron Frontier actually has "
           "as a thing you cast. Note CoA's own text disagrees with its node "
           "name - Earthroot in the title, Earthbloom in the body; the title "
           "is kept."))

N.append(node(
    "disciple_of_sseratus", "Disciple of Sseratus",
    "Increases the healing of Loa's Brew and Spirit in a Bottle by 15%.",
    1, 4,
    effects={"ability_witch_doctor_loas_brew_healing": 0.15,
             "ability_witch_doctor_spirit_in_a_bottle_healing": 0.15},
    connect=["jungle_secrets"],
    source="CoA verbatim: 'Increases the bonus healing scaling of Loa's Brew "
           "and Spirit in a Bottle by 15%.' There is no key for how much an "
           "ability scales with healing power - the coefficients live on the "
           "abilities - so it is expressed as healing, which is what the "
           "scaling buys. Spirit in a Bottle is an enemy-target ability in "
           "Frontier that heals on hit, so the key is still live."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "potion_boss", "Potion Boss",
    "Increases the healing of Potion Toss and Splash Potion by 20%.",
    2, -4,
    effects={"ability_witch_doctor_potion_toss_healing": 0.20,
             "ability_witch_doctor_splash_potion_healing": 0.20},
    connect=["splash_on_em"],
    source="CoA verbatim: 'Increases the effectiveness of Potion Toss and "
           "your tossed Ingredients by 20%.' Splash Potion stands in for "
           "'tossed Ingredients', since a thrown Ingredient is not a "
           "separate thing here - there is no loadout, so an Ingredient is "
           "only ever cast directly."))

N.append(node(
    "splash_on_em", "Splash On 'Em",
    "Your heals bring Potion Toss and Splash Potion a turn closer to ready.",
    2, -2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_loas_brew",
                             "witch_doctor_mojo_beam"],
          "reset_cooldown": {"abilities": ["witch_doctor_potion_toss",
                                           "witch_doctor_splash_potion"],
                             "turns": 1}},
    connect=["unstable_concoction"],
    source="CoA verbatim: 'Effective healing done by Loa's Brew and Mojo "
           "Beam reduce the cooldown of Potion Toss and Splash Potion by 1 "
           "sec.' Ports almost exactly - on_heal_cast is the right trigger "
           "and both target abilities exist. 1 sec becomes 1 turn, which is "
           "a buff relative to CoA, because a turn is roughly three seconds "
           "and a fraction of a turn cannot be expressed."))

N.append(node(
    "touch_of_the_spirits", "Touch of the Spirits",
    "Spirit in a Bottle leaves the enemy taking 3% more damage and dealing "
    "3% less for 5 turns.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_spirit_in_a_bottle"],
          "apply_effect": {"effect_id": "witch_doctor_touch_of_the_spirits",
                           "name": "Touch of the Spirits",
                           "effect_type": "debuff", "duration": 5,
                           "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": 0.03,
                                         "damage_dealt_pct": -3.0},
                           "on_target": True}},
    connect=["unstable_concoction"],
    source="CoA verbatim: 'Damage dealt by Spirit In a Bottle causes the "
           "enemies to take 3% more damage and deal -3% less damage for 15 "
           "sec.' Both halves live and 15 sec is 5 turns. THE TWO KEYS TAKE "
           "DIFFERENT UNITS INSIDE THE SAME STATUS EFFECT: bare "
           "damage_taken_pct is read RAW, so 3% is 0.03, while "
           "damage_dealt_pct is percentage POINTS, so -3% is -3.0. Authoring "
           "damage_taken_pct as 3.0 would mean 300% extra damage taken - the "
           "same key that produced immortality on Boltslinger's Evasive when "
           "it was authored at -20.0."))

N.append(node(
    "spice_peacebloom", "Spice: Peacebloom",
    "Reduces the duration of stuns against you by 25%.",
    2, 2,
    effects={"stun_duration_reduction_pct": 0.25},
    connect=["jungle_secrets"],
    source="CoA verbatim: 'Infuse your Cauldron with Spice: Peacebloom. "
           "Reduces the duration of roots, stuns, and snares against allies "
           "within 40 yds by -25%.' There is no party-aura mechanism, so the "
           "reduction lands on the Witch Doctor and the description says "
           "'you' rather than promising an aura the engine will not deliver. "
           "Roots and snares are dropped from the description because the "
           "only key that exists, stun_duration_reduction_pct, is read "
           "solely against effects flagged is_stun "
           "(status_effects.py:699) - promising roots and snares would be "
           "text with no mechanic behind it. It is a FRACTION where POSITIVE "
           "reduces, floored so a stun can be shortened but never negated. "
           "CoA's 25% kept. My first draft invented 'cc_duration_taken_pct', "
           "which no engine code reads - caught by audit_talents."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "jungle_secrets", "Jungle Secrets",
    "Loa's Brew splashes 35% of its healing onto the worst-off ally.",
    3, -4,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_loas_brew"],
          "splash_heal": {"pct": 0.35, "max_targets": 1}},
    connect=["jungle_booms"],
    source="CoA verbatim: 'When you heal with Loa's Brew your Effigies will "
           "now heal an additional ally within 20 yds for 35% of the healing "
           "done, prioritizing allies with low health.' Ports closely - "
           "splash_heal already prioritises the worst-off ally, which is "
           "exactly CoA's rule, and 35% and one extra target are CoA's "
           "numbers. The Effigy doing the healing is flavour; nothing here "
           "lets a summon carry a heal."))

N.append(node(
    "unstable_concoction", "Unstable Concoction",
    "Potion Toss splashes 40% of its healing across up to 3 nearby allies.",
    3, -2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_potion_toss"],
          "splash_heal": {"pct": 0.40, "max_targets": 3}},
    connect=["voodoo_cauldron_mastery"],
    source="CoA: 'Potion Toss now applies Unstable Concoction to the target "
           "for 20 seconds. Using Loa's Brew or Spirit in a Bottle on the "
           "target will trigger an explosion of mojo around the target, "
           "healing nearby allies within 20 yds for 177 + 40% healing.' A "
           "DELAYED DETONATION keyed on a second ability hitting the same "
           "target, which needs two things the engine lacks: nothing reads "
           "whether a target carries a debuff, and no payload fires on a "
           "later specific cast. Built as an immediate splash off Potion "
           "Toss at CoA's 40%, so the healing lands without the setup step."))

N.append(node(
    "master_of_concoctions", "Master of Concoctions",
    "Jungle Shrooms and Frog Bones last 1 turn longer, and your Ingredients "
    "heal 20% more.",
    3, 0,
    effects={"ability_witch_doctor_ingredient_jungle_shrooms_duration": 1,
             "ability_witch_doctor_ingredient_frog_bones_duration": 1,
             **{f"ability_{a}_healing": 0.20 for a in INGREDIENTS}},
    connect=["voodoo_cauldron_mastery"],
    source="CoA: 'Increases the duration of Ingredients by 20% and causes "
           "allies affected by Jungle Shrooms to heal for 5% of the damage "
           "they deal with their next 3 offensive abilities or spells for 15 "
           "sec.' The leech-on-allies half would need a party-wide applied "
           "buff with a charge counter, and neither the aura nor the charges "
           "exist. The duration half is built as a flat turn on the two "
           "Ingredients that have one, plus the 20% as effectiveness. NOTE "
           "the small integer durations keep this node out of the rank "
           "policy's reach - see tools/talent_ranks.rankable()."))

N.append(node(
    "doctor_of_the_jungle", "Doctor of the Jungle",
    "Increases the healing of Jungle Shrooms by 25%.",
    3, 2,
    effects={"ability_witch_doctor_ingredient_jungle_shrooms_healing": 0.25},
    connect=["mojo_wave"],
    source="CoA: 'Jungle Shrooms used from your Cauldron now ticks -2 sec "
           "faster.' A faster tick has no meaning when ticks are per-turn, "
           "so it is rerouted to healing, which is what a faster tick "
           "delivers - more healing in the same window."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "jungle_booms", "Jungle Booms",
    "Jungle Shrooms heal 100% more.",
    4, -3,
    effects={"ability_witch_doctor_ingredient_jungle_shrooms_healing": 1.00},
    connect=["voodoo_cauldron_mastery"],
    source="CoA verbatim: 'Jungle Shrooms used from your Cauldron now heal "
           "for 100% more, but heals 3 less targets.' CoA's 100% kept and "
           "THE DOWNSIDE IS DROPPED, because no key removes targets from an "
           "ability - the same wall that stops a key from adding them. So "
           "this node is strictly stronger than CoA's, which is noted rather "
           "than hidden: a single-target trade is the whole point of CoA's "
           "version and it cannot be expressed. Priced at one rank at tier 4 "
           "to keep it honest."))

N.append(node(
    "mojo_wave", "Mojo Wave",
    "Mojo Beam reaches further, splashing 75% of its healing across up to 3 "
    "of the worst-off allies.",
    4, -1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_mojo_beam"],
          "splash_heal": {"pct": 0.75, "max_targets": 3}},
    connect=["voodoo_cauldron_mastery"],
    source="CoA's level 40 passive: 'Healing with Mojo Beam now heals up to 3 "
           "of the lowest health nearby allies for 75% of the healing done "
           "and casting it grants allies Replenishment. Replenishment "
           "Replenishes 5% of maximum mana per 5 sec for 15 seconds.' The "
           "splash half ports exactly - 75%, 3 targets, worst-off first, all "
           "CoA's. Replenishment is dropped: there is no per-turn mana "
           "regeneration key and no party aura. Frontier has Mojo Beam as an "
           "ability already, so this is not its unlock."))

N.append(node(
    "base_crystal_water", "Base: Crystal Water",
    "Your heals shield the target for 20% of the healing done.",
    4, 1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": HEALS,
          "shield_pct": 0.20},
    connect=["loas_blessing"],
    source="CoA verbatim: 'Infuse your Cauldron with Crystal Water for 10 "
           "sec, causing party and raid members within 40 yds to be shielded "
           "for 20% of their healing taken for 5 sec. Only 1 Base can be "
           "active at a time.' Frontier HAS Base: Crystal Water as a castable "
           "ability, so this talent is the passive version: CoA's 20% of "
           "healing as a shield, applied by your own heals rather than by a "
           "Cauldron with a radius, and permanently rather than in a "
           "10-second window. 'Only 1 Base at a time' has no state to "
           "enforce. shield_pct is a FRACTION."))

N.append(node(
    "base_beast_blood", "Base: Beast Blood",
    "Reduces the physical damage you take by 15%.",
    4, 3,
    effects={"physical_damage_taken_pct": -0.15},
    connect=["loas_blessing"],
    source="CoA verbatim: 'Infuse your Cauldron with Beast Blood for 10 sec, "
           "causing 15% of the direct Physical damage taken by party and raid "
           "members within 40 yds to instead be dealt over time.' Converting "
           "a hit into a dot on someone else is not a mechanic here - "
           "nothing redirects or defers incoming damage - and there is no "
           "party aura. Built as straight physical mitigation for the Witch "
           "Doctor at CoA's 15%, which is the survivability the talent buys. "
           "As a TALENT effect physical_damage_taken_pct is a fraction where "
           "NEGATIVE reduces; inside a status effect the same key is divided "
           "by 100 and positive increases."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "voodoo_cauldron_mastery", "Voodoo Cauldron",
    "Increases the healing the Voodoo Cauldron does by 50% and the healing "
    "you receive by 10%.",
    5, -3,
    effects={"ability_witch_doctor_voodoo_cauldron_healing": 0.50,
             "healing_taken_pct": 0.10},
    connect=["master_mixologist"],
    source="CoA verbatim: 'Place down a Voodoo Cauldron for 15 sec, "
           "increasing allies' healing received by 20% while near the "
           "cauldron. Allies within 15 yds are healed for 300+Heal*0.6 every "
           "1.5 sec for 15 sec.' Frontier has Voodoo Cauldron as a castable "
           "party ability, so this talent empowers it. The healing-received "
           "aura has no party mechanism, so half of CoA's 20% lands on the "
           "Witch Doctor alone. AS A TALENT EFFECT healing_taken_pct is a "
           "FRACTION, so 10% is 0.10 - inside a status effect the same key "
           "is percentage POINTS. Authoring 10.0 here would have been "
           "1000%, which is what shipped briefly on Bloodmage Eternal."))

N.append(node(
    "loas_blessing", "Loa's Blessing",
    "Your heals bless you with the Loa's favour, raising your haste by 3% "
    "and the healing you receive by 3% for 5 turns, stacking 3 times.",
    5, -1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_loas_brew"],
          "apply_effect": {"effect_id": "witch_doctor_loas_blessing",
                           "name": "Loa's Blessing", "effect_type": "buff",
                           "duration": 5, "max_stacks": 3,
                           "stat_mods": {"haste": 3.0,
                                         "healing_taken_pct": 3.0},
                           "on_target": False}},
    connect=["master_mixologist"],
    source="CoA's level 30 passive: 'Healing done by Loa's Brew now applies a "
           "RANDOM empowerment to the target ally. Ferocity of Bethekk "
           "increases melee, ranged and spell haste by 3%. Vitality of "
           "Sseratus healing received increased by 3%. Cunning of Quetz'lun "
           "critical strike...' A random pick from a table is not a payload - "
           "apply_effect takes one effect, or a list, but nothing chooses "
           "among them - so the buff grants two of CoA's three empowerments "
           "at once, at CoA's own 3% each, and lands on the caster because a "
           "proc buff cannot be sent to the heal's target. INSIDE A STATUS "
           "EFFECT healing_taken_pct is percentage POINTS, so 3% is 3.0 - "
           "the opposite unit to the same key on the node beside it."))

N.append(node(
    "senjins_presence", "Sen'jin's Presence",
    "Reduces the mana cost of Loa's Brew by 20%.",
    5, 1,
    effects={"ability_witch_doctor_loas_brew_cost_pct": 0.20},
    connect=["master_mixologist"],
    source="CoA: 'Casting Potion Toss and Spirit in a Bottle now reduce the "
           "cast time of your next 2 Loa's Brews by 20% for 10 sec.' Three "
           "things fail at once: no cast times, no charge counter, and no "
           "payload that discounts a later specific cast. Rerouted to a flat "
           "cost reduction on the same ability at CoA's 20%, which is the "
           "throughput the talent buys. POSITIVE reduces."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "master_mixologist", "Master Mixologist",
    "Your heals crit 10% more often and your Ingredients, Cauldron and "
    "potions all heal 40% more.",
    6, 0,
    effects={"crit_chance_spell": 10.0,
             "ability_witch_doctor_voodoo_cauldron_healing": 0.40,
             "ability_witch_doctor_potion_toss_healing": 0.40,
             "ability_witch_doctor_splash_potion_healing": 0.40,
             **{f"ability_{a}_healing": 0.40 for a in INGREDIENTS}},
    source="CoA: 'For 10 sec, the effectiveness of all Cauldron effects and "
           "Ingredients is increased by 100% and you can cast Spirit in a "
           "Bottle while moving.' Frontier HAS Master Mixologist as a "
           "castable self ability, so this talent is its passive half. "
           "Casting while moving is positional. CoA's 100% in a 10-second "
           "window on a 2-minute cooldown is priced at a permanent 40% plus "
           "crit - roughly the same throughput averaged out, and reachable "
           "every turn rather than once a fight. The three Mojo talents that "
           "would also have lived at this tier (Mojo: Fish Bones, Frog "
           "Shrooms, Jungle Thistle) are NOT built: each resets a cooldown "
           "and then swaps the loaded Ingredient pair, and there is no "
           "loadout state to swap. Tiki Splash is dropped for the same "
           "reason - it transforms one ability into another while a Base is "
           "active, and there is no 'while active' gate."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations.
from tools.talent_ranks import rankable, spread  # noqa: E402

for _n in TREE["nodes"]:
    if _n["max_points"] < 3 and _n["tier"] < 6 and rankable(_n):
        spread(_n, 3)

# Jungle Booms is deliberately single-rank: it keeps CoA's 100% while its
# downside (three fewer targets) cannot be expressed, so it stays expensive.
for _n in TREE["nodes"]:
    if _n["talent_id"].endswith("_jungle_booms"):
        _n["max_points"] = 1
        _n["effects"]["ability_witch_doctor_ingredient_jungle_shrooms_healing"] = 1.00


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    names = [n["name"] for n in TREE["nodes"]]
    assert len(names) == len(set(names)), "duplicate node NAME"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Witch Doctor Brewing: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
