#!/usr/bin/env python3
"""Rebuild Venomancer's Venom tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_venomancer_venom.py [--check]

SOURCE: data/reference/coa_worksheets/venomancer.md and
data/reference/coa/venomancer.json - 38 real Venom talents from
Ascension's own CoA Builder payload. Role: DPS.

Venomancer measured 88.9% scalar-only across its FOUR specs (Venom,
Stalking, Fortitude tank, Vizier healer - 160 CoA talents), the worst of
the 14 classes remaining. Venom itself was 23 nodes with ONE proc.

WHAT THE SPEC IS. A poison-and-rot caster. Venom Bolt and Serpent's Fang
are the direct spells, Wilt and Spore the dots, Mycosis the burst, Decay
the area application. Mana.

SHADRA'S GIFT PORTS WHOLE - both halves. spell_damage and haste are both
in STAT_CONVERSION_TARGETS and intellect in STAT_CONVERSION_SOURCES, so
CoA's level 20 passive is exact. That is now the third class in this
audit built on a real conversion node (Witch Doctor on Spirit,
Stormbringer on Intellect-to-haste, this on Intellect to both).

MUSHROOMS AND FUNGARIANS HAVE NO MECHANISM, and between them they take
nine talents. A Mushroom is a ground object that explodes on a delay:
there is no ground placement and no delayed detonation, so Blightfang,
Sporelord, Prophetic Speaker, From Life Comes Death and Mycelial Ring all
lose their stated effect. A Fungarian is a pet, and VENOMANCER SUMMONS NO
PETS AT ALL - nothing in data/abilities/venomancer.json has a summon
field - so pet_damage/pet_health/pet_armor would be dead data here, the
same trap the Witch Doctor's Serpent Wards set (see tools/qa_pet_keys.py,
which exists because of it). Fungal Assailant, Venoxis Rage and Fungal
Allies lose theirs.

FIVE COA ABILITIES THIS TREE NAMES DO NOT EXIST HERE: Fungal Assailant,
Mycelial Ring, Sepsis Bloom, Serpent Lord's Ring and Rot Lich. Each
talent naming one is re-pointed at a real ability and says so.

UNLOCK NODES. Only ONE Venomancer ability is talent-gated -
venomancer_barbed_stinger - and its unlock node lives in the FORTITUDE
tree, not here. The old Venom tree carried five unlock nodes (Decay,
Spore, Weaver Form, Wilt, Spindlebind) and none of those abilities is
gated: all five granted something the character already had and did
nothing. Verified the gate is real first - an ability with
requires_talent reports is_learned False until its unlock node is bought,
and flips True the moment it is - so these five genuinely are decorative.
Replaced with real mechanics.

CONVENTIONS, which do not agree with each other:
  intellect_pct, armor_pct                 percentage POINTS
  spell_damage, all_damage, dot_damage, crit_damage_spell,
    ability_*_damage, ability_*_crit_damage   FRACTION
  crit_chance_spell, haste, hit_rating,
    ability_*_crit                            PERCENT
  spell_damage_taken_pct inside a status effect: divided by 100,
    POSITIVE INCREASES damage taken
  threat_generation_pct   FRACTION, NEGATIVE reduces
  splash_damage           FRACTION
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every cast time (Envenom, Limb Decayer, Cycle of Decay's
"casts 30% faster"), every yard and all movement, and the "currently
active Venom" loadout (Intoxicating Venoms) - there is no mode state a
talent can read, the same wall that reshaped the Witch Doctor's Brewing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/venomancer_venom.json"

#: The spec's direct spells.
DIRECT = ["venomancer_venom_bolt", "venomancer_serpents_fang"]

#: The poisons and rots - everything that ticks.
ROTS = ["venomancer_wilt", "venomancer_spore"]

TREE = {
    "spec_name": "Venomancer Venom",
    "tree_id": "venomancer_venom",
    "description": ("Rot and spore - a poison caster who turns Intellect "
                    "into both damage and speed."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 38 real CoA Venom talents (role DPS). "
        "Venomancer measured 88.9% scalar-only across its four specs, the "
        "worst of the 14 classes remaining; Venom itself was 23 nodes with "
        "one proc. Shadra's Gift ports whole - both conversions are legal "
        "pairs. Mushrooms (ground objects with a delayed explosion) and "
        "Fungarians (pets, and VENOMANCER SUMMONS NO PETS AT ALL) have no "
        "mechanism and between them take nine talents. Five CoA abilities "
        "this tree names do not exist in Frontier. The old tree's five "
        "unlock nodes were all for non-gated abilities and did nothing; the "
        "class's only gated ability, barbed_stinger, is unlocked from the "
        "Fortitude tree."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"venomancer_venom_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"venomancer_venom_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "shadras_gift", "Shadra's Gift",
    "Increases your spell damage by 25% of your Intellect and your haste by "
    "20% of your Intellect.",
    0, -5,
    effects={"spell_damage_from_intellect_pct": 0.25,
             "haste_from_intellect_pct": 0.20},
    connect=["acid_bolt"],
    source="CoA verbatim: 'Level 20 Passive. Increases your spell damage by "
           "25% of your Intellect and your haste rating by 20% of your "
           "Intellect.' PORTS WHOLE - spell_damage and haste are both in "
           "STAT_CONVERSION_TARGETS and intellect is in "
           "STAT_CONVERSION_SOURCES, so both halves are legal and CoA's "
           "numbers are kept exactly. Both are FRACTIONS."))

N.append(node(
    "acid_bolt", "Acid Bolt",
    "Increases the damage of Venom Bolt by 30% and its critical strike chance "
    "by 6%.",
    0, -3, ranks=3,
    effects={"ability_venomancer_venom_bolt_damage": 0.10,
             "ability_venomancer_venom_bolt_crit": 2.0},
    connect=["rotpriest"],
    source="CoA over 3 ranks: 'Increases the damage of Venom Bolt by 10% and "
           "its critical strike chance by 2%.' Authored at CoA's own PER-RANK "
           "values with CoA's 3 ranks, so get_effective_effects() multiplies "
           "by points spent to reach 30% and 6% - the description states the "
           "ceiling. Authoring the ceiling here with ranks=3 would have "
           "delivered 90% and 18%, the bug that shipped on Guardian "
           "Vanguard's Iron Guardian. Note the two keys differ in unit: "
           "ability_*_damage is a FRACTION, ability_*_crit a PERCENT."))

N.append(node(
    "rotpriest", "Rotpriest",
    "Increases the critical strike damage of your spells by 50%.",
    0, -1,
    effects={"crit_damage_spell": 0.50},
    connect=["protraction"],
    source="CoA verbatim: 'Increases your spell critical damage by 100%.' "
           "Priced at 50%: CoA's figure sits on a different crit-damage "
           "baseline, and doubling crit damage from a tier-0 node would make "
           "crit the only stat this spec wants. crit_damage_spell is a "
           "FRACTION."))

N.append(node(
    "protraction", "Protraction",
    "Increases the duration of Wilt and Spore by 1 turn.",
    0, 1,
    effects={"ability_venomancer_wilt_duration": 1,
             "ability_venomancer_spore_duration": 1},
    connect=["serpents_embrace"],
    source="CoA over 2 ranks: 'Increases the duration of your Venomancer "
           "periodic damage effects by 3 sec.' No key names a group of "
           "effects, so the spec's two real dots are written out. 3 sec is a "
           "turn. The small integers keep this node out of the rank policy's "
           "reach - a duration cannot be divided across ranks (see "
           "tools/talent_ranks.rankable())."))

N.append(node(
    "serpents_embrace", "Serpent's Embrace",
    "Increases the damage of Serpent's Fang by 30%.",
    0, 3,
    effects={"ability_venomancer_serpents_fang_damage": 0.30},
    connect=["fungal_growth"],
    source="CoA over 2 ranks: 'Increases the damage of Serpent's Fang and its "
           "spell power scaling by 15%.' Doubled for the two ranks. There is "
           "no key for how much an ability scales with spell power - the "
           "coefficients live on the ability - so both halves are expressed "
           "as damage."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "fungal_growth", "Fungal Growth",
    "Your spells have a 35% chance to leave the target taking 2% more spell "
    "damage per stack for 10 turns, stacking 10 times.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "venomancer_fungal_growth",
                           "name": "Fungal Growth", "effect_type": "debuff",
                           "duration": 10, "max_stacks": 10,
                           "stat_mods": {"spell_damage_taken_pct": 2.0},
                           "on_target": True}},
    connect=["rotting_away"],
    source="CoA verbatim: 'Shadow and Nature damage dealt now has a 35% "
           "chance to increase periodic damage you deal to the target by 2% "
           "for 30 sec, stacking 10 times.' THERE IS NO TRIGGER-SIDE SCHOOL "
           "FILTER (proc['school'] only types a damage_flat payload) and no "
           "recipient-side key for 'periodic damage taken' specifically, so "
           "it becomes spell damage taken - which covers the dots this spec "
           "actually lands. CoA's 35%, 2% and 10 stacks all kept; 30 sec is "
           "10 turns. Two later CoA talents (Mycosis, Captivation) read this "
           "stack count and cannot."))

N.append(node(
    "rotting_away", "Rotting Away",
    "Wilt has a 15% chance to strike again as shadow damage.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 15, "icd": 0,
          "ability_filter": ["venomancer_wilt"],
          "damage_flat": 70, "school": "shadow"},
    connect=["wilting_away"],
    source="CoA verbatim: 'Your Wilt now has a 15% chance when it deals "
           "damage to strike again as Shadow damage.' PORTS CLOSELY - "
           "damage_flat with a school is a live payload and CoA's 15% is "
           "kept. It fires on Wilt's CAST rather than on each of its ticks, "
           "because there is no periodic trigger."))

N.append(node(
    "wilting_away", "Wilting Away",
    "Wilt splashes 60% of its damage onto 1 nearby enemy.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_wilt"],
          "splash_damage": {"pct": 0.60, "max_targets": 1,
                            "school": "nature"}},
    connect=["necessary_preparations"],
    source="CoA verbatim: 'Your Wilt now strikes an additional nearby "
           "enemy.' NO KEY ADDS TARGETS TO AN ABILITY - the count lives on "
           "the ability - so it becomes splash_damage at CoA's one extra "
           "target. 60% rather than 100% because a splash applies no dot, "
           "only damage, so it is strictly weaker than a second full "
           "application and should not be priced as one."))

N.append(node(
    "envenom", "Envenom",
    "Reduces the mana cost of Venom Bolt by 20%.",
    1, 2,
    effects={"ability_venomancer_venom_bolt_cost_pct": 0.20},
    connect=["necessary_preparations"],
    source="CoA verbatim: 'Reduces the cast time of Venom Bolt by -0.3 sec.' "
           "There are no cast times here, so nothing of this talent survives "
           "as written. Rerouted to cost, which is what a shorter cast buys. "
           "POSITIVE reduces."))

N.append(node(
    "necessary_preparations", "Necessary Preparations",
    "Increases the damage of Wilt by 20% and your chance to hit by 3%.",
    1, 4,
    effects={"ability_venomancer_wilt_damage": 0.20, "hit_rating": 3.0},
    connect=["mycosis"],
    source="CoA verbatim: 'Increases the damage of Wilt by 20% and it now "
           "increases the chance to hit the target with spells by 3% for 20 "
           "seconds.' The hit bonus is a buff applied by landing Wilt, which "
           "would need a proc; folded into the node as a flat 3% instead, "
           "since Wilt is on every target in this rotation and the condition "
           "was nearly always true. hit_rating is a PERCENT."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "mycosis", "Mycosis",
    "Increases the damage of Mycosis by 50%.",
    2, -4,
    effects={"ability_venomancer_mycosis_damage": 0.50},
    connect=["captivation"],
    source="CoA verbatim: 'Fungus grows throughout the body of an enemy, "
           "dealing Nature damage and applying a shield that absorbs the next "
           "healing done to them. Deals 20% increased damage for each stack "
           "of Fungal Growth on the target.' Frontier HAS Mycosis as an "
           "ability, so this is not its unlock. NOTHING READS ANOTHER "
           "EFFECT'S STACK COUNT, so the per-stack scaling off Fungal Growth "
           "cannot exist; a realistic stack count mid-fight is 2-3, giving "
           "50% flat rather than CoA's uncapped 20% per stack (which at 10 "
           "stacks would be 200%)."))

N.append(node(
    "captivation", "Captivation",
    "Increases the damage of Mycosis by a further 25%.",
    2, -2,
    effects={"ability_venomancer_mycosis_damage": 0.25},
    connect=["a_pit_of_snakes"],
    source="CoA verbatim: 'Increases Mycosis's damage through Fungal Growth "
           "stacks by 5%.' A talent modifying how another talent scales off a "
           "third effect's stack count fails three ways over. Granted as flat "
           "damage on the same ability, deliberately stacking with the node "
           "above it, as CoA's two do."))

N.append(node(
    "lethargy", "Lethargy",
    "Wilt leaves the enemy 3% less likely to hit and taking 5% more damage "
    "for 3 turns.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_wilt"],
          "apply_effect": {"effect_id": "venomancer_lethargy",
                           "name": "Lethargy", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"hit_rating": -3.0,
                                         "damage_taken_pct": 0.05},
                           "on_target": True}},
    connect=["a_pit_of_snakes"],
    source="CoA verbatim: 'Damage dealt by your Wilt now applies Lethargy to "
           "affected enemies. Reduces an enemy's chance to hit by -3% and "
           "increases their Nature Damage taken from you by 5% for 8 "
           "seconds. Dispelling this effect increases the dispeller's "
           "resource costs by 100% for 5 seconds.' Both stat halves port - "
           "CoA's 3% and 5%, and 8 sec is 3 turns - with the Nature-specific "
           "damage becoming general (no per-school taken key beyond the "
           "existing siblings). The dispel punishment has no mechanism. TWO "
           "UNITS IN ONE STATUS EFFECT: hit_rating is a PERCENT so -3% is "
           "-3.0, while BARE damage_taken_pct IS READ RAW so 5% is 0.05."))

N.append(node(
    "a_pit_of_snakes", "A Pit of Snakes",
    "Serpent's Fang feeds the pit, raising your damage by 5% per stack for 3 "
    "turns, stacking 3 times.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_serpents_fang"],
          "apply_effect": {"effect_id": "venomancer_pit_of_snakes",
                           "name": "A Pit of Snakes", "effect_type": "buff",
                           "duration": 3, "max_stacks": 3,
                           "stat_mods": {"damage_dealt_pct": 5.0},
                           "on_target": False}},
    connect=["blightfang"],
    source="CoA verbatim: 'Serpent's Fang now increases the damage of "
           "subsequent Serpent's Fangs by 15% for 8 sec, stacking up to 3 "
           "times.' No key scopes a buff to one named ability, so it raises "
           "all damage instead - priced down from CoA's 15% per stack to 5%, "
           "because 45% on everything is a different node from 45% on one "
           "spell. CoA's 3 stacks kept; 8 sec is 3 turns. damage_dealt_pct "
           "inside a status effect is percentage POINTS."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "blightfang", "Blightfang",
    "Serpent's Fang bursts, splashing 40% of its damage onto up to 3 nearby "
    "enemies.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_serpents_fang"],
          "splash_damage": {"pct": 0.40, "max_targets": 3,
                            "school": "nature"}},
    connect=["venom_saturation"],
    source="CoA verbatim: 'Casting Serpent's Fang now spawns a Mushroom below "
           "the target that will explode after 2 sec, dealing Nature damage "
           "to nearby enemies.' A MUSHROOM IS A GROUND OBJECT WITH A DELAYED "
           "EXPLOSION and this engine has neither ground placement nor a "
           "delayed detonation - the same accumulator wall as the Witch "
           "Doctor's Puppeteer's Threads. Built as an immediate splash, which "
           "is the damage the Mushroom was for. This is the first of five "
           "Mushroom talents; the rest are noted on their own nodes."))

N.append(node(
    "venom_saturation", "Venom Saturation",
    "Increases the damage your damage-over-time spells deal by 25%.",
    3, -2,
    effects={"dot_damage": 0.25},
    connect=["septic_trauma"],
    source="CoA verbatim: 'Increases the damage of your poison effects by 25% "
           "against enemies above 50% health.' No effect key reads a target's "
           "health percentage - high_health_damage_threshold_pct is a dead "
           "key, confirmed earlier in this audit - so the condition is "
           "dropped and CoA's 25% applies always. dot_damage is the live key "
           "for 'poison effects', since nothing names a poison group."))

N.append(node(
    "septic_trauma", "Septic Trauma",
    "Increases the duration of Wilt by a further 1 turn.",
    3, 0,
    effects={"ability_venomancer_wilt_duration": 1},
    connect=["infestation"],
    source="CoA verbatim: 'Harmful critical strikes now increase the duration "
           "of Wilt by 2 sec.' NO PAYLOAD EXTENDS A LIVE EFFECT'S DURATION - "
           "consumes_stacks_of is the only thing that lengthens a dot and it "
           "reads the caster's own stacks - so the on-crit extension cannot "
           "exist. Built as a flat turn on Wilt, stacking with Protraction at "
           "tier 0. Small integer, so outside the rank policy."))

N.append(node(
    "infestation", "Infestation",
    "Your spells have a 10% chance to ready Serpent's Fang again.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "reset_cooldown": ["venomancer_serpents_fang"]},
    connect=["decay_mastery"],
    source="CoA verbatim: 'Periodic damage dealt now has a 10% chance to "
           "reduce the cooldown of Serpent's Fang and Fungal Assailant by 20% "
           "of the remaining cooldown.' Periodic damage has no trigger, so it "
           "fires off casts. Fungal Assailant does not exist in Frontier. A "
           "percentage of the REMAINING cooldown is not expressible - "
           "reset_cooldown takes whole turns or a full reset - so the 10% "
           "buys a full reset, which is cleaner than inventing a turn count. "
           "CoA's 10% kept."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "decay_mastery", "Decay",
    "Increases the damage of Decay by 40% and reduces its cooldown by 25%.",
    4, -3,
    effects={"ability_venomancer_decay_damage": 0.40,
             "ability_venomancer_decay_cooldown_pct": 0.25},
    connect=["from_death_comes_life"],
    source="CoA verbatim: 'Apply Wilt to up to 5 enemies at target location "
           "and drop a Mushroom that will explode after 2 sec.' Frontier HAS "
           "Decay as an ability, so this is not its unlock - the old tree's "
           "unlock node for it did nothing, since Decay is not "
           "requires_talent. Built as damage and cooldown on the real "
           "ability. CoA's Limb Decayer node ('reduces the cast time and "
           "increases the mana cost of Decay by 50%') is folded in as the "
           "cooldown half, its cast time being meaningless and no key adding "
           "a cost. POSITIVE on a _cooldown_pct reduces."))

N.append(node(
    "from_death_comes_life", "From Death Comes Life",
    "Spore brings Decay a turn closer to ready.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["venomancer_spore"],
          "reset_cooldown": {"abilities": ["venomancer_decay"], "turns": 1}},
    connect=["fungic"],
    source="CoA verbatim: 'Damage dealt by Spore now reduces the cooldown of "
           "Decay by -1 sec.' Ports in shape; 1 sec becomes a turn, which is "
           "a buff relative to CoA because a fraction of a turn cannot be "
           "expressed, so a 1-turn internal cooldown holds it to once per "
           "turn. CoA's Prophetic Speaker ('each time you spawn a Mushroom, "
           "reduce the cooldown of Decay by -1 sec') is the same mechanic "
           "keyed on Mushrooms, which do not exist, and is folded in here "
           "rather than built twice."))

N.append(node(
    "fungic", "Fungic",
    "Your direct spells leave fungus in the wound, dealing nature damage over "
    "2 turns.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": DIRECT,
          "apply_effect": {"effect_id": "venomancer_fungic",
                           "name": "Fungic", "effect_type": "dot",
                           "duration": 2, "potency": 34,
                           "damage_school": "nature", "on_target": True}},
    connect=["sporelord"],
    source="CoA verbatim: 'You now apply Fungic to enemies affected by "
           "Lethargy, dealing an additional 20% of the damage dealt by your "
           "Venom Bolt or Serpent's Fang as Nature damage over 3 seconds, "
           "stacking up to 2 times.' The Lethargy condition cannot be read - "
           "no effect key asks whether a target carries a debuff - and "
           "Lethargy is applied by Wilt, which is on everything anyway. The "
           "potency is flat rather than a share of the hit, because an "
           "apply_effect payload cannot read the triggering ability's "
           "damage."))

N.append(node(
    "fungal_link", "Fungal Link",
    "Increases your haste by 3% and reduces the threat your spells generate "
    "by 20%.",
    4, 3,
    effects={"haste": 3.0, "threat_generation_pct": -0.20},
    connect=["sporelord"],
    source="CoA verbatim: 'Increases the spell haste of all party and raid "
           "members by 3%. Does not stack with similar effects. In addition, "
           "the range of your Rot spells is increased by 20% and the threat "
           "they generate is reduced by -20%.' A TALENT CANNOT REACH AN ALLY, "
           "so the haste lands on the Venomancer at CoA's own 3% and the "
           "description says 'your'. Range means nothing here. The threat "
           "reduction ports exactly - threat_generation_pct is a FRACTION "
           "where NEGATIVE reduces, the opposite sign to the _cost_pct "
           "family."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "sporelord", "Sporelord",
    "Spore bursts outward, splashing 50% of its damage onto up to 3 nearby "
    "enemies.",
    5, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_spore"],
          "splash_damage": {"pct": 0.50, "max_targets": 3,
                            "school": "nature"}},
    connect=["cycle_of_decay"],
    source="CoA verbatim: 'Fungal Assailant now spawns 3 Mushrooms below the "
           "target.' TWO WALLS AT ONCE: Fungal Assailant does not exist in "
           "Frontier, and Mushrooms have no mechanism. Re-pointed at Spore, "
           "the spec's real area dot, with CoA's three Mushrooms becoming "
           "three splash targets - which is what three exploding Mushrooms "
           "delivered. CoA's Fungal Allies ('Fungal Assailant now summons 2 "
           "additional Fungarians') fails for the same reason plus the pet "
           "wall, and is not built."))

N.append(node(
    "weaver_form", "Weaver Form",
    "Teaches Weaver Form, the spec's caster shape.",
    5, -5,
    effects={"unlock_ability": "venomancer_weaver_form"},
    connect=["cycle_of_decay"],
    source="CoA's own description for this node is the unresolved token "
           "'$b4'. LOAD-BEARING UNLOCK, and newly so: Kyle's call on 5 Nov "
           "2026 was that the DPS and healing forms should be level-40 "
           "talents 'like Tree of life or moonkin', while Spider Form and "
           "Beetle Form stay 'learnt via level up' like Bear and Cat. So "
           "venomancer_weaver_form now carries requires_talent with level_req "
           "40, and without this node it is unobtainable forever - "
           "qa_abilities_obtainable flagged it the moment the ability was "
           "gated. Placed at tier 5 rather than 6: tier 5 opens at 25 points "
           "in the tree, which a level-40 Venomancer can reach, whereas tier "
           "6 needs 30. Before this change all four forms were auto-learned, "
           "so every Venomancer had the tank form from level 10 and both "
           "caster forms regardless of spec, and this node did nothing."))

N.append(node(
    "cycle_of_decay", "Cycle of Decay",
    "Your spells have a 20% chance to quicken the cycle, raising your haste "
    "by 20% for 2 turns.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "apply_effect": {"effect_id": "venomancer_cycle_of_decay",
                           "name": "Cycle of Decay", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"haste": 20.0},
                           "on_target": False}},
    connect=["venoxis_rage"],
    source="CoA's level 50 passive: 'When you cast any spell you now have a "
           "20% chance to gain Cycle of Decay. Your Venom Bolt is now "
           "castable while moving and casts 30% faster for 6 sec.' Casting "
           "while moving is positional and there are no cast times, so "
           "'casts 30% faster' becomes haste - acting more often, which is "
           "what faster means in a turn-based fight. CoA's 20% chance kept; 6 "
           "sec is 2 turns."))

N.append(node(
    "venoxis_rage", "Venoxis Rage",
    "Mycosis enrages you, raising all your damage by 30% for 2 turns.",
    5, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_mycosis"],
          "apply_effect": {"effect_id": "venomancer_venoxis_rage",
                           "name": "Venoxis Rage", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 30.0},
                           "on_target": False}},
    connect=["rot_lich"],
    source="CoA verbatim: 'Your Mycosis now enrages your Fungarians for 6 "
           "seconds, increasing its damage and attack speed by 30% for 6 "
           "seconds.' FUNGARIANS ARE PETS AND VENOMANCER SUMMONS NONE - "
           "nothing in its ability file has a summon field, so pet_damage "
           "would be dead data here (tools/qa_pet_keys.py guards exactly "
           "this). The enrage lands on the Venomancer instead, at CoA's own "
           "30%; 6 sec is 2 turns."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "rot_lich", "Rot Lich",
    "Everything rots: your damage-over-time spells deal 40% more, and Wilt "
    "and Spore hit 50% harder.",
    6, 0,
    effects={"dot_damage": 0.40,
             **{f"ability_{a}_damage": 0.50 for a in ROTS}},
    source="CoA's own description for the Rot Lich ability is the unresolved "
           "token '$b2', and its Suffocating Coils talent is '$b0', so there "
           "is no verbatim text for either and this capstone is NOT a "
           "faithful copy - it is named from CoA's own title and built as the "
           "payoff the tree points at. Flagged so a later pass can correct it "
           "if the real text surfaces, the same situation as Brewing's "
           "Mixologist ('$40'), Lightning's Umbral Glaive ('$42') and Wind's "
           "Tempest Calling ('$4c'). CoA's Mycelial Ring is the other "
           "candidate for this slot and is not built: it places a damaging "
           "ring with twelve Mushrooms and then heals allies inside it, which "
           "needs ground placement, delayed detonation and an area heal, none "
           "of which exist."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# NOTE Acid Bolt is deliberately authored at CoA's PER-RANK values with CoA's
# own 3 ranks, so the policy skips it (max_points is already 3) and
# get_effective_effects() multiplies by points spent to reach the ceiling.
# Every other ranked node is authored at the CEILING for the policy to
# divide. Hand-authoring a ceiling at ranks=3 tripled five Guardian nodes.
from tools.talent_ranks import rankable, spread  # noqa: E402

for _n in TREE["nodes"]:
    if _n["max_points"] < 3 and _n["tier"] < 6 and rankable(_n):
        spread(_n, 3)


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
    assert "venomancer_weaver_form" in unlocks, (
        "venomancer_weaver_form is requires_talent (Kyle's 5 Nov 2026 call: "
        "the DPS form is a level-40 talent like Moonkin) and this tree is "
        "its only unlock - dropping the node makes it unobtainable forever")
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Venomancer Venom: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
