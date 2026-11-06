#!/usr/bin/env python3
"""Rebuild Stormbringer's Wind tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_stormbringer_wind.py [--check]

SOURCE: data/reference/coa_worksheets/stormbringer.md and
data/reference/coa/stormbringer.json - 42 real Wind talents from
Ascension's own CoA Builder payload. Role: Support.

WHAT THE SPEC IS. An Air Elemental pet spec that buffs the party. Unlike
Guardian's Inspiration, this Support spec ALREADY HAS real party-targeted
abilities - Clear Skies, Tailwind, Aerodynamics, Kiss of the Clouds and
the three Call of the X buffs are all target_type "party", so they reach
every living ally. So the talents here empower real auras rather than
pretending to create them.

FIVE UNLOCK NODES ARE LOAD-BEARING. These Stormbringer abilities carry
requires_talent, so without their unlock node each is unobtainable
forever: clear_skies, tailwind, aerodynamics, kiss_of_the_clouds and
summon_air_elemental - the Air Elemental itself, which this entire spec
is built around. All five are preserved and main() asserts them.
(Dropping gated unlock nodes is how I stranded nine abilities earlier in
this audit; tools/qa_abilities_obtainable.py exists because of it.)
raging_zephyr is NOT gated, so the old tree's unlock node for it granted
an ability the character already had and did nothing - replaced with real
mechanics.

TEN OF COA'S WIND ABILITIES DO NOT EXIST HERE, which is the single
biggest constraint on this tree: Gale, Updraft, Windsurf, Wind Gate,
Unshackle, Flurry, Skyfall, Nimbus, Cloudburst and Body of Lightning. A
dozen talents name one of them. Each is re-pointed at the nearest real
ability and says so; nothing is authored against an id that does not
exist.

THE PET WALL, and this spec runs straight into it. Pets scale off exactly
three keys - pet_damage, pet_health, pet_armor - and PETS NEVER FIRE
PROCS (no fire_proc_trigger in entities/pet.py). Nor can a proc's
apply_effect land on a pet: it goes to the caster or the trigger's
target. And pet_haste is read by nothing. So Invigoration (a stacking pet
damage buff), Comforting Winds (pet haste), Unshackle (a pet transform),
Aeromancy and Enveloping Winds (the pet casting its own spells), Flurry
and Skyfall (commanding the pet) all lose their mechanism. Stormbringer
DOES have a real pet, so pet_damage/pet_health/pet_armor are live here -
unlike the Witch Doctor, where they were dead data (see
tools/qa_pet_keys.py).

CONVENTIONS, which do not agree with each other:
  intellect_pct, spirit_pct, armor_pct      percentage POINTS
  spell_damage, all_damage, dot_damage, pet_damage, pet_health,
    pet_armor, ability_*_damage, ability_*_healing   FRACTION
  crit_chance_spell, haste, hit_rating, ability_*_crit  PERCENT
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every cast time (Air Flow, Lexicon of Servitude), every
yard and all movement (Windrunner, Clearsky Pendant, Skyfall's speed
half, Wind Gate's teleport), charges (Gale, Evergale, Raging Zephyr's
recharge), and "tick rate" (Quickdraft).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/stormbringer_wind.json"

#: The party-wide buffs this spec actually owns, all target_type "party".
AURAS = ["stormbringer_clear_skies", "stormbringer_tailwind",
         "stormbringer_aerodynamics", "stormbringer_kiss_of_the_clouds"]

#: The spec's own nature damage, standing in for CoA's Gale and Updraft.
WINDS = ["stormbringer_freewind", "stormbringer_gust_of_wind",
         "stormbringer_razorwind"]
# Of the three Winds, only Freewind is a damage spell. Gust of Wind is a pure
# 'debuff' with no stat_mods, and Razorwind is a 'dispel' - neither deals
# damage nor can crit, so _damage and _crit keys naming them were SILENT DEAD
# DATA (caught 6 Nov 2026 by tools/qa_ability_scoped_fields.py). The two
# damage/crit nodes use this narrower list; cost and cooldown nodes keep WINDS,
# because all three really do cost mana and have cooldowns.
DAMAGING_WINDS = ["stormbringer_freewind"]

#: Abilities that bank Static, for the talents keyed on building it.
BUILDERS = ["stormbringer_shock", "stormbringer_electrocute",
            "stormbringer_freewind"]

TREE = {
    "spec_name": "Stormbringer Wind",
    "tree_id": "stormbringer_wind",
    "description": ("Air elemental and open sky - a support caster whose "
                    "winds carry the whole party."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 42 real CoA Wind talents (role "
        "Support). FIVE UNLOCK NODES ARE LOAD-BEARING and asserted in "
        "main(): clear_skies, tailwind, aerodynamics, kiss_of_the_clouds and "
        "summon_air_elemental all carry requires_talent. Unlike Guardian's "
        "Inspiration, this Support spec already had real party-targeted "
        "abilities, so the talents empower genuine auras. Ten CoA Wind "
        "abilities do not exist in Frontier (Gale, Updraft, Windsurf, Wind "
        "Gate, Unshackle, Flurry, Skyfall, Nimbus, Cloudburst, Body of "
        "Lightning) and a dozen talents name one of them, each re-pointed "
        "per node. Stormbringer HAS a pet, so pet_damage/pet_health/"
        "pet_armor are live - but pets never fire procs and no proc can "
        "apply an effect to a pet, which costs six talents their "
        "mechanism."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"stormbringer_wind_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"stormbringer_wind_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "clear_skies", "Clear Skies",
    "Teaches Clear Skies, a party-wide buff raising everyone's chance to hit.",
    0, -5,
    effects={"unlock_ability": "stormbringer_clear_skies"},
    connect=["power_the_elements"],
    source="CoA verbatim: 'Increases chance to hit with all spells and "
           "attacks by 1% for you and party and raid members. Does not stack "
           "with similar effects.' LOAD-BEARING UNLOCK: "
           "stormbringer_clear_skies carries requires_talent, so dropping "
           "this node makes it unobtainable forever. The ability is already "
           "target_type 'party', so it genuinely reaches every living ally - "
           "the aura CoA describes exists here, which is not true of "
           "Guardian Inspiration's."))

N.append(node(
    "power_the_elements", "Power the Elements",
    "Increases the damage your Air Elemental deals by 20% and your spell "
    "damage by 4%.",
    0, -3,
    effects={"pet_damage": 0.20, "spell_damage": 0.04},
    connect=["master_elementalist"],
    source="CoA over 2 ranks: 'Increases the damage dealt by your Air "
           "Elemental's spells by 10% and your Nature damage dealt by 2%.' "
           "Doubled for the two ranks. pet_damage is one of only three pet "
           "keys the engine reads and it IS live here, because Stormbringer "
           "really has a pet (summon_air_elemental). There is no per-school "
           "damage key, so the Nature half lands on spell_damage - the spec "
           "deals almost nothing else. Both are FRACTIONS."))

N.append(node(
    "master_elementalist", "Master Elementalist",
    "Increases the damage of Shock by 10% and Aeroblast by 20%.",
    0, -1,
    effects={"ability_stormbringer_shock_damage": 0.10,
             "ability_stormbringer_aeroblast_damage": 0.20},
    connect=["air_flow"],
    source="CoA verbatim: 'Increases the spell damage scaling of Shock by 10% "
           "and Aeroblast by 20%.' There is no key for how much an ability "
           "scales with spell power - the coefficients live on the abilities "
           "- so it is expressed as damage, which is what the scaling buys. "
           "Both abilities exist in Frontier."))

N.append(node(
    "air_flow", "Air Flow",
    "Reduces the mana cost of Aeroblast by 20%.",
    0, 1,
    effects={"ability_stormbringer_aeroblast_cost_pct": 0.20},
    connect=["storm_bond"],
    source="CoA verbatim: 'Reduces the cast time of Aeroblast by -0.3 sec.' "
           "There are no cast times here, so nothing of this talent survives "
           "as written. Rerouted to cost, which is what a shorter cast buys - "
           "more Aeroblasts per mana bar. POSITIVE reduces."))

N.append(node(
    "storm_bond", "Storm Bond",
    "Your Shock, Electrocute and Freewind bank 6 extra Static.",
    0, 3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": BUILDERS,
          "grant_resource": {"resource": "static", "amount": 6}},
    connect=["invigoration"],
    source="CoA verbatim: 'Damage dealt by your Air Elemental now generates "
           "you 2 Static.' PETS NEVER FIRE PROCS - there is no "
           "fire_proc_trigger anywhere in entities/pet.py - so a pet's damage "
           "cannot trigger anything at all. Re-pointed at the caster's own "
           "Static builders, which is the same resource outcome through the "
           "one route that works. grant_resource takes a flat `amount` and "
           "Static is a real secondary resource, so gain_resource respects "
           "its cap."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "invigoration", "Invigoration",
    "Increases the damage your Air Elemental deals by a further 30%.",
    1, -4,
    effects={"pet_damage": 0.30},
    connect=["tailwind"],
    source="CoA verbatim: 'Your Aeroblast now grants your Air Elemental a "
           "stack of Invigoration. Increases the damage of your Air Elemental "
           "by 3% for 15 seconds, stacking 10 times. Additional applications "
           "do not refresh duration.' TWO WALLS: no proc payload can apply an "
           "effect to a PET (apply_effect lands on the caster or the "
           "trigger's target), and nothing reads another effect's stack "
           "count. Ten stacks of 3% is 30%, granted flat - the ceiling a "
           "fully-stacked elemental would have reached, without the ramp. "
           "CoA's Everlasting Invigoration and Aurat Scripts both modify this "
           "stacking buff and so have nothing to modify; their value is "
           "folded into the nodes below."))

N.append(node(
    "tailwind", "Tailwind",
    "Teaches Tailwind, which raises your damage and grants the party haste "
    "for 40 Static.",
    1, -2,
    effects={"unlock_ability": "stormbringer_tailwind"},
    connect=["unrelenting_winds"],
    source="CoA verbatim: 'Tap into the swift winds, increasing your damage "
           "by 10% and granting all allied players 5% increased haste for 15 "
           "sec.' LOAD-BEARING UNLOCK: stormbringer_tailwind carries "
           "requires_talent. The ability is target_type 'party', so the ally "
           "haste is real. CoA's Gift of Air rider ('your critical strikes "
           "now extend the duration of your Tailwind by 1.5 sec') is not "
           "built - no payload extends a live effect's duration."))

N.append(node(
    "unrelenting_winds", "Unrelenting Winds",
    "Increases the critical strike chance of your wind spells by 15%.",
    1, 0,
    effects={f"ability_{a}_crit": 15.0 for a in DAMAGING_WINDS},
    connect=["comforting_winds"],
    source="CoA verbatim: 'Increases the critical strike chance of Gale by "
           "15%.' FRONTIER HAS NO GALE. Re-pointed at the three wind "
           "abilities it does have - Freewind, Gust of Wind and Razorwind - "
           "which together occupy Gale's slot as the spec's spammable nature "
           "damage. CoA's 15% kept. ability_*_crit is a PERCENT."))

N.append(node(
    "quickdraft", "Quickdraft",
    "Increases the duration of Gust of Wind by 1 turn and the damage of your "
    "wind spells by 16%.",
    1, 2,
    effects={"ability_stormbringer_gust_of_wind_duration": 1,
             **{f"ability_{a}_damage": 0.16 for a in DAMAGING_WINDS}},
    connect=["comforting_winds"],
    source="CoA over 2 ranks: 'Increases the duration of your Updraft by 3 "
           "sec and increases its tick rate by 15%.' FRONTIER HAS NO UPDRAFT. "
           "Gust of Wind is the nearest real ability with a duration to "
           "extend; 3 sec is a turn. Tick rate has no meaning per-turn, so "
           "that 15% over two ranks becomes 16% damage across the wind "
           "spells. The small integer duration keeps this node out of the "
           "rank policy's reach."))

N.append(node(
    "comforting_winds", "Comforting Winds",
    "Your damage stirs the winds, raising your haste by 1% per stack for 3 "
    "turns, stacking 5 times.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "stormbringer_comforting_winds",
                           "name": "Comforting Winds", "effect_type": "buff",
                           "duration": 3, "max_stacks": 5,
                           "stat_mods": {"haste": 1.0},
                           "on_target": False}},
    connect=["kiss_of_the_clouds"],
    source="CoA verbatim: 'Your damage dealt now increases the haste of your "
           "Air Elemental by 1% for 10 sec, stacking 5 times. Damage dealt by "
           "your Air Elemental now increases your haste by 1% for 10 sec, "
           "stacking 5 times.' The first half is impossible twice over - "
           "PET_HASTE IS READ BY NOTHING, and no proc can apply an effect to "
           "a pet. The second half is impossible because pets never fire "
           "procs. What survives is the half CoA gives the caster, triggered "
           "by the caster's own damage: CoA's 1% and 5 stacks, 10 sec as 3 "
           "turns."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "kiss_of_the_clouds", "Kiss of the Clouds",
    "Teaches Kiss of the Clouds, shielding the whole party for 40 Static.",
    2, -4,
    effects={"unlock_ability": "stormbringer_kiss_of_the_clouds"},
    connect=["cyclones_embrace"],
    source="CoA verbatim: 'Grant all party and raid members a shield that "
           "absorbs damage, scaling with Intellect, for 10 sec. While active, "
           "the target suffers no spell pushback from taking damage.' "
           "LOAD-BEARING UNLOCK: stormbringer_kiss_of_the_clouds carries "
           "requires_talent, and it is target_type 'party', so the party "
           "shield is real. Spell pushback is not modelled."))

N.append(node(
    "cyclones_embrace", "Cyclone's Embrace",
    "Increases the amount Kiss of the Clouds absorbs by 100%.",
    2, -2,
    effects={"ability_stormbringer_kiss_of_the_clouds_potency": 1.00},
    connect=["focal_point"],
    source="CoA verbatim: 'Increases the base amount absorbed by your Kiss of "
           "the Clouds by 100%.' Ports exactly - ability_*_potency is the key "
           "that scales an absorb, since the shield is not damage or healing. "
           "CoA's 100% kept, which is steep but it is a 30-second cooldown "
           "costing 40 Static."))

N.append(node(
    "cyclones_recharge", "Cyclone's Recharge",
    "Your Static builders bring Kiss of the Clouds a turn closer to ready.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": BUILDERS,
          "reset_cooldown": {
              "abilities": ["stormbringer_kiss_of_the_clouds"],
              "turns": 1}},
    connect=["focal_point"],
    source="CoA verbatim: 'Casting Shock, Gale or Electrocute now reduces the "
           "remaining cooldown of your Kiss of the Clouds by -1 sec.' Gale "
           "does not exist; Freewind takes its place in the builder list. 1 "
           "sec becomes a turn, which is a buff relative to CoA, so a 1-turn "
           "internal cooldown holds it to once per turn."))

N.append(node(
    "focal_point", "Focal Point",
    "Your Tailwind and Clear Skies last a turn longer, and your spell "
    "critical strike chance rises by 5%.",
    2, 2,
    effects={"ability_stormbringer_tailwind_duration": 1,
             "ability_stormbringer_clear_skies_duration": 1,
             "crit_chance_spell": 5.0},
    connect=["aerodynamics"],
    source="CoA verbatim: 'Casting Call Lightning now increases the critical "
           "strike chance of party and raid members by 5% for 10 seconds.' "
           "Frontier has no Call Lightning, and a TALENT cannot grant allies "
           "crit - get_talent_effects() reads only the character's own trees. "
           "But Tailwind and Clear Skies ARE party abilities, so extending "
           "their duration is the real party lever a talent has; the 5% crit "
           "lands on the Stormbringer at CoA's own number. Same treatment as "
           "Guardian Inspiration's Banner nodes."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "aerodynamics", "Aerodynamics",
    "Teaches Aerodynamics, granting the party attack and spell power for 40 "
    "Static.",
    3, -4,
    effects={"unlock_ability": "stormbringer_aerodynamics"},
    connect=["flow"],
    source="CoA verbatim: 'Envelop party and raid members within 40 yds in "
           "magical mist, increasing their attack or spell power by 95 for 15 "
           "sec.' LOAD-BEARING UNLOCK: stormbringer_aerodynamics carries "
           "requires_talent, and it is target_type 'party'."))

N.append(node(
    "flow", "Flow",
    "Increases the healing of Invigorating Surge by 40%.",
    3, -2,
    effects={"ability_stormbringer_invigorating_surge_healing": 0.40},
    connect=["everlasting_invigoration"],
    source="CoA verbatim: 'Your Invigoration now stacks 5 additional times.' "
           "Invigoration could not be built as a stacking buff at all (see "
           "the Invigoration node - no proc can apply an effect to a pet, and "
           "nothing reads a stack count), so there are no stacks to add. "
           "Re-pointed at Invigorating Surge, the spec's real ally heal, "
           "which keeps the node in the support half of the tree rather than "
           "making it a third flat pet-damage line."))

N.append(node(
    "everlasting_invigoration", "Everlasting Invigoration",
    "Increases the health and armour of your Air Elemental by 30%.",
    3, 0,
    effects={"pet_health": 0.30, "pet_armor": 0.30},
    connect=["tempests_call"],
    source="CoA over 2 ranks: 'Increases the duration of Invigoration by 5 "
           "sec.' Invigoration is not a live effect here, so its duration "
           "cannot be extended. Re-pointed at the other two pet keys the "
           "engine reads, which is a longer-lived elemental rather than a "
           "longer buff - the same intent through the keys that exist. CoA's "
           "Aurat Scripts ('increases the damage gained per stack of "
           "Invigoration by 2%') fails for the same reason and is folded into "
           "Invigoration's flat 30%."))

N.append(node(
    "hurricanes", "Hurricanes",
    "Increases all damage you deal by 15%.",
    3, 2,
    effects={"all_damage": 0.15},
    connect=["gift_of_air"],
    source="CoA verbatim: 'Casting Unshackle now unshackles you, increasing "
           "your damage dealt by 15% for 15 seconds.' FRONTIER HAS NO "
           "UNSHACKLE - it is a pet transform, which has no mechanism either "
           "- so the trigger cannot exist. CoA's 15% is granted permanently. "
           "Stronger than CoA's windowed version, stated rather than "
           "hidden."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "tempests_call", "Tempest's Call",
    "Teaches Summon: Air Elemental, calling the elemental that this whole "
    "spec is built around.",
    4, -3,
    effects={"unlock_ability": "stormbringer_summon_air_elemental"},
    connect=["enveloping_winds"],
    source="CoA's Tempest Calling node, whose Builder description is the "
           "unresolved token '$4c', paired with its Air Elemental ability "
           "('$4e' - also unresolved). So there is no verbatim text to port "
           "and the node is named from CoA's own title. THE MOST LOAD-BEARING "
           "UNLOCK IN THE TREE: stormbringer_summon_air_elemental carries "
           "requires_talent, so without this node the Air Elemental cannot be "
           "summoned at all - and six other nodes here scale it. Kept at "
           "tier 4 as the old tree had it, rather than moved earlier, because "
           "moving it would change every existing Wind build."))

N.append(node(
    "enveloping_winds", "Enveloping Winds",
    "Freewind splashes 45% of its damage onto up to 2 nearby enemies, and "
    "your armour rises by 15%.",
    4, -1,
    effects={"armor_pct": 15.0},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_freewind"],
          "splash_damage": {"pct": 0.45, "max_targets": 2,
                            "school": "nature"}},
    connect=["unbound_elementalist"],
    source="CoA verbatim: 'Casting Gale now causes your Air Elemental to cast "
           "Gale. Additionally, you now emanate an aura around you, "
           "increasing the Armor of party and raid members by 390.' Three "
           "walls: Gale does not exist, nothing makes a pet cast an ability, "
           "and a talent cannot grant allies armour. Freewind stands in for "
           "Gale, the pet's echo becomes a splash (the same 'it hits twice' "
           "outcome through a live payload), and the armour lands on the "
           "Stormbringer. armor_pct takes percentage POINTS while "
           "splash_damage pct is a FRACTION."))

N.append(node(
    "gift_of_air", "Gift of Air",
    "Kiss of the Clouds fills your sails, raising your haste by 15% and all "
    "your damage by 20% for 5 turns.",
    4, 1,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_kiss_of_the_clouds"],
          "apply_effect": {"effect_id": "stormbringer_gift_of_air",
                           "name": "Gift of Air", "effect_type": "buff",
                           "duration": 5, "max_stacks": 1,
                           "stat_mods": {"haste": 15.0,
                                         "damage_dealt_pct": 20.0},
                           "on_target": False}},
    connect=["unbound_elementalist"],
    source="CoA verbatim: 'Casting Kiss of the Clouds now empowers your Air "
           "Elemental with Gift of Air for 30 sec. Increases damage dealt by "
           "20%, spell haste by 15%, and heals for 50 every 2 sec.' The buff "
           "cannot land on the PET - apply_effect goes to the caster or the "
           "trigger's target - so it lands on the Stormbringer with CoA's own "
           "20% and 15%. ON_CAST rather than on_damage_cast, because Kiss of "
           "the Clouds is a party shield that deals no damage and a damage "
           "trigger would never have fired. The periodic heal is dropped: no "
           "per-turn regeneration key exists. damage_dealt_pct inside a "
           "status effect is percentage POINTS."))

N.append(node(
    "child_of_the_storm", "Child of the Storm",
    "Reduces the cooldown of Razorwind and Gust of Wind by 20%.",
    4, 3,
    effects={"ability_stormbringer_razorwind_cooldown_pct": 0.20,
             "ability_stormbringer_gust_of_wind_cooldown_pct": 0.20},
    connect=["raging_zephyr"],
    source="CoA verbatim: 'Reduces the cooldown of your Cloudburst and "
           "Windsurf by 20%.' NEITHER ABILITY EXISTS HERE. Re-pointed at the "
           "two real wind abilities that have cooldowns worth cutting. CoA's "
           "20% kept. POSITIVE reduces."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "unbound_elementalist", "Unbound Elementalist",
    "Increases the damage your Air Elemental deals by a further 40%.",
    5, -3,
    effects={"pet_damage": 0.40},
    connect=["surge_of_might"],
    source="CoA verbatim: 'Increases the effectiveness of your Unshackle by "
           "20%.' Unshackle does not exist - it is the pet transform, which "
           "has no mechanism - so there is nothing to make more effective. "
           "Re-pointed at pet_damage, which is what Unshackle bought (CoA's "
           "own text: '+25% damage and +30% spell haste' on the elemental). "
           "Priced at 40% as the tier-5 payoff for a pet build, stacking with "
           "Power the Elements and Invigoration for a total of 90%."))

N.append(node(
    "raging_zephyr", "Raging Zephyr",
    "Increases the damage of Raging Zephyr by 50% and of your damage-over-"
    "time spells by 20%.",
    5, -1,
    effects={"ability_stormbringer_raging_zephyr_potency": 0.50,
             "dot_damage": 0.20},
    connect=["surge_of_might"],
    source="CoA verbatim: 'Transforms your Whirlpool into Raging Zephyr. "
           "Summon a Raging Zephyr at the targeted location for 12 seconds. "
           "Every 4 sec, it will pull all enemies within 10 yds inside of "
           "it.' Frontier HAS Raging Zephyr as an ability and it is NOT "
           "talent-gated, so the old tree's unlock node for it granted "
           "something the character already had and did nothing - this "
           "replaces it with real mechanics on the same ability. The pull is "
           "positional and the charges have no system."))

N.append(node(
    "aeromancy", "Aeromancy",
    "Increases the healing of Invigorating Surge by a further 30% and your "
    "spell critical strike chance by 5%.",
    5, 1,
    effects={"ability_stormbringer_invigorating_surge_healing": 0.30,
             "crit_chance_spell": 5.0},
    connect=["surge_of_might"],
    source="CoA verbatim: 'Casting Updraft will now cause your Air Elemental "
           "to cast its own Updraft beneath you.' Updraft does not exist and "
           "nothing makes a pet cast an ability, so neither half is "
           "buildable. Re-pointed at the support half of the kit - Updraft is "
           "CoA's ground heal, and Invigorating Surge is Frontier's real ally "
           "heal - so the node keeps its healing identity rather than "
           "becoming another damage line."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "surge_of_might", "Surge of Might",
    "Every one of your party buffs lasts a turn longer, and your spell "
    "damage rises by 20%.",
    6, 0,
    effects={**{f"ability_{a}_duration": 1 for a in AURAS},
             "spell_damage": 0.20},
    source="CoA verbatim: 'Emanate an aura around you for 15 seconds, causing "
           "allied players within 100 yds to deal 70% nature SP additional "
           "damage as Nature damage when they deal direct damage. Applies "
           "Exhaustion, preventing you from benefiting from similar effects "
           "for 1 minute.' A talent cannot make allies deal extra damage. But "
           "ALL FOUR of this spec's party auras are real target_type 'party' "
           "abilities, so a turn added to each is four party-wide buffs held "
           "a third longer - hit chance from Clear Skies, haste from "
           "Tailwind, attack and spell power from Aerodynamics, and the "
           "absorb from Kiss of the Clouds. That is a genuine support "
           "capstone, and the one this spec could already support without any "
           "ability conversion, unlike Guardian Inspiration's. Exhaustion has "
           "no mechanism and is dropped."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# NOTE it is the policy that does the spreading. Hand-authoring max_points=3
# keeps the ceiling as the PER-RANK value and triples it in play - the bug
# that shipped on Guardian Vanguard's Iron Guardian earlier today.
from tools.talent_ranks import rankable, spread  # noqa: E402

for _n in TREE["nodes"]:
    if _n["max_points"] < 3 and _n["tier"] < 6 and rankable(_n):
        spread(_n, 3)


#: Every Stormbringer ability with requires_talent that THIS tree unlocks.
#: Dropping one makes that ability unobtainable forever.
GATED = {
    "stormbringer_clear_skies",
    "stormbringer_tailwind",
    "stormbringer_aerodynamics",
    "stormbringer_kiss_of_the_clouds",
    "stormbringer_summon_air_elemental",
}


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    names = [n["name"] for n in TREE["nodes"]]
    assert len(names) == len(set(names)), "duplicate node NAME"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"
    unlocks = {(n.get("effects") or {}).get("unlock_ability")
               for n in TREE["nodes"]}
    missing = GATED - unlocks
    assert not missing, (
        f"these abilities are requires_talent and this tree is their only "
        f"unlock - dropping the node makes them unobtainable forever: "
        f"{sorted(missing)}")
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Stormbringer Wind: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
