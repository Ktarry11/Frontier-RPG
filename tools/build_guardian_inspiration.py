#!/usr/bin/env python3
"""Rebuild Guardian's Inspiration tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_guardian_inspiration.py [--check]

SOURCE: data/reference/coa_worksheets/guardian.md and
data/reference/coa/guardian.json - 42 real Inspiration talents from
Ascension's own CoA Builder payload. Role: Support.

THE STRUCTURAL PROBLEM, AND KYLE'S CALL ON IT (5 Nov 2026). Inspiration is
CoA's support spec and more than twenty of its forty-two talents are party
or raid auras. A talent effect cannot reach an ally - get_talent_effects()
aggregates only the character's own stances, forms and trees - and neither
can a proc payload, whose apply_effect lands on the caster or the
triggering target and nowhere else.

But a party ABILITY can. target_type "party" resolves to every living ally
(abilities.py:2064) and the UI passes living_allies() as the target list
(ui/screens/combat_screen.py:594), so the Guardian and the whole party are
covered; with no party context it degrades to the caster, so a solo fight
still works.

The Guardian had none. Song of Steel, Inspiring Presence, Standard of
Valiance and Champion's Presence are all explicitly ally-facing in CoA's
own text and had all been authored as target_type "self" by an earlier
pass, so the support spec buffed nobody but the Guardian. Kyle chose to
convert them rather than build a selfish Inspiration, so this tree is
written on top of four genuinely party-wide abilities: the talents here
make those auras bigger, longer and cheaper, which is how a support spec
supports in a turn-based game.

Hero's March and Fearless stay self - both are self-buffs in CoA too.

WHAT STILL CANNOT BE BUILT, per node: Sound of War as a TRIGGER (CoA
treats "triggering a Sound of War" as an event; here it is an enemy_aoe
ability, so five talents hang off its CAST instead); the Banners as
wearable items; "your next N casts" empowerments; and dispels, immunities
and movement, none of which have talent-reachable keys.

DEAD KEYS THIS TREE WANTED. energy_regen, energy_regen_pct and
resource_regen_pct are all read by nothing, which takes A Hero's Tale as
written - there is no per-turn resource regeneration key anywhere, the
same wall that trimmed the Witch Doctor's Spirits.

CONVENTIONS, which do not agree with each other:
  attack_power_pct, armor_pct, agility_pct, stamina_pct   percentage POINTS
  all_damage, physical_damage, dot_damage, crit_damage_physical,
    ability_*_damage, ability_*_crit_damage               FRACTION
  crit_chance_physical, haste, hit_rating, ability_*_crit PERCENT
  magic_damage_taken_pct / damage_dealt_pct inside a status effect:
    divided by 100, POSITIVE INCREASES damage taken
  bare damage_taken_pct inside a status effect            read RAW
  block_value_pct    FRACTION on BOTH sides
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/guardian_inspiration.json"

#: The four abilities converted to target_type "party" on 5 Nov 2026 so
#: this spec has something ally-facing to empower. See the module docstring.
AURAS = ["guardian_song_of_steel", "guardian_inspiring_presence",
         "guardian_standard_of_valiance", "guardian_champions_presence"]

#: CoA's "Ballads". Frontier has Ballad of Steel as the damaging song and
#: Song of Battle as the sustained one.
BALLADS = ["guardian_ballad_of_steel", "guardian_song_of_battle"]

TREE = {
    "spec_name": "Guardian Inspiration",
    "tree_id": "guardian_inspiration",
    "description": ("Ballads and banners - a battle bard whose songs carry "
                    "the whole party."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 42 real CoA Inspiration talents (role "
        "Support). More than twenty are party or raid auras, and a talent "
        "effect or proc payload can never reach an ally - but a party "
        "ABILITY can. The Guardian's four ally-facing abilities (Song of "
        "Steel, Inspiring Presence, Standard of Valiance, Champion's "
        "Presence) had all been authored as target_type 'self', so the "
        "support spec supported nobody; Kyle's call was to convert them to "
        "'party' rather than build a selfish Inspiration. This tree "
        "empowers those four auras. Dead keys it wanted: energy_regen, "
        "energy_regen_pct, resource_regen_pct - no per-turn resource "
        "regeneration key exists at all."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"guardian_inspiration_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"guardian_inspiration_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "a_heros_tale", "A Hero's Tale",
    "Reduces the Energy cost of your songs and presences by 20%.",
    0, -5,
    effects={f"ability_{a}_cost_pct": 0.20 for a in AURAS},
    connect=["leading_the_march"],
    source="CoA over 2 ranks: 'Increases your Energy regeneration by 10%.' "
           "THERE IS NO RESOURCE REGENERATION KEY - energy_regen, "
           "energy_regen_pct and resource_regen_pct are all read by nothing. "
           "Rerouted to the cost of the four party auras, which is what more "
           "Energy buys a support: the auras up more often. POSITIVE "
           "reduces."))

N.append(node(
    "leading_the_march", "Leading the March",
    "Increases your attack power and armour by 8%.",
    0, -3,
    effects={"attack_power_pct": 8.0, "armor_pct": 8.0},
    connect=["dragonslayer"],
    source="CoA over 2 ranks: 'Increases your attack power and total Armor "
           "by 4%.' Doubled for the two ranks and authored as the "
           "full-investment ceiling. Both keys take percentage POINTS."))

N.append(node(
    "dragonslayer", "Dragonslayer",
    "Increases your Agility by 5%.",
    0, -1,
    effects={"agility_pct": 5.0},
    connect=["spirit_of_battle"],
    source="CoA verbatim: 'Increases your Agility by 5%.' Percentage "
           "POINTS."))

N.append(node(
    "wars_muse", "War's Muse",
    "Increases your critical strike damage by 20%.",
    0, 1,
    effects={"crit_damage_physical": 0.20},
    connect=["spirit_of_battle"],
    source="CoA verbatim: 'Increases your critical damage by 20%.' Routed to "
           "the physical side, which is every ability this spec uses. "
           "crit_damage_physical is a FRACTION, while crit_chance_physical "
           "beside it is a PERCENT."))

N.append(node(
    "spirit_of_battle", "Spirit of Battle",
    "Increases your chance to hit with all attacks by 3%.",
    0, 3,
    effects={"hit_rating": 3.0},
    connect=["battle_bard"],
    source="CoA verbatim: 'Increases chance to hit with all spells and "
           "attacks by 1% for you and party and raid members. Does not stack "
           "with similar effects.' A TALENT cannot reach an ally even now "
           "that the spec has party abilities - get_talent_effects() reads "
           "only the character's own trees - so the hit lands on the "
           "Guardian and the description says 'your'. Priced at 3% rather "
           "than CoA's 1%, since it covers one character instead of five."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "battle_bard", "Battle Bard",
    "Increases the damage of your Ballads by 15%.",
    1, -4,
    effects={f"ability_{a}_damage": 0.15 for a in BALLADS},
    connect=["minstrel"],
    source="CoA verbatim: 'Increases the damage of your Ballads by 15%.' "
           "CoA's Inspiring Leader node transforms Pulverize and Broad Sweep "
           "into Ballads, which no key does - nothing replaces one ability "
           "with another - so 'Ballads' is read as the two songs Frontier "
           "actually has: Ballad of Steel (enemy damage) and Song of Battle "
           "(enemy_aoe dot)."))

N.append(node(
    "soundwave", "Soundwave",
    "Increases the damage of Sound of War by 15%.",
    1, -2,
    effects={"ability_guardian_sound_of_war_damage": 0.15},
    connect=["minstrel"],
    source="CoA verbatim. Sound of War is an enemy_aoe ability in Frontier "
           "rather than CoA's triggered event, which is why five talents in "
           "this tree hang off its cast instead of off 'triggering' it."))

N.append(node(
    "powerful_voice", "Powerful Voice",
    "Increases the critical strike chance of your Ballads by 10%.",
    1, 0,
    effects={f"ability_{a}_crit": 10.0 for a in BALLADS},
    connect=["into_the_fray"],
    source="CoA verbatim. ability_*_crit is a PERCENT, unlike "
           "ability_*_crit_damage, which is a FRACTION - both appear in this "
           "tree."))

N.append(node(
    "veteran_of_the_third_war", "Veteran of the Third War",
    "Blocking an attack restores some of your health.",
    1, 2,
    proc={"trigger": "on_block", "chance": 100, "icd": 0,
          "heal_flat": 60},
    connect=["dissonance"],
    source="CoA verbatim: 'You now restore 3% of your base health whenever "
           "you block an attack.' on_block is a live trigger and heal_flat a "
           "live payload, so this ports in shape. The amount is flat because "
           "no payload reads a percentage of maximum health - the same limit "
           "that made the Witch Doctor's Spiritual Devotee a flat mana "
           "grant."))

N.append(node(
    "minstrel", "Minstrel",
    "Casting a Ballad quickens you, raising your haste by 3% per stack for 3 "
    "turns, stacking 3 times.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": BALLADS,
          "apply_effect": {"effect_id": "guardian_minstrel",
                           "name": "Minstrel", "effect_type": "buff",
                           "duration": 3, "max_stacks": 3,
                           "stat_mods": {"haste": 3.0},
                           "on_target": False}},
    connect=["dissonance"],
    source="CoA verbatim: 'Casting a Ballad now increases your haste by 3%, "
           "stacking 3 times, for 8 sec.' PORTS EXACTLY - CoA's 3%, 3 "
           "stacks, and 8 sec is 3 turns. One of the few nodes in this spec "
           "that needed no translation at all, because it is the one that "
           "buffs only the Guardian."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "into_the_fray", "Into The Fray",
    "Sound of War carries you forward, granting an extra attack once per "
    "turn.",
    2, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["guardian_sound_of_war"],
          "extra_attack": True},
    connect=["knights_song"],
    source="CoA verbatim: 'Triggering a Sound of War now grants you an "
           "additional auto attack on your next swing.' extra_attack is a "
           "live boolean payload. CoA treats Sound of War as a triggered "
           "event with its own hooks; Frontier has it as an enemy_aoe "
           "ability, so this fires on the cast. 1-turn internal cooldown so "
           "a multi-target cast does not grant several extra attacks."))

N.append(node(
    "pied_piper", "Pied Piper",
    "Increases the damage of Ram by 20%.",
    2, -2,
    effects={"ability_guardian_ram_damage": 0.20},
    connect=["knights_song"],
    source="CoA verbatim: 'Triggering a Sound of War now increases damage of "
           "your next Ram by 20% for 15 sec.' No payload empowers a 'next' "
           "specific cast - the same wall as the Witch Doctor's Sen'jin's "
           "Presence and Dambala's Lethality - so CoA's 20% is permanent. "
           "Stronger than CoA's, stated rather than hidden."))

N.append(node(
    "knights_song", "Knight's Song",
    "Your Song of Steel rings a turn longer and raises your armour by 15%.",
    2, 0,
    effects={"ability_guardian_song_of_steel_duration": 1,
             "armor_pct": 15.0},
    connect=["banner_of_conquest"],
    source="CoA verbatim: 'Casting a Ballad now grants allies Knight's Song. "
           "Emanate an aura for 10 seconds that increases the Armor of party "
           "and raid members by 400.' A proc cannot apply an effect to "
           "allies, so the armour aura cannot be created from a talent. But "
           "Song of Steel IS now a party ability, so extending its duration "
           "is a real party benefit - the longest lever a talent has on an "
           "ally. The armour itself lands on the Guardian. The small integer "
           "duration keeps this node out of the rank policy's reach."))

N.append(node(
    "dissonance", "Dissonance",
    "Sound of War has a 25% chance to leave enemies taking 5% more magic "
    "damage for 3 turns.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "ability_filter": ["guardian_sound_of_war"],
          "apply_effect": {"effect_id": "guardian_dissonance",
                           "name": "Dissonance", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"magic_damage_taken_pct": 5.0},
                           "on_target": True}},
    connect=["banner_of_swiftness"],
    source="CoA verbatim: 'Damage dealt by Sound of War now has a 25% chance "
           "to reduce enemies' resistances by 75 and increases their Magic "
           "damage taken by -2% for 8 seconds.' CoA's 25% kept and 8 sec is "
           "3 turns. The flat resistance reduction has no key, so it is "
           "folded into the magic damage taken, raised to 5% to cover both "
           "halves. INSIDE A STATUS EFFECT magic_damage_taken_pct is divided "
           "by 100 and POSITIVE INCREASES damage taken - so a debuff is "
           "positive here, the opposite sign to the same key as a talent "
           "effect, where negative reduces. CoA's own '-2%' is written as a "
           "reduction but described as an increase; the increase is what a "
           "support wants."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "banner_of_conquest", "Banner of Conquest",
    "Your Champion's Presence lasts a turn longer, and your critical strike "
    "chance rises by 5%.",
    3, -4,
    effects={"ability_guardian_champions_presence_duration": 1,
             "crit_chance_physical": 5.0},
    connect=["stand_your_ground"],
    source="CoA verbatim: 'Attach a Banner of Conquest to your back, "
           "increasing the critical strike chance of party and raid members "
           "within 40 yds by 5%. Does not stack with similar effects.' A "
           "wearable banner is not a mechanic here and a talent cannot give "
           "allies crit. Champion's Presence is now a party ability, so its "
           "duration is the real party lever; the 5% crit lands on the "
           "Guardian at CoA's own number."))

N.append(node(
    "banner_of_swiftness", "Banner of Swiftness",
    "Your Song of Steel lasts a turn longer, and your haste rises by 5%.",
    3, -2,
    effects={"ability_guardian_song_of_steel_duration": 1, "haste": 5.0},
    connect=["stand_your_ground"],
    source="CoA verbatim: 'Attach a Banner of Swiftness to your back, "
           "increasing the haste of party and raid members within 40 yds by "
           "5%.' Same treatment as Banner of Conquest above. CoA's Banner "
           "Boy node ('+5% haste and +8% to Line Formation's movement "
           "speed') is folded in here, its movement half dropped - there is "
           "no positioning in this engine."))

N.append(node(
    "reverberations", "Reverberations",
    "Ram sets the air ringing, dealing magic damage over 2 turns.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_ram"],
          "apply_effect": {"effect_id": "guardian_reverberations",
                           "name": "Reverberations", "effect_type": "dot",
                           "duration": 2, "potency": 30,
                           "damage_school": "arcane", "on_target": True}},
    connect=["echoes_of_war"],
    source="CoA verbatim: 'Casting Ram now causes your next 3 melee attacks "
           "to deal an additional 30 + 10% AP Magic damage for 10 seconds.' "
           "No charge counter exists and no payload empowers the next N "
           "attacks, so the extra magic damage is paid as a dot on the "
           "target instead - the same total, over turns. CoA's 'Magic' is "
           "typed arcane, the engine's generic magic school."))

N.append(node(
    "elegant_combat", "Elegant Combat",
    "Casting a Ballad has a 20% chance to ready Ram again.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "ability_filter": BALLADS,
          "reset_cooldown": ["guardian_ram"]},
    connect=["echoes_of_war"],
    source="CoA verbatim: 'Casting a Ballad has a 20% chance to remove the "
           "cost of the next Ram and increase its critical chance by 10%.' "
           "Neither a free next cast nor a one-shot crit bonus is "
           "expressible, so the 20% buys a full cooldown reset instead - "
           "reset_cooldown as a BARE LIST - which is worth more than a free "
           "cast and is the honest nearest thing. CoA's 20% kept."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "stand_your_ground", "Stand Your Ground!",
    "Your Standard of Valiance stands a turn longer, and you take 10% less "
    "physical damage.",
    4, -3,
    effects={"ability_guardian_standard_of_valiance_duration": 1,
             "physical_damage_taken_pct": -0.10},
    connect=["legion_commander"],
    source="CoA verbatim: 'While standing in your Standard of Valiance, your "
           "allies' Physical damage taken is reduced by 10%.' THIS IS THE "
           "NODE THAT MOST NEEDED THE PARTY CONVERSION: Standard of Valiance "
           "already carries physical_damage_taken_pct -12 in its own "
           "stat_mods, and now that it targets the party, that mitigation "
           "reaches allies - so extending its duration delivers exactly what "
           "CoA promises. The 10% on this node is the Guardian's own share. "
           "AS A TALENT EFFECT physical_damage_taken_pct is a FRACTION where "
           "NEGATIVE reduces; inside a status effect it is divided by 100 "
           "and positive increases."))

N.append(node(
    "warbringers_manuscript", "Warbringer's Manuscript",
    "Your critical strikes bring Hero's March a turn closer to ready.",
    4, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "reset_cooldown": {"abilities": ["guardian_heros_march"],
                             "turns": 1}},
    connect=["legion_commander"],
    source="CoA verbatim: 'Critical strikes now reduce the cooldown of "
           "Hero's March by -1 sec.' Ports in shape; 1 sec becomes a turn, "
           "which is a buff relative to CoA because a fraction of a turn "
           "cannot be expressed, so a 1-turn internal cooldown holds it to "
           "once per turn."))

N.append(node(
    "bards_manuscript", "Bard's Manuscript",
    "Reduces the cooldown of Hero's March by 40%.",
    4, 1,
    effects={"ability_guardian_heros_march_cooldown_pct": 0.40},
    connect=["war_drums"],
    source="CoA verbatim: 'Reduces the cooldown of Hero's March by -60 sec.' "
           "Expressed as a percentage because CoA's 60 seconds is measured "
           "against a 2-minute cooldown that does not exist here in those "
           "units. POSITIVE reduces, so CoA's minus sign is dropped."))

N.append(node(
    "echoes_of_war", "Echoes of War",
    "Sound of War echoes, striking again for magic damage.",
    4, 3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_sound_of_war"],
          "damage_flat": 75, "school": "arcane"},
    connect=["war_drums"],
    source="CoA verbatim: 'Triggering a Sound of War now grants Echoes of "
           "War to nearby allies for 8 sec. Next direct ability or spell "
           "deals 15% of their damage as additional Magic Damage.' A proc "
           "cannot apply an effect to allies and nothing empowers an ally's "
           "next cast, so the ally-facing half is impossible. Built as the "
           "Guardian's own echo - CoA's extra magic damage, dealt directly. "
           "damage_flat with a school is a live payload."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "legion_commander", "Legion Commander",
    "Increases the damage of Harrowing Melody by 50% and of your Ballads by "
    "30%.",
    5, -3,
    effects={"ability_guardian_harrowing_melody_damage": 0.50,
             **{f"ability_{a}_damage": 0.30 for a in BALLADS}},
    connect=["inspiring_presence_mastery"],
    source="CoA verbatim: 'The damage increase of Harrowing Melody now "
           "affects an additional 2 Ballad casts and guarantees them to "
           "critically strike and deal 100% more damage.' A GUARANTEED CRIT "
           "HAS NO KEY - crit at 100 would be a permanent stat, not a "
           "one-shot - and 'an additional 2 casts' needs a charge counter. "
           "Both halves are paid as flat damage on the abilities involved, "
           "which is what the combination delivered."))

N.append(node(
    "war_drums", "War Drums",
    "Sound of War has a 40% chance to beat twice, striking again for magic "
    "damage.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 40, "icd": 1,
          "ability_filter": ["guardian_sound_of_war"],
          "damage_flat": 90, "school": "arcane"},
    connect=["inspiring_presence_mastery"],
    source="CoA verbatim: 'Adds 5% to the value of Echoes of War. In "
           "addition, performing a Sound of War now has a 40% chance to echo, "
           "striking an additional time after 0.5 sec. Can only occur once "
           "per sec.' The second half ports - CoA's 40%, and the 1-turn "
           "internal cooldown covers 'once per sec'. The first half would "
           "need a talent to edit another talent's payload, which no key "
           "does, so it is folded into this node's own damage. Deliberately "
           "stacks with Echoes of War at tier 4, as CoA's do."))

N.append(node(
    "field_commander", "Field Commander",
    "Your Song of Steel and Inspiring Presence each last a turn longer, and "
    "all your damage rises by 8%.",
    5, 1,
    effects={"ability_guardian_song_of_steel_duration": 1,
             "ability_guardian_inspiring_presence_duration": 1,
             "all_damage": 0.08},
    connect=["inspiring_presence_mastery"],
    source="CoA verbatim: 'Placing a Standard causes your next Song of Steel "
           "to unleash an additional unique effect. Spellwarding... Might... "
           "Rallying... Recovery...' A random or chosen pick from a table of "
           "four party auras is not expressible: apply_effect takes one "
           "effect or a list but nothing chooses among them, and a talent "
           "cannot reach an ally regardless. Rebuilt as duration on the two "
           "party auras CoA names here plus the Guardian's own damage. The "
           "small integer durations keep this node out of the rank policy."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "inspiring_presence_mastery", "Inspiring Presence",
    "Your presences and standards all last a turn longer, and your attack "
    "power rises by 15%.",
    6, 0,
    effects={**{f"ability_{a}_duration": 1 for a in AURAS},
             "attack_power_pct": 15.0},
    source="CoA verbatim: 'Emanate an aura around you for 15 seconds, "
           "causing allied players within 100 yds to deal 35% AP additional "
           "damage as Holy damage when they deal direct damage. Applies "
           "Exhaustion, preventing you from benefiting from similar effects "
           "for 1 minute.' The ally damage rider cannot be created by a "
           "talent. THE CAPSTONE IS THE PAYOFF OF THE PARTY CONVERSION: a "
           "turn on all four party auras at once, which on a support is four "
           "party-wide buffs held a third longer - attack power from Song of "
           "Steel, crit from Inspiring Presence, physical mitigation from "
           "Standard of Valiance and haste from Champion's Presence. That is "
           "a real support capstone rather than a self-buff, which it could "
           "not have been before those four abilities were converted. "
           "Exhaustion has no mechanism and is dropped. CoA's Voice of an "
           "Angel node (reset Liberation, Harrowing Melody and Hero's March) "
           "is not built - Frontier already has that as an ability, and a "
           "talent resetting three cooldowns at once needs an active, not a "
           "passive."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations.
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
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Guardian Inspiration: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
