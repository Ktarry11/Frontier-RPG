#!/usr/bin/env python3
"""Rebuild Pyromancer's Incineration tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_pyromancer_incineration.py [--check]

SOURCE: data/reference/coa_worksheets/pyromancer.md and
data/reference/coa/pyromancer.json - 36 real Incineration talents from
Ascension's own CoA Builder payload. Role: DPS.

Pyromancer measured 84.1% scalar-only, worst of the 13 classes remaining;
Incineration itself was 23 nodes with TWO procs.

PYROMANCER IS THE BEST-STRUCTURED CLASS IN THIS AUDIT. Each of its three
trees owns exactly THREE talent-gated abilities, at tiers 4, 5 and 6, and
every one is accounted for - nine gated abilities, nine unlock nodes, no
strays. Someone built that deliberately and it is preserved exactly:
this tree owns pillar_of_flame (t4), fired_up (t5) and pyroclasm (t6),
and main() asserts all three.

HEAT AND EMBERS DO NOT EXIST. CoA's Pyromancer banks Heat ("Generates 10
Heat Per Tick") and spends Embers, and eight talents here read, generate
or consume one of them. Pyromancer's resource is MANA with NO SECONDARY
(abilities.py:133), no ability carries a `generates` block, and nothing
reads a live resource amount anyway. So "each active Ember", "Ember
spenders" and "consuming Embers" all become either the named abilities
themselves or flat values, per node.

"FOR EACH PERIODIC EFFECT ON THE TARGET" is the other recurring shape -
Combustion, Cataclysmic Power and Pyromantic Accelerants all scale off
the Pyromancer's own dot count on a target. Nothing counts effects on a
target, so each is granted at a realistic three-dot value, flat.

SPELL PENETRATION IS LIVE AND WORTH KNOWING ABOUT. `spell_penetration`
is fed from bonuses into a real character attribute
(character.py:1382) and read attacker-side by both Character and Monster
take_damage. So Incinerator genuinely works - and it becomes a much
stronger node whenever per-school creature resistances get authored,
which is currently shelved.

CONVENTIONS, which do not agree with each other:
  intellect_pct                            percentage POINTS
  spell_damage, all_damage, dot_damage, crit_damage_spell,
    ability_*_damage, ability_*_crit_damage   FRACTION
  crit_chance_spell, haste, ability_*_crit    PERCENT
  spell_penetration                        FLAT rating, not a percentage
  spell_damage_taken_pct inside a status effect: divided by 100,
    POSITIVE INCREASES damage taken
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every cast time (Residual Power, Fired Up's "now
instant"), "tick rate" (Explosive), and the on-expiry trigger Sizzle
needs.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/pyromancer_incineration.json"

#: CoA's "Ember spenders" - the big direct nukes.
SPENDERS = ["pyromancer_explode", "pyromancer_flames_of_neltharion",
            "pyromancer_lava_shard"]

#: The dots CoA calls "Pyromancer periodic effects".
BURNS = ["pyromancer_ignite", "pyromancer_blaze"]

#: This tree's three talent-gated abilities. Dropping any unlock node makes
#: that ability unobtainable forever.
GATED = {
    "pyromancer_pillar_of_flame",
    "pyromancer_fired_up",
    "pyromancer_pyroclasm",
}

TREE = {
    "spec_name": "Pyromancer Incineration",
    "tree_id": "pyromancer_incineration",
    "description": ("Burn everything - a fire caster who stacks dots and "
                    "detonates them."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 36 real CoA Incineration talents (role "
        "DPS). Pyromancer measured 84.1% scalar-only, worst of the 13 "
        "classes remaining. IT IS ALSO THE BEST-STRUCTURED CLASS IN THE "
        "AUDIT: each tree owns exactly three talent-gated abilities at tiers "
        "4, 5 and 6, nine in total with no strays - preserved exactly and "
        "asserted in main(). Heat and Embers do not exist (Pyromancer's "
        "resource is MANA with no secondary and no ability generates "
        "either), and nothing counts periodic effects on a target, which "
        "between them reshape eleven talents. spell_penetration IS live and "
        "becomes stronger once per-school creature resistances are "
        "authored."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"pyromancer_incineration_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"pyromancer_incineration_{c}"
                         for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "lighting_the_fuse", "Lighting the Fuse",
    "Increases your spell critical strike chance by 15% of your Intellect.",
    0, -5,
    effects={"crit_chance_spell_from_intellect_pct": 0.15},
    connect=["magnitude_10"],
    source="CoA's level 30 passive: 'Allows your periodic effects to "
           "critically strike and increases your spell critical strike rating "
           "by 15% of your Intellect.' The conversion PORTS EXACTLY - "
           "crit_chance_spell is in STAT_CONVERSION_TARGETS and intellect in "
           "STAT_CONVERSION_SOURCES. The first half is dropped: there is no "
           "per-ability or per-effect 'can crit' flag, because everything can "
           "crit here already - the same non-issue as Venomancer Vizier's "
           "Fangbinder."))

N.append(node(
    "magnitude_10", "Magnitude 10",
    "Increases the critical strike chance of Flare Bolt by 10%.",
    0, -3,
    effects={"ability_pyromancer_flare_bolt_crit": 10.0},
    connect=["searing_power"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of Flare "
           "Bolt by 5%.' Doubled for the two ranks. Flare Bolt is the spec's "
           "filler nuke. ability_*_crit is a PERCENT."))

N.append(node(
    "searing_power", "Searing Power",
    "Increases the damage of Flare Bolt by 20%.",
    0, -1,
    effects={"ability_pyromancer_flare_bolt_damage": 0.20},
    connect=["embrace_the_fire"],
    source="CoA verbatim: 'Increases the spell power scaling of Flare Bolt by "
           "20%.' There is no key for how much an ability scales with spell "
           "power - the coefficients live on the ability - so it is expressed "
           "as damage, which is what the scaling buys."))

N.append(node(
    "embrace_the_fire", "Embrace the Fire",
    "Increases the damage of Blaze and Ignite by 20%.",
    0, 1,
    effects={f"ability_{a}_damage": 0.20 for a in BURNS},
    connect=["arsonist"],
    source="CoA verbatim: 'Increases the damage of Blaze and Ignite by 20%.' "
           "Both abilities exist in Frontier and are the spec's two dots - "
           "what CoA calls its 'Pyromancer periodic effects', which three "
           "other talents try to count."))

N.append(node(
    "arsonist", "Arsonist",
    "Increases the critical strike damage of your spells by 20%.",
    0, 3,
    effects={"crit_damage_spell": 0.20},
    connect=["cataclysmic_power"],
    source="CoA verbatim: 'Increases the critical damage of your Ember "
           "spenders by 10%.' EMBERS DO NOT EXIST - Pyromancer's resource is "
           "MANA with no secondary (abilities.py:133) and no ability carries a "
           "`generates` block - so 'Ember spenders' has no membership to "
           "scope to. Applied to spell crit damage generally and doubled to "
           "20% to be worth a tier-0 point. crit_damage_spell is a FRACTION."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "cataclysmic_power", "Cataclysmic Power",
    "Increases the damage of Flare Bolt by 27%.",
    1, -4, ranks=3,
    effects={"ability_pyromancer_flare_bolt_damage": 0.09},
    connect=["combustion"],
    source="CoA over 3 ranks: 'Increases the damage of Flare Bolt by 3% for "
           "each periodic effect you have on the target.' NOTHING COUNTS "
           "EFFECTS ON A TARGET - no effect key reads a target's debuffs at "
           "all - so the per-dot scaling cannot exist. This spec maintains "
           "three periodic effects in practice (Ignite, Blaze and whichever "
           "Scorch is up), so 3% x 3 dots is 9% per rank, reaching 27% at "
           "full investment. Authored at the PER-RANK value with CoA's own 3 "
           "ranks, so the policy skips it and get_effective_effects() "
           "multiplies by points spent."))

N.append(node(
    "combustion", "Combustion",
    "Increases the damage of Explode by 45%.",
    1, -2,
    effects={"ability_pyromancer_explode_damage": 0.45},
    connect=["scorched"],
    source="CoA verbatim: 'Damage dealt by Explode is now increased by 15% "
           "for each of your Pyromancer periodic effects on the target.' Same "
           "wall as Cataclysmic Power - nothing counts effects on a target - "
           "so 15% x 3 realistic dots is 45%, flat. Explode is the spec's "
           "detonator and the whole point of stacking dots, so this is the "
           "node that most wants the real mechanic and cannot have it."))

N.append(node(
    "scorched", "Scorched",
    "Your critical strikes scorch the target, burning them for fire damage "
    "over 2 turns.",
    1, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "pyromancer_scorched",
                           "name": "Scorched", "effect_type": "dot",
                           "duration": 2, "potency": 42,
                           "damage_school": "fire", "on_target": True}},
    connect=["melting_point"],
    source="CoA's level 20 passive: 'Direct critical strikes with Ember "
           "spenders now Scorch the target, Burning them for an additional "
           "30% of the damage dealt over 6 sec.' on_crit is live and a dot is "
           "the right shape, so this ports closely - 6 sec is 2 turns. The "
           "Ember-spender scoping is dropped (no such membership) so it fires "
           "on any crit, and the potency is flat because an apply_effect "
           "payload cannot read the triggering hit's damage."))

N.append(node(
    "melting_point", "Melting Point",
    "Increases your spell critical strike chance by 3%, and your critical "
    "strikes leave the target taking 3% more spell damage for 4 turns.",
    1, 2,
    effects={"crit_chance_spell": 3.0},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "pyromancer_melting_point",
                           "name": "Melting Point", "effect_type": "debuff",
                           "duration": 4, "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 3.0},
                           "on_target": True}},
    connect=["explosive"],
    source="CoA verbatim: 'Increases your critical strike chance by 3% and "
           "critical strikes with Fire spells now increases the chance for "
           "the enemy to by critically hit with spells by 3% for 12 seconds.' "
           "THERE IS NO RECIPIENT-SIDE 'CHANCE TO BE CRIT' KEY - crit lives "
           "on the attacker - so it becomes spell damage taken at CoA's own "
           "3%, the same translation used four times already in this audit. "
           "12 sec is 4 turns. No trigger-side school filter exists, so "
           "'with Fire spells' is dropped; this spec casts almost nothing "
           "else."))

N.append(node(
    "explosive", "Explosive",
    "Increases the damage your damage-over-time spells deal by 20%.",
    1, 4,
    effects={"dot_damage": 0.20},
    connect=["wreath_of_flames"],
    source="CoA over 2 ranks: 'Increases the tick rate of Blaze and Ignite by "
           "10%.' A faster tick has no meaning when ticks are per-turn, so "
           "the doubled 20% becomes dot damage - what a faster tick "
           "delivers."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "wreath_of_flames", "Wreath of Flames",
    "Your spells have a 10% chance to set you flamecasting, raising your "
    "haste by 5% per stack for 5 turns, stacking 5 times.",
    2, -4,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "apply_effect": {"effect_id": "pyromancer_flamecasting",
                           "name": "Flamecasting", "effect_type": "buff",
                           "duration": 5, "max_stacks": 5,
                           "stat_mods": {"haste": 5.0},
                           "on_target": False}},
    connect=["flames_of_focus"],
    source="CoA verbatim: 'Periodic Fire damage now has a 10% chance to grant "
           "a stack of Flamecasting, or 2 stacks if they critically strike. "
           "Increases your spell haste by 5% for 15 sec. Stacks 5 times. "
           "Additional applications do not refresh duration.' Periodic damage "
           "has no trigger, so it fires off casts. CoA's 10%, 5% and 5 stacks "
           "all kept; 15 sec is 5 turns. A payload cannot grant two stacks at "
           "once, so the crit bonus is dropped, and re-application always "
           "refreshes here. Frontier has no Wreath of Flames ABILITY, so this "
           "is purely the talent."))

N.append(node(
    "flames_of_focus", "Flames of Focus",
    "Increases your haste by 5%.",
    2, -2,
    effects={"haste": 5.0},
    connect=["to_ashes"],
    source="CoA verbatim: 'Adds 1 additional stack to Flamecasting and "
           "increases its duration by 5 sec.' NO KEY MODIFIES ANOTHER "
           "EFFECT'S max_stacks OR DURATION - the same wall that took "
           "Venomancer Fortitude's Beetle Poison - so neither half is "
           "buildable. Granted as flat haste, which is what a sixth "
           "Flamecasting stack would have been worth."))

N.append(node(
    "to_ashes", "To Ashes",
    "Your critical strikes restore mana.",
    2, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "grant_resource": {"resource": "mana", "amount": 40}},
    connect=["pyromaniac"],
    source="CoA verbatim: 'Damaging critical strikes now generate 10 Heat and "
           "restore 3% of your base mana.' Heat does not exist. The mana half "
           "ports in shape, but grant_resource takes a FLAT `amount` only - "
           "no percentage-of-maximum form - so 40 stands in for 3% of a "
           "mid-level pool. 1-turn internal cooldown so a multi-hit turn does "
           "not refill the bar."))

N.append(node(
    "pyromaniac", "Pyromaniac",
    "Increases the critical strike chance of Explode, Flames of Neltharion "
    "and Lava Shard by 5%.",
    2, 2,
    effects={f"ability_{a}_crit": 5.0 for a in SPENDERS},
    connect=["pyromantic_accelerants"],
    source="CoA verbatim: 'Increases the critical strike chance of Ember "
           "spenders by 5%.' Embers do not exist, so CoA's 'Ember spenders' "
           "is read as the three big direct nukes Frontier has - Explode, "
           "Flames of Neltharion and Lava Shard - which are what the term "
           "covers in CoA's own tooltips. CoA's 5% kept."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "pyromantic_accelerants", "Pyromantic Accelerants",
    "Increases the damage of Flames of Neltharion and Explode by 15%.",
    3, -4,
    effects={"ability_pyromancer_flames_of_neltharion_damage": 0.15,
             "ability_pyromancer_explode_damage": 0.15},
    connect=["fiery_passion"],
    source="CoA verbatim: 'Your Flames of Neltharion and Explode now deal 15% "
           "increased damage to Burning targets.' No effect key reads whether "
           "a target carries a debuff, and this spec keeps everything Burning "
           "anyway, so the condition was nearly always true. CoA's 15% kept "
           "and applies always."))

N.append(node(
    "fiery_passion", "Fiery Passion",
    "Increases your haste by 6%.",
    3, -2,
    effects={"haste": 6.0},
    connect=["rapid_incineration"],
    source="CoA verbatim: 'Increases the spell haste of all party and raid "
           "members by 3%. Does not stack with similar effects. In addition, "
           "your spell haste is increased by 3%.' A TALENT CANNOT REACH AN "
           "ALLY - get_talent_effects() reads only the character's own trees - "
           "so the party half lands on the Pyromancer too, giving CoA's two "
           "3% halves as a single 6%. The description says 'your' rather than "
           "promising a raid buff the engine will not deliver."))

N.append(node(
    "rapid_incineration", "Rapid Incineration",
    "Reduces the cooldown of Lava Shard and Pillar of Flame by 20%.",
    3, 0,
    effects={"ability_pyromancer_lava_shard_cooldown_pct": 0.20,
             "ability_pyromancer_pillar_of_flame_cooldown_pct": 0.20},
    connect=["sizzle"],
    source="CoA verbatim: 'Consuming Embers now reduces the cooldown of Lava "
           "Shard and Pillar of Flame by 10%.' Embers do not exist, so the "
           "trigger condition goes and the reduction is permanent, doubled to "
           "20% since it no longer needs a spender to fire. POSITIVE reduces. "
           "Pillar of Flame is unlocked at tier 4 below, so this node is "
           "worth taking after it."))

N.append(node(
    "sizzle", "Sizzle",
    "Your damage-over-time spells throw off a Flare Bolt.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
          "ability_filter": BURNS,
          "cast_ability": "pyromancer_flare_bolt"},
    connect=["pillar_of_flame"],
    source="CoA verbatim: 'When Flamecasting expires you launch a Flare Bolt "
           "on up to 12 enemies affected by your active Pyromancer periodic "
           "effects.' NO TRIGGER FIRES WHEN AN EFFECT EXPIRES, and nothing "
           "selects targets by which debuffs they carry. Rebuilt so the dots "
           "themselves throw the bolt - cast_ability takes a bare id and Flare "
           "Bolt is auto-learned, so it is in the book. 25% with a 1-turn icd "
           "rather than guaranteed, since a free nuke on every dot cast would "
           "outclass the rotation."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "pillar_of_flame", "Pillar of Flame",
    "Teaches Pillar of Flame, a lava pillar that also burns nearby enemies.",
    4, -3,
    effects={"unlock_ability": "pyromancer_pillar_of_flame"},
    connect=["incinerator"],
    source="CoA verbatim: 'Generates 20 Heat Per Target. Create a pillar of "
           "lava beneath an enemy, dealing Fire damage. Deals an additional "
           "Fire damage to enemies near the primary target.' LOAD-BEARING "
           "UNLOCK: pyromancer_pillar_of_flame carries requires_talent, so "
           "without this node it is unobtainable forever. Kept at tier 4 "
           "exactly where the shipped tree had it - Pyromancer's three trees "
           "each own three gated abilities at tiers 4, 5 and 6, the "
           "best-structured arrangement in this audit, and moving one would "
           "break that pattern and every existing build."))

N.append(node(
    "incinerator", "Incinerator",
    "Increases your spell penetration by 30.",
    4, -1,
    effects={"spell_penetration": 30.0},
    connect=["roasted_alive"],
    source="CoA's level 40 passive: 'Increases your spell penetration by 30, "
           "scaling with your level.' PORTS AS WRITTEN, minus the level "
           "scaling (no key scales a flat rating by level). `spell_penetration` "
           "is fed from bonuses into a real character attribute "
           "(character.py:1382) and read attacker-side by BOTH "
           "Character.take_damage and Monster.take_damage, so it genuinely "
           "works today against magic resistance - and it becomes a much "
           "stronger node whenever per-school creature resistances get "
           "authored, which is currently shelved. A FLAT RATING, not a "
           "percentage."))

N.append(node(
    "roasted_alive", "Roasted Alive",
    "Reduces the cooldown of Fired Up! by 25%.",
    4, 1,
    effects={"ability_pyromancer_fired_up_cooldown_pct": 0.25},
    connect=["flamespiller"],
    source="CoA verbatim: 'Increases the chance to trigger Fired Up by 20%.' "
           "Fired Up is an ABILITY with a cooldown here, not a proc, so there "
           "is no trigger chance to increase. Rerouted to its cooldown, which "
           "is the same outcome - Fired Up available more often. POSITIVE "
           "reduces."))

N.append(node(
    "flamespiller", "Flamespiller",
    "Your critical strikes with Explode or Flames of Neltharion burst for "
    "fire damage.",
    4, 3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "ability_filter": ["pyromancer_explode",
                             "pyromancer_flames_of_neltharion"],
          "damage_flat": 105, "school": "fire"},
    connect=["fired_up"],
    source="CoA verbatim: 'Critical strikes with Explode or Flames of "
           "Neltharion now extend the duration of Fired Up by 0.5 sec.' NO "
           "PAYLOAD EXTENDS A LIVE EFFECT'S DURATION, and half a second is "
           "below a turn regardless. Rerouted to direct damage off exactly "
           "CoA's two abilities, so the node still rewards critting with "
           "them. 1-turn internal cooldown."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "fired_up", "Fired Up!",
    "Teaches Fired Up!, a burst window that sharply raises your critical "
    "strike chance.",
    5, -3,
    effects={"unlock_ability": "pyromancer_fired_up"},
    connect=["residual_power"],
    source="CoA verbatim: 'Your Ember spenders are now instant and have a 30% "
           "chance to refund their cost and increases your chance to "
           "critically strike by 30% for 15 sec.' LOAD-BEARING UNLOCK: "
           "pyromancer_fired_up carries requires_talent. The instant-cast and "
           "cost-refund halves live on the ability or not at all; the talent "
           "only grants it. Kept at tier 5 where the shipped tree had it."))

N.append(node(
    "residual_power", "Residual Power",
    "Reduces the mana cost of Explode, Flames of Neltharion and Lava Shard by "
    "20%.",
    5, -1,
    effects={f"ability_{a}_cost_pct": 0.20 for a in SPENDERS},
    connect=["magmatic"],
    source="CoA verbatim: 'Each active Ember now reduces the cast time of "
           "Explode by -8%.' Embers do not exist and there are no cast times, "
           "so nothing of this talent survives as written. Rerouted to the "
           "cost of the three spenders, which is what cheaper, faster Ember "
           "spending bought."))

N.append(node(
    "magmatic", "Magmatic",
    "Increases all damage you deal by 10%.",
    5, 1,
    effects={"all_damage": 0.10},
    connect=["pyroclasm"],
    source="CoA's own description for this node is the unresolved token "
           "'$8a' - the Builder payload never expands it - so there is no "
           "verbatim text to port and this is NOT a faithful copy. Named from "
           "CoA's own title and built as flat damage. Flagged so a later pass "
           "can correct it if the real text surfaces; the same situation as "
           "Brewing's Mixologist ('$40'), Lightning's Umbral Glaive ('$42'), "
           "Wind's Tempest Calling ('$4c') and Venom's Rot Lich ('$b2')."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "pyroclasm", "Pyroclasm",
    "Teaches Pyroclasm, and your damage-over-time spells deal 30% more.",
    6, 0,
    effects={"unlock_ability": "pyromancer_pyroclasm",
             "dot_damage": 0.30},
    source="LOAD-BEARING UNLOCK: pyromancer_pyroclasm carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. Kept at tier 6 as the shipped tree had it, completing "
           "Pyromancer's 4/5/6 gated-ability pattern. The dot damage is added "
           "because a capstone that only grants an ability is thin - the "
           "ability carries its own tooltip, and this way the node also pays "
           "off every dot the tree has been stacking. A capstone granting an "
           "ability AND a real effect is the shape used on Lightning's Ride "
           "the Lightning too."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# Cataclysmic Power is authored at its PER-RANK value with CoA's own 3 ranks,
# so the policy skips it. Author the CEILING at one rank everywhere else and
# let the policy divide - hand-authoring a ceiling at ranks=3 triples it,
# which is the bug that shipped on Guardian Vanguard's Iron Guardian.
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
    missing = GATED - unlocks
    assert not missing, (
        f"these abilities carry requires_talent and this tree is their only "
        f"unlock - dropping the node makes them unobtainable forever: "
        f"{sorted(missing)}")
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Pyromancer Incineration: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
