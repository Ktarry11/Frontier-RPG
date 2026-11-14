#!/usr/bin/env python3
"""Rebuild Stormbringer's Lightning tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_stormbringer_lightning.py [--check]

SOURCE: data/reference/coa_worksheets/stormbringer.md and
data/reference/coa/stormbringer.json - 36 real Lightning talents from
Ascension's own CoA Builder payload. Role: DPS.

THE WORST TREE IN THE PROJECT. 23 nodes with ONE proc and 64 points;
Stormbringer measured 89.6% scalar-only across its three specs, the
highest of all 21 CoA classes.

WHAT THE SPEC IS. Kyle's canon: "Stormbringer is basically elemental
shaman, a PURE CASTER (not melee)." It runs on Mana plus STATIC, a real
secondary resource (abilities.py:158), and Static is the whole rotation:
Shock, Electrocute, Freewind, Forked Lightning, Volt and Charge all carry
a `generates` block that fills it, and Arm of Thorim and Ride the
Lightning spend it.

STATIC IS A REAL RESOURCE, SO THE SPENDER/BUILDER LOOP IS REAL - but
nothing reads HOW MUCH Static you hold. Five CoA talents scale off the
Static level ("damage increased based on Static level", "chance increases
based on Static level", "1% per Static depleted") and none of them can be
built: no effect key reads a live resource amount, the same wall that
stopped the Witch Doctor reading its Spirit stacks. Those are granted
flat at their realistic ceiling and say so per node.

UNLOCK NODES. Only ONE Stormbringer Lightning ability is actually
talent-gated - stormbringer_ride_the_lightning - and its unlock node is
PRESERVED. The old tree also carried unlock nodes for Arm of Thorim,
Forked Lightning, Aeroblast, Volt and Storm Ascendance, none of which are
gated, so those five nodes granted abilities the character already had
and did nothing at all. They are replaced with real mechanics on the same
abilities rather than kept as decoration. (Dropping a GATED unlock node is
how I stranded nine abilities earlier in this audit;
tools/qa_abilities_obtainable.py exists because of it and guards this.)

CONVENTIONS, which do not agree with each other:
  intellect_pct, spirit_pct                percentage POINTS
  spell_damage, all_damage, dot_damage, crit_damage_spell,
    ability_*_damage, ability_*_crit_damage   FRACTION
  crit_chance_spell, haste, hit_rating,
    ability_*_crit                            PERCENT
  spell_damage_taken_pct / magic_damage_taken_pct inside a status effect:
    divided by 100, POSITIVE INCREASES damage taken
  splash_damage                            FRACTION
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every cast time, which takes Arm of Thorim's
"cast time increased based on Static". Standing still and blinking forward
are positional, which takes Electrical Charge and half of Ride the
Lightning. "Tick rate -25%" (Stormy Days) has no meaning per-turn. Silence
and interrupt have no keys, which takes half of Tome of Lightning.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/stormbringer_lightning.json"

#: The Static builders - every ability carrying a `generates` block.
BUILDERS = ["stormbringer_shock", "stormbringer_electrocute",
            "stormbringer_freewind", "stormbringer_forked_lightning",
            "stormbringer_volt"]

#: The big three CoA keeps naming together.
BIG_THREE = ["stormbringer_shock", "stormbringer_conjure_storm",
             "stormbringer_arm_of_thorim"]

TREE = {
    "spec_name": "Stormbringer Lightning",
    "tree_id": "stormbringer_lightning",
    "description": ("Static and thunder - a pure caster who banks charge "
                    "and spends it on Thorim's arm."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 36 real CoA Lightning talents (role "
        "DPS). Replaces THE WORST TREE IN THE PROJECT - 23 nodes with one "
        "proc - from the worst-measuring class, Stormbringer at 89.6% "
        "scalar-only. Static is a real secondary resource and its "
        "builder/spender loop works, but NOTHING READS A LIVE RESOURCE "
        "AMOUNT, so the five CoA talents that scale off Static level are "
        "granted flat at their ceiling. The one genuinely talent-gated "
        "ability, ride_the_lightning, keeps its unlock node; five unlock "
        "nodes for non-gated abilities are replaced with real mechanics, "
        "since granting an ability the character already has does "
        "nothing."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"stormbringer_lightning_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"stormbringer_lightning_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "thunderous", "Thunderous",
    "Increases the critical strike damage of your spells by 60%.",
    0, -5,
    effects={"crit_damage_spell": 0.60},
    connect=["electric_energy"],
    source="CoA's level 20 passive: 'Increases the critical damage of your "
           "spells by 150%.' Priced at 60% rather than 150%: CoA's figure "
           "sits on top of a different crit-damage baseline, and 150% here "
           "would make a single Electrocute crit the whole rotation. "
           "crit_damage_spell is a FRACTION."))

N.append(node(
    "electric_energy", "Electric Energy",
    "Increases the damage of Shock, Conjure Storm and Arm of Thorim by 20%.",
    0, -3,
    effects={f"ability_{a}_damage": 0.20 for a in BIG_THREE},
    connect=["wicked_storms"],
    source="CoA verbatim: 'Increases the damage of your Shock, Call "
           "Lightning, and Arm of Thorim by 20%.' Frontier has no Call "
           "Lightning; Conjure Storm is its enemy_aoe nature nuke and stands "
           "in, which is the same slot in the rotation. CoA names this trio "
           "together in three separate talents, so they are kept as a group."))

N.append(node(
    "wicked_storms", "Wicked Storms",
    "Increases your spell damage by 10%.",
    0, -1,
    effects={"spell_damage": 0.10},
    connect=["tome_of_lightning"],
    source="CoA verbatim: 'Increases your Nature damage dealt by 5%.' THERE "
           "IS NO PER-SCHOOL DAMAGE KEY - nature_damage, shadow_damage and "
           "magic_damage are read by nothing - so it lands on spell_damage. "
           "Doubled to 10% because the spec deals almost nothing but nature, "
           "making the broader key nearly equivalent rather than a windfall. "
           "FRACTION."))

N.append(node(
    "tome_of_lightning", "Tome of Lightning",
    "Increases your spell critical strike chance by 4%.",
    0, 1,
    effects={"crit_chance_spell": 4.0},
    connect=["titanic_thunderbolt"],
    source="CoA verbatim: 'Increases your critical strike chance by 2% and "
           "reduces the duration of interrupt and silence effects against you "
           "by -20%.' SILENCE AND INTERRUPT HAVE NO KEYS - the only "
           "duration-reduction key that exists is "
           "stun_duration_reduction_pct, read solely against effects flagged "
           "is_stun - so that half is dropped rather than quietly re-pointed "
           "at stuns, which are a different thing. The crit is doubled to 4% "
           "to carry the node alone. PERCENT."))

N.append(node(
    "titanic_thunderbolt", "Titanic Thunderbolt",
    "Increases the critical strike chance of Shock, Conjure Storm and Arm of "
    "Thorim by 8%.",
    0, 3,
    effects={f"ability_{a}_crit": 8.0 for a in BIG_THREE},
    connect=["invoking_storms"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of Shock, "
           "Conjure Storm, and Eye of the Storm by 4%.' Doubled for the two "
           "ranks. Frontier has no Eye of the Storm; Arm of Thorim takes its "
           "place to keep CoA's trio intact. ability_*_crit is a PERCENT."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "invoking_storms", "Invoking Storms",
    "Increases the damage of Shock, Conjure Storm and Arm of Thorim by a "
    "further 30%.",
    1, -4,
    effects={f"ability_{a}_damage": 0.30 for a in BIG_THREE},
    connect=["voltaic_bursts"],
    source="CoA over 2 ranks: 'Increases the spell power scaling of Shock, "
           "Call Lightning, and Arm of Thorim by 15%.' Doubled for the two "
           "ranks. There is no key for how much an ability scales with spell "
           "power - the coefficients live on the abilities - so it is "
           "expressed as damage, which is what the scaling buys. Deliberately "
           "stacks with Electric Energy at tier 0, as CoA's two do."))

N.append(node(
    "superconductor", "Superconductor",
    "Increases the damage of Arm of Thorim by 40%.",
    1, -2,
    effects={"ability_stormbringer_arm_of_thorim_damage": 0.40},
    connect=["voltaic_bursts"],
    source="CoA verbatim: 'Increases the damage of your Arm of Thorim by an "
           "additional 1% per Static depleted.' NOTHING READS A LIVE RESOURCE "
           "AMOUNT - no effect key asks how much Static you hold or spent - "
           "so the per-Static scaling cannot exist. Arm of Thorim depletes "
           "ALL Static in CoA, and a realistic bank at cast time is around "
           "40, so 40% is the flat equivalent of CoA's ceiling rather than an "
           "invention. This is the same wall that flattened the Witch "
           "Doctor's Soul Feeder and Spirit Hunting."))

N.append(node(
    "voltaic_bursts", "Voltaic Bursts",
    "Increases the damage your damage-over-time spells deal by 50%.",
    1, 0,
    effects={"dot_damage": 0.50},
    connect=["jolt"],
    source="CoA verbatim: 'Increases the periodic damage of Shock by 50%.' "
           "There is no key for one ability's periodic damage as distinct "
           "from its direct damage, so CoA's 50% is applied to the spec's "
           "dots generally via dot_damage - which also reaches Volt, the "
           "spec's real dot and Static engine. Broader than CoA's, stated "
           "rather than hidden."))

N.append(node(
    "jolt", "Jolt",
    "Increases the damage of Electrocute by 20% and its critical strike "
    "chance by 20%.",
    1, 2,
    effects={"ability_stormbringer_electrocute_damage": 0.20,
             "ability_stormbringer_electrocute_crit": 20.0},
    connect=["never_strikes_twice"],
    source="CoA over 2 ranks: 'Increases the damage and critical strike "
           "chance of Electrocute by 10%.' Doubled for the two ranks. Note "
           "the two keys take different units in the same block: "
           "ability_*_damage is a FRACTION, ability_*_crit a PERCENT."))

N.append(node(
    "never_strikes_twice", "Never Strikes Twice?",
    "Electrocute has a 25% chance to strike again.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "ability_filter": ["stormbringer_electrocute"],
          "cast_ability": "stormbringer_electrocute"},
    connect=["critical_circuit"],
    source="CoA verbatim: 'Your Electrocute now has a 25% chance to strike "
           "again.' PORTS EXACTLY - cast_ability takes a bare ability id and "
           "Electrocute is auto-learned, so it is in the caster's book. CoA's "
           "25% kept. Note this also re-fires Electrocute's own `generates` "
           "block, so a second strike banks another 20 Static, which is "
           "CoA's behaviour too."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "critical_circuit", "Critical Circuit",
    "Your critical strikes refund 10 Static.",
    2, -4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "static", "amount": 10}},
    connect=["sparks"],
    source="CoA verbatim: 'Direct critical strikes with Static spenders now "
           "refund 10 Static.' PORTS ALMOST EXACTLY - grant_resource takes a "
           "flat `amount`, which is what CoA states, and Static is a real "
           "secondary resource so gain_resource respects its cap. The "
           "'with Static spenders' scoping is dropped: a proc's "
           "ability_filter would restrict it, but Arm of Thorim and Ride the "
           "Lightning are the only spenders and neither crits often enough to "
           "carry the node, so it fires on any crit."))

N.append(node(
    "sparks", "Sparks",
    "Electrocute and Arm of Thorim leave the target taking 3% more spell "
    "damage for 3 turns.",
    2, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_electrocute",
                             "stormbringer_arm_of_thorim"],
          "apply_effect": {"effect_id": "stormbringer_sparks",
                           "name": "Sparks", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 3.0},
                           "on_target": True}},
    connect=["dark_skies"],
    source="CoA verbatim: 'Damage dealt by Electrocute and Arm of Thorim now "
           "increase the target's chance to be critically hit by spells by 3% "
           "for 10 seconds.' THERE IS NO RECIPIENT-SIDE 'CHANCE TO BE CRIT' "
           "KEY - crit lives on the attacker - so this becomes spell damage "
           "taken, the live recipient-side equivalent, at CoA's own 3%. 10 "
           "sec is 3 turns. Same translation as the Witch Doctor's Hollow "
           "Spirit."))

N.append(node(
    "improved_forked_lightning", "Improved Forked Lightning",
    "Forked Lightning splashes 35% of its damage onto 2 more enemies.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_forked_lightning"],
          "splash_damage": {"pct": 0.35, "max_targets": 2,
                            "school": "nature"}},
    connect=["titanstorm"],
    source="CoA verbatim: 'Your Forked Lightning now affects 1 additional "
           "enemy.' NO KEY ADDS TARGETS TO AN ABILITY - the count lives on "
           "the ability - so it becomes splash_damage, as every "
           "added-targets talent in this audit has. 2 targets rather than "
           "CoA's 1 because a percentage splash is weaker than a full extra "
           "bounce, and Forked Lightning generates 5 Static per enemy struck, "
           "so the extra reach is partly a resource node."))

N.append(node(
    "dark_skies", "Dark Skies",
    "A spell that fails to crit raises your spell critical strike chance by "
    "2% per stack for 3 turns, stacking 5 times.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "stormbringer_dark_skies",
                           "name": "Dark Skies", "effect_type": "buff",
                           "duration": 3, "max_stacks": 5,
                           "stat_mods": {"crit_chance_spell": 2.0},
                           "on_target": False}},
    connect=["stormy_days"],
    source="CoA verbatim: 'When your direct damage spells fail to critically "
           "strike, your critical strike chance is increased by 2% for 10 "
           "sec, stacking up to 5 times. Critically striking removes this "
           "effect.' THERE IS NO 'ON FAILED CRIT' TRIGGER and no payload "
           "removes a stack or an effect, so neither half of CoA's "
           "self-correcting loop can be built. It fires on every damage cast "
           "instead and simply ramps - CoA's 2% and 5 stacks kept, 10 sec is "
           "3 turns. Stronger than CoA's, because nothing consumes it; stated "
           "rather than hidden. The description says 'fails to crit' is the "
           "flavour, so it is worded as the ramp it actually is."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "titanstorm", "Titanstorm",
    "Casting Electrocute brings Arm of Thorim a turn closer to ready.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["stormbringer_electrocute"],
          "reset_cooldown": {"abilities": ["stormbringer_arm_of_thorim"],
                             "turns": 1}},
    connect=["fulmination"],
    source="CoA verbatim: 'Casting Call Lightning or Electrocute now reduces "
           "the cooldown of Arm of Thorim and Lightning Cage by 1.5 sec.' "
           "Frontier has neither Call Lightning nor Lightning Cage, so only "
           "the Electrocute half and the Arm of Thorim target survive. 1.5 "
           "sec rounds to a turn, with a 1-turn internal cooldown so it "
           "cannot stack within one turn."))

N.append(node(
    "fulmination", "Fulmination",
    "Increases the critical strike chance of Arm of Thorim by 30%.",
    3, -2,
    effects={"ability_stormbringer_arm_of_thorim_crit": 30.0},
    connect=["thorims_gift"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of Call "
           "Lightning and Arm of Thorim by 15% against targets affected by "
           "your Volt.' Doubled for the two ranks. The Volt condition cannot "
           "be read - no effect key asks whether a target carries a debuff - "
           "and Volt is on everything in this rotation anyway, so it was "
           "nearly always true. Call Lightning does not exist here."))

N.append(node(
    "thorims_gift", "Thorim's Gift",
    "Arm of Thorim leaves unstable electricity in the ground, dealing nature "
    "damage over 2 turns.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_arm_of_thorim"],
          "apply_effect": {"effect_id": "stormbringer_thorims_gift",
                           "name": "Thorim's Gift", "effect_type": "dot",
                           "duration": 2, "potency": 44,
                           "damage_school": "nature", "on_target": True}},
    connect=["lightning_rod"],
    source="CoA verbatim: 'Your Arm of Thorim now leaves unstable electricity "
           "beneath the target, dealing damage equal to 10% of its damage "
           "dealt to enemies within every 1 sec for 3 seconds.' A ground "
           "effect ticking for 3 sec IS a dot, so this ports in shape. The "
           "potency is flat rather than a share of the hit, because an "
           "apply_effect payload cannot read the triggering ability's "
           "damage, and it lands on the target rather than an area because "
           "there is no ground placement."))

N.append(node(
    "stormy_days", "Stormy Days",
    "Increases the damage of Conjure Storm by 25%.",
    3, 2,
    effects={"ability_stormbringer_conjure_storm_damage": 0.25},
    connect=["lightning_rod"],
    source="CoA verbatim: 'Increases the tick rate of Conjure Storm by -25%.' "
           "A faster tick has no meaning when ticks are per-turn, so it is "
           "rerouted to damage, which is what a faster tick delivers - more "
           "damage in the same window."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "lightning_rod", "Lightning Rod",
    "Forked Lightning has a 35% chance to fuse Volt into the target as well.",
    4, -3,
    proc={"trigger": "on_damage_cast", "chance": 35, "icd": 0,
          "ability_filter": ["stormbringer_forked_lightning"],
          "cast_ability": "stormbringer_volt"},
    connect=["crackling_devastation"],
    source="CoA verbatim: 'Damage dealt by Forked Lightning now has a 20% "
           "chance to spread an active Volt on your target to each affected "
           "enemy. Chance increases based on Static level.' Spreading an "
           "existing dot to new targets is not a payload - apply_effect lands "
           "on the trigger's own target - so it CASTS Volt instead, which "
           "applies the same dot and also fires Volt's `generates` block for "
           "6 more Static. The Static-level scaling cannot be read (see "
           "Superconductor), so 35% is the flat equivalent of CoA's 20% "
           "floor plus its scaling."))

N.append(node(
    "flux_arc", "Flux Arc",
    "Forked Lightning and Arm of Thorim splash 15% of their damage onto up "
    "to 3 nearby enemies.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_forked_lightning",
                             "stormbringer_arm_of_thorim"],
          "splash_damage": {"pct": 0.15, "max_targets": 3,
                            "school": "nature"}},
    connect=["crackling_devastation"],
    source="CoA verbatim: 'Your Forked Lightning and Arm of Thorim now marks "
           "enemies for 6 sec. Your Call Lightning against marked enemies "
           "deals an additional 15% of its damage to them and nearby "
           "enemies.' A MARK READ BY A LATER SPECIFIC CAST needs two things "
           "that do not exist: a debuff-presence check and a payload that "
           "empowers a named follow-up. Call Lightning does not exist either. "
           "Built as the splash the mark was for, at CoA's own 15%, paid by "
           "the two abilities that applied the mark."))

N.append(node(
    "crackling_devastation", "Crackling Devastation",
    "Increases the critical strike damage of Electrocute by 30%.",
    4, 1,
    effects={"ability_stormbringer_electrocute_crit_damage": 0.30},
    connect=["thundershocker"],
    source="CoA verbatim: 'Increases the critical damage of Electrocute by "
           "30%.' Ports exactly. ability_*_crit_damage is a FRACTION."))

N.append(node(
    "thundershocker", "Thundershocker",
    "Your spells leave the enemy taking 10% more damage from you for 3 turns.",
    4, 3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "stormbringer_thundershocker",
                           "name": "Thundershocker", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "on_target": True}},
    connect=["electrical_charge"],
    source="CoA verbatim: 'While rooted by Eye of the Storm, affected enemies "
           "now take 30% increased damage from you.' Frontier has no Eye of "
           "the Storm and roots are not modelled, so the gate cannot exist. "
           "Rebuilt as a plain damage-taken debuff applied by casting, priced "
           "at 10% rather than CoA's 30% because it needs no setup and lands "
           "on everything. BARE damage_taken_pct IS READ RAW, so 10% is 0.10 "
           "- authoring 10.0 would be +1000% damage taken."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "electrical_charge", "Electrical Charge",
    "Your spells build charge, raising your haste by 1% per stack for 5 "
    "turns, stacking 20 times.",
    5, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "stormbringer_electrical_charge",
                           "name": "Electrical Charge", "effect_type": "buff",
                           "duration": 5, "max_stacks": 20,
                           "stat_mods": {"haste": 1.0},
                           "on_target": False}},
    connect=["lord_of_lightning"],
    source="CoA verbatim: 'Standing still grants you Electrical Charge every "
           "second, increasing your haste by 1%. Upon reaching 20 stacks, "
           "your spells dont deplete Static for 10 sec, after which the "
           "charges are depleted.' Three walls: standing still is positional, "
           "there is no periodic trigger to tick the stacks on, and the "
           "20-stack threshold cannot be read - nothing reads another "
           "effect's stack count. Rebuilt so casting builds the charge, which "
           "a pure caster does every turn anyway. CoA's 1% and 20 stacks "
           "kept; the free-Static payoff is dropped."))

N.append(node(
    "ride_the_lightning", "Ride the Lightning",
    "Teaches Ride the Lightning, a nature blast through every enemy in your "
    "path that spends 40 Static.",
    5, -1,
    effects={"unlock_ability": "stormbringer_ride_the_lightning"},
    connect=["lord_of_lightning"],
    source="CoA verbatim: 'Infuse yourself with lightning and blink forward a "
           "long distance, dealing Nature damage to all enemies in your "
           "path.' THIS UNLOCK NODE IS LOAD-BEARING AND PRESERVED: "
           "stormbringer_ride_the_lightning is one of only six Stormbringer "
           "abilities with requires_talent set, so without this node it is "
           "unobtainable forever. Dropping gated unlock nodes is how I "
           "stranded nine abilities earlier in this audit, which is why "
           "tools/qa_abilities_obtainable.py exists. The blink is positional "
           "and lives on the ability as an enemy_aoe hit; the talent only "
           "grants it."))

N.append(node(
    "storm_barrier", "Storm Barrier",
    "Reduces the magic damage you take by 25%.",
    5, 1,
    effects={"magic_damage_taken_pct": -0.25},
    connect=["lord_of_lightning"],
    source="CoA verbatim: 'While Lightning Cage is active your Magic Damage "
           "taken is now reduced by -25% and you are unable to be hit by "
           "ranged attacks.' Frontier has no Lightning Cage, so the gate has "
           "nothing to read, and ranged immunity has no key. The mitigation "
           "is granted permanently at CoA's own 25% - the spec's only "
           "defensive node, which a pure caster wants. AS A TALENT EFFECT "
           "magic_damage_taken_pct is a FRACTION where NEGATIVE reduces; "
           "inside a status effect the same key is divided by 100 and "
           "positive INCREASES damage taken."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "lord_of_lightning", "Lord of Lightning",
    "Increases the damage of Forked Lightning, Conjure Storm and Electrocute "
    "by 30%, and Electrocute splashes 40% of its damage onto up to 3 nearby "
    "enemies.",
    6, 0,
    effects={"ability_stormbringer_forked_lightning_damage": 0.30,
             "ability_stormbringer_conjure_storm_damage": 0.30,
             "ability_stormbringer_electrocute_damage": 0.30},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_electrocute"],
          "splash_damage": {"pct": 0.40, "max_targets": 3,
                            "school": "nature"}},
    source="CoA verbatim: 'Storm Ascendance now additionally grants you Lord "
           "of Lightning for 20 seconds. Increases the damage dealt by Forked "
           "Lightning, Call Lightning, and Electrocute by an additional 30% "
           "and allows Electrocute to strike 3 additional enemies.' Both "
           "halves are built: CoA's 30% on the three abilities (Conjure Storm "
           "standing in for Call Lightning), and the three extra enemies as "
           "splash_damage, since no key adds targets. What is lost is the "
           "gate - CoA grants this only while Storm Ascendance is up, and "
           "nothing reads whether a buff is active - so it is permanent. "
           "Stated rather than hidden; priced as a capstone accordingly."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations.
#
# NOTE it is the policy that does the spreading. Hand-authoring max_points=3
# keeps the ceiling as the PER-RANK value and triples it in play - the bug
# that shipped on Guardian Vanguard's Iron Guardian earlier today.
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
    # the gated ability must keep its unlock node
    unlocks = {(n.get("effects") or {}).get("unlock_ability")
               for n in TREE["nodes"]}
    assert "stormbringer_ride_the_lightning" in unlocks, \
        "ride_the_lightning is requires_talent - dropping its unlock node " \
        "makes it unobtainable forever"
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Stormbringer Lightning: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
