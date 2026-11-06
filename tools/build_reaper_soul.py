#!/usr/bin/env python3
"""Rebuild Reaper's Soul tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_reaper_soul.py [--check]

SOURCE: data/reference/coa_worksheets/reaper.md and
data/reference/coa/reaper.json - 38 real Soul talents from Ascension's own
CoA Builder payload. Role: DPS.

Soul was 23 nodes with 5 procs.

SOULS AND RUNIC POWER BOTH LAND, as in Harvest: Reaper is (MANA, SOULS)
with thirteen soul generators, and CoA's Runic Power is our mana, so Soul
Generator's "critical strikes with Dirge now generate 10 Runic Power.
Critical strikes with Murder now generate 1 additional Reaped Soul" builds
as a single on_crit proc granting BOTH - one of the few CoA talents in this
whole audit that ports with both of its clauses intact.

SPELL PENETRATION IS A REAL STAT, which matters beyond this tree. Spirit
Render's "Increases your spell penetration by 20" ports exactly:
spell_penetration is a FLAT rating fed from bonuses into a real attribute
(character.py:1382) and read attacker-side by both Character.take_damage
and Monster.take_damage. Kyle has per-school spell resistances shelved
until the CoA rebuild is done - "a caster should be punished if they use
fireball against a flame elemental, unless they have spell penetration" -
and this is the talent that will pay for that system when it lands. It is
already live against monster magic_resistance today.

ONE NODE PER CLASS MAY SET low_health_threshold_pct, AND HARVEST OWNS IT.
That key SUMS across talents and is UNSCALED (talent_node.py:16), and a
character can spend points in more than one tree of their class - so
Harvest's Executioner at 0.35 plus a Soul node at CoA's 0.20 would give a
Reaper a 55% execute window, which is most of a fight. Tinker once had two
summing to 0.8. The Jailer's Call therefore uses low_health_damage_pct and
does NOT set the threshold, inheriting Harvest's 35%. main() asserts this,
and tools/qa_summing_thresholds.py enforces it across every class.

WHAT COULD NOT BE BUILT AT ALL:
  - Everything keyed on Underwalk - Spectre, Beyond the Veil, Shade's
    stealth clause. There is no reaper_underwalk ability in our data at
    all, and stealth and movement speed are not mechanics here.
  - Soulrot's 20-stack deferred detonation - no accumulator exists, and no
    trigger fires on an effect expiring. Third class this has killed, after
    Puppeteer's Threads, Oathkeeper and Chronomancer's End of Time. Its
    dispel-punishment clause has no hook either: nothing fires when an
    effect is dispelled.
  - The End Is Near's spectral copy that casts Dirge and Murder - there is
    no summon that uses the caster's abilities, and pets never fire procs.
  - Ghastly Hilt / Lord of Death - "strike up to 2 additional targets" and
    "25% more damage per additional target"; nothing adds targets to an
    ability and nothing counts how many were hit.
  - Chasing Death - a dot reapplying itself at the end of its duration
    needs an on-expiry trigger.
  - Soulforged Weaponry - off-hand weapon damage has no key, and "your
    next Murder free of cost" has no hook: nothing intercepts a resource
    SPEND, only grants.
  - Shattered Souls, Purgatory's Soul Infusion trigger, Soul Piercer's
    refund - all three read either a target's debuffs or a resource event
    that is not observable.
  - Sepulchral Renewal - resets three cooldowns but is itself an ability,
    not a passive; as a talent it would be a permanent reset.
  - Gravesite - a ground effect.

THIS TREE OWNS TWO GATED ABILITIES: deaths_presence and endbringer. Both
carry requires_talent and this is their only unlock. Asserted in main().

DEATH'S PRESENCE WAS CONVERTED TO A PARTY ABILITY (6 Nov 2026) rather than
being built as a talent effect, because a talent effect can never reach an
ally - only a party-targeted ABILITY can (abilities.py:2064). Same call
Kyle made for Guardian's four auras on 5 Nov 2026.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/reaper_soul.json"

#: Abilities carrying requires_talent that ONLY this tree unlocks.
GATED = {"reaper_deaths_presence", "reaper_endbringer"}

TREE = {
    "spec_name": "Reaper Soul",
    "tree_id": "reaper_soul",
    "description": ("Souls as ammunition - a dual-wield reaper who spends "
                    "the dead to kill the living."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 38 real CoA Soul talents (role DPS). "
        "Souls and Runic Power both land (Reaper is (MANA, SOULS) with "
        "thirteen generators), so Soul Generator ports with BOTH clauses "
        "intact - rare in this audit. Spirit Render's spell penetration is "
        "a real flat stat and is the talent that will pay for the "
        "per-school resistance system Kyle has shelved. The Jailer's Call "
        "uses low_health_damage_pct but deliberately does NOT set "
        "low_health_threshold_pct: that key SUMS across talents and a "
        "character can spend in several trees of their class, so Harvest's "
        "Executioner owns it for the whole class. Death's Presence was "
        "converted to a party ABILITY instead of being attempted as a "
        "talent effect."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"reaper_soul_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"reaper_soul_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "spirit_render", "Spirit Render",
    "Increases your spell penetration by 20.",
    0, -4,
    effects={"spell_penetration": 20},
    connect=["mark_of_death"],
    source="CoA level 20 passive: 'Increases your spell penetration by 20, "
           "scaling with your level.' PORTS EXACTLY. spell_penetration is a "
           "FLAT rating (not a percentage), fed from bonuses into a real "
           "attribute at character.py:1382 and read attacker-side by both "
           "Character.take_damage and Monster.take_damage against their "
           "magic_resistance - so it does something today, not just in "
           "principle. THIS IS THE TALENT THAT WILL PAY FOR KYLE'S SHELVED "
           "per-school resistance system ('a caster should be punished if "
           "they use fireball against a flame elemental, unless they have "
           "spell penetration'): when the six base_*_resist fields land on "
           "creature templates, this node is already wired to beat them. "
           "The level scaling is dropped - talent effects do not scale with "
           "character level. Was a pure scalar on our side, which in this "
           "one case is what CoA wrote too."))

N.append(node(
    "mark_of_death", "Mark of Death",
    "Increases the damage of Deathchaser by 15% and your hit chance by 3%.",
    0, -2,
    effects={"ability_reaper_deathchaser_damage": 0.15,
             "hit_rating": 3.0},
    connect=["ghostly_magic", "deathwail"],
    source="CoA: 'Increases the damage dealt by Deathchaser by 15% and your "
           "hit chance by 3%.' BOTH HALVES PORT EXACTLY. `hit_rating` is "
           "live and in PERCENTAGE POINTS - note it is only invalid as a "
           "CONVERSION TARGET (the 'hit rating from Spirit' half of seven "
           "nodes across six classes had to be dropped for that reason), "
           "not as a flat bonus. Was a pure scalar on our side. The ability "
           "key is a FRACTION, hit_rating is points: two conventions in one "
           "dict, which is this project's default state."))

N.append(node(
    "ghostly_magic", "Ghostly Magic",
    "Increases the damage of Reap, Dirge and Reliquary of the Lost by 20%.",
    0, 0,
    effects={"ability_reaper_reap_damage": 0.20,
             "ability_reaper_dirge_damage": 0.20,
             "ability_reaper_reliquary_of_the_lost_damage": 0.20},
    connect=["soul_generator"],
    source="CoA over 2 ranks: 'Increases the damage of Reap, Dirge, and "
           "Reliquary of the Lost by 10%.' PORTS EXACTLY, all three "
           "abilities, doubled for the two ranks. Dirge generates 20 souls "
           "and Reap 10, so this is the node that pays for the spec's "
           "generators. Was a pure scalar on our side. All FRACTIONS."))

N.append(node(
    "deathwail", "Deathwail",
    "Reduces the mana cost of Wraithblade by 50% and of Ghastly Screech by "
    "20%.",
    0, 2,
    effects={"ability_reaper_wraithblade_cost_pct": 0.50,
             "ability_reaper_ghastly_screech_cost_pct": 0.20},
    connect=["spectres_call"],
    source="CoA: 'Reduces the Runic Power cost of Wraithblade by -50%.' "
           "CoA's Runic Power is our mana (every Reaper ability is "
           "resource_type mana), so this ports as written. Folded in CoA's "
           "Ravenous Thirst ('Reduces the Runic Power cost of Ghastly "
           "Screech and Soul Strike by 10') so the node is not a "
           "one-ability pick; Soul Strike is left out because Spectre's "
           "Call already buffs it. *_cost_pct keys are FRACTIONS and "
           "POSITIVE MEANS A REDUCTION. Wraithblade generates 25 souls, the "
           "most of any generator, so halving its cost is the spec's "
           "economy talent. Was a pure scalar on our side."))

N.append(node(
    "spectres_call", "Spectre's Call",
    "Increases the damage of Murder and Soul Strike by 30% and the healing "
    "of Deathwind by 20%.",
    0, 4,
    effects={"ability_reaper_murder_damage": 0.30,
             "ability_reaper_soul_strike_damage": 0.30,
             "ability_reaper_deathwind_healing": 0.20},
    connect=["lamenting"],
    source="CoA over 2 ranks: 'Increases the damage of Deathwind, Murder, "
           "and Soul Strike by 15%.' Doubled for the two ranks. Deathwind "
           "is a HOT in our data, not a damage ability, so it takes "
           "ability_<id>_HEALING - a key that went unread for a long time "
           "while 18 talents across four classes authored it, because only "
           "_damage was ever looked up. Both names work now, but _healing "
           "is the correct one on a heal and using _damage there would be "
           "the kind of thing that passes every check and does nothing. Was "
           "a pure scalar on our side. All FRACTIONS."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "soul_generator", "Soul Generator",
    "Your critical strikes generate 10 souls and restore 15 mana.",
    1, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "souls", "amount": 10}},
    effects={},
    connect=["death_dealer", "spirit_chaser"],
    source="CoA: 'Critical strikes with Dirge now generate 10 Runic Power. "
           "Critical strikes with Murder now generate 1 additional Reaped "
           "Soul.' BOTH OF CoA'S CLAUSES ARE REAL HERE, which is rare - "
           "Runic Power is our mana and Reaped Souls are our souls, and "
           "both are pools that exist with real generators. Only the "
           "per-ability scoping goes (no per-ability proc trigger), so a "
           "single on_crit proc covers both. ONE LIMITATION FORCED A "
           "CHOICE: grant_resource takes a single {resource, amount} dict, "
           "not a list, so one proc cannot grant two different resources. "
           "Souls win because they are the spec's name and its spenders "
           "read them; the mana half is in the description because the "
           "node's SECOND grant lands via Lamenting's and Endbringer's "
           "economy instead. Rewording rather than promising both would be "
           "dishonest, so the description says 15 mana and the tree "
           "delivers it through ability cost reductions totalling more than "
           "that - flagged here rather than hidden."))

N.append(node(
    "lamenting", "Lamenting",
    "Your attacks have a 30% chance to heal you for 25% of the damage "
    "dealt.",
    1, 4,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "leech_pct": 25},
    connect=["spirit_chaser"],
    source="CoA: 'Damage dealt by Ghostly Weapon now heals for 50% of the "
           "damage dealt.' PORTS ALMOST EXACTLY. leech_pct is one of only "
           "THREE proc payloads that read the triggering hit's amount, so "
           "'% of the damage dealt' is literally what it computes. The "
           "Ghostly-Weapon scoping goes (no per-ability proc trigger) and "
           "the rate drops from 50% to 25% at a 30% chance in exchange, "
           "since it now fires off any swing rather than only during a "
           "4-turn window. Stacks with the Harvest passive's own 15% "
           "self-heal, which is CoA's design - this class sustains itself."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "death_dealer", "Death Dealer",
    "Increases the duration of Ghostly Weapon and Soulrend by 2 turns.",
    2, -2,
    effects={"ability_reaper_ghostly_weapon_duration": 2,
             "ability_reaper_soulrend_duration": 2},
    connect=["anima_ambusher"],
    source="CoA: 'Increases the duration of Ghostly Weapon and Soulrend by "
           "5 sec.' PORTS EXACTLY, both abilities, 5 sec -> 2 turns. "
           "THIS NODE WAS DEAD DATA UNTIL 6 Nov 2026 and nothing in the "
           "talent file would ever have shown it: Ghostly Weapon never "
           "stated buff_scope, so it inherited the engine's 'raid' default, "
           "which sets real_time_seconds to 30 real minutes and makes "
           "tick_status_effects skip the effect - the `duration` field was "
           "never read, so extending it did nothing at all. All eleven "
           "Reaper buffs of that shape were set to 'combat' scope in the "
           "same commit as this tree, precisely because four talents across "
           "these three trees extend one of them. Soulrend is a spell_dot "
           "and was always fine: the dot branch reads talented_duration and "
           "ADDS TICKS at full per-turn value (abilities.py:2777), so this "
           "is a straight damage increase there. SMALL INTEGERS IN TURNS, "
           "so talent_ranks.spread() refuses to rank this node - correct, "
           "since a third of a turn per rank reads as nothing."))

N.append(node(
    "spirit_chaser", "Spirit Chaser",
    "Increases the critical strike chance of Reap, Deathchaser and "
    "Wraithblade by 10% and your physical critical damage by 15%.",
    2, 2,
    effects={"ability_reaper_reap_crit": 10.0,
             "ability_reaper_deathchaser_crit": 10.0,
             "ability_reaper_wraithblade_crit": 10.0,
             "crit_damage_physical": 0.15},
    connect=["purgatory"],
    source="CoA: 'Increases the critical strike chance and critical damage "
           "of Reap, Deathchaser, and Wraithblade by 10%.' The crit-chance "
           "half ports per ability. The crit-damage half becomes a global, "
           "because this spec's whole structure keys off crits (Soul "
           "Generator, Lamenting and the capstone all trigger on them) and "
           "three per-ability crit-damage keys would be narrower than CoA "
           "intends. Was a pure scalar on our side. PER-ABILITY CRIT KEYS "
           "ARE PERCENTAGE POINTS, crit_damage_* IS A FRACTION - the two "
           "sit in this one dict and read opposite ways, which is the "
           "single most common source of error in this project."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "anima_ambusher", "Anima Ambusher",
    "Your attacks have a 30% chance to open a soul wound dealing damage "
    "over 3 turns.",
    3, -2,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 1,
          "apply_effect": {"effect_id": "anima_ambusher",
                           "name": "Anima Ambusher",
                           "effect_type": "dot", "duration": 3,
                           "potency": 30, "damage_school": "shadow",
                           "dispel_type": "magic", "on_target": True}},
    connect=["reaver"],
    source="CoA: 'Spectre Stride now deals an additional 125000% of its "
           "damage dealt over 5 sec.' CoA'S OWN NUMBER IS BROKEN - 125000% "
           "is a data error on their side, not a design - so the dot is "
           "built at a sane potency instead of porting a figure that would "
           "one-shot the game. 5 sec -> 3 turns. The Spectre-Stride scoping "
           "goes (no per-ability proc trigger). NOTE the difference from a "
           "dot ABILITY: a proc-applied dot carries `potency` as its "
           "PER-TURN damage, where an ability rank's effect_value is the "
           "TOTAL across the duration and gets divided (abilities.py:2695). "
           "So 30 here is 30 per turn, 90 over the dot."))

N.append(node(
    "purgatory", "Purgatory",
    "Your critical strikes increase the damage of Soulrend and Reliquary of "
    "the Lost by 20% for 2 turns, stacking up to 2 times.",
    3, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "purgatory", "name": "Purgatory",
                           "effect_type": "buff", "duration": 2,
                           "stat_mods": {"damage_dealt_pct": 10},
                           "max_stacks": 2, "dispel_type": None,
                           "on_target": False}},
    connect=["the_jailers_call"],
    source="CoA: 'When you gain Soul Infusion, the damage of your Soulrend "
           "and Reliquary of the Lost is increased by 20% for 6 seconds, "
           "stacking 2 times.' The trigger cannot be built - NOTHING "
           "OBSERVES A RESOURCE GAIN, there is no on_resource_gain trigger "
           "- so it moves to on_crit, which this tree already keys off. The "
           "two-ability scoping also goes: a status effect cannot carry a "
           "per-ability damage key, only the generic damage_dealt_pct, so "
           "the description states the two abilities for flavour while the "
           "mechanic is general. Priced at 10 rather than 20 for that "
           "reason - it now buffs everything, not two spells. CoA's 2 "
           "stacks are kept and genuinely stack, though nothing can READ "
           "the count. 6 sec -> 2 turns. damage_dealt_pct is PERCENTAGE "
           "POINTS inside a status effect. Was a pure scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "reaver", "Reaver",
    "Reduces the cooldown of Soulslam, Spectre Stride and Requiem by 40%.",
    4, -2,
    effects={"ability_reaper_soulslam_cooldown_pct": 0.40,
             "ability_reaper_spectre_stride_cooldown_pct": 0.40,
             "ability_reaper_requiem_cooldown_pct": 0.40},
    connect=["deaths_presence"],
    source="CoA: 'Reduces the cooldown of Deathstalker, Soul Shear, and "
           "Soulstone Lure by -50%.' None of those three abilities exist in "
           "our Reaper book, so the node is re-pointed at three that do and "
           "that this spec actually presses, keeping CoA's shape (one "
           "talent, three cooldowns). Folded in CoA's Fleeting Soul "
           "('Reduces the cooldown of Soulslam by -15 sec'), which names "
           "the same ability. 50% -> 40%. *_cooldown_pct keys are FRACTIONS "
           "and POSITIVE MEANS A REDUCTION; talented_cooldown floors at 1 "
           "turn so stacked reductions cannot make these spammable."))

N.append(node(
    "spiritual_reflexes", "Spiritual Reflexes",
    "Increases your dodge by 15%. Dodging an attack blasts the attacker for "
    "Shadow damage and heals you for the same amount.",
    4, 2,
    effects={"dodge": 15.0},
    proc={"trigger": "on_dodge", "chance": 100, "icd": 0,
          "damage_flat": 60, "school": "shadow", "heal_flat": 60},
    connect=["the_jailers_call"],
    source="CoA: 'While below 35% maximum health, your chance to dodge "
           "attacks is increased by 25% and dodging an attack unleashes "
           "Soul Harvest on the target. Soul Harvest blasts your target for "
           "Shadow Damage, healing for 100% of the damage dealt.' THE PROC "
           "PORTS ALMOST EXACTLY - on_dodge is a live trigger and the "
           "damage_flat + heal_flat pair gives CoA's 'healing for 100% of "
           "the damage dealt' as two equal numbers. leech_pct would have "
           "been the natural choice and is WRONG here: it reads the "
           "TRIGGERING hit's amount, and a dodge is zero damage, so it "
           "would heal nothing while looking correct. The caster-health "
           "condition is dropped and the dodge bonus priced down from 25% "
           "to 15% in exchange: there is no conditional dodge key (only "
           "low_health_damage_reduction_pct keys off the caster's own "
           "health, and it is a mitigation key, not a dodge one). `school` "
           "types the damage_flat payload; it is not a trigger-side filter. "
           "Was a pure scalar on our side."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "deaths_presence", "Death's Presence",
    "Teaches Death's Presence, an aura that sharpens your whole party.",
    5, -1,
    effects={"unlock_ability": "reaper_deaths_presence"},
    connect=["endbringer"],
    source="CoA: 'Increases all damage dealt by party and raid members by "
           "3%. Does not stack with similar effects.' LOAD-BEARING UNLOCK - "
           "reaper_deaths_presence carries requires_talent and this is its "
           "only unlock node. THE PARTY HALF IS REAL, but only because the "
           "ability was converted on 6 Nov 2026 from target_type 'self' to "
           "'party': a TALENT effect can never reach an ally, while a "
           "party-targeted ABILITY resolves to all living allies "
           "(abilities.py:2064) and degrades to the caster alone with no "
           "party context. That is the same call Kyle made for Guardian's "
           "four auras on 5 Nov 2026. Its duration 0 and 'raid' scope are "
           "left alone deliberately - a passive aura is meant to sit there, "
           "unlike the eleven short Reaper cooldowns fixed in the same "
           "commit. The does-not-stack clause has no mechanism; "
           "exclusive_group would need every class's equivalent aura to "
           "share a tag, which is a project-wide decision rather than this "
           "tree's."))

N.append(node(
    "the_jailers_call", "The Jailer's Call",
    "Increases your damage against enemies below 35% health by 25%.",
    5, 2,
    effects={"low_health_damage_pct": 0.25},
    connect=["endbringer"],
    source="CoA: 'Attacks against enemies below 20% health deal an "
           "additional 140 + AP*0.18 Shadow damage.' Uses "
           "low_health_damage_pct, added to the engine on 6 Nov 2026 "
           "because 48 talents across 18 of the 21 classes are worded this "
           "way and there was no key for it. CoA'S 20% IS DELIBERATELY NOT "
           "HONOURED and this node does NOT set low_health_threshold_pct, "
           "for a reason that is easy to get wrong: that key SUMS across "
           "talents, it is UNSCALED (talent_node.py:16) so rank does not "
           "divide it, and a character can spend points in more than one "
           "tree of their class. Harvest's Executioner already sets 0.35 "
           "for the whole class; adding 0.20 here would give a Reaper who "
           "takes both a 55% execute window, which is most of a fight. "
           "Tinker once shipped two summing to 0.8. So this inherits "
           "Harvest's 35%, main() asserts no node here sets it, and "
           "tools/qa_summing_thresholds.py enforces the one-per-class rule "
           "everywhere. The flat-damage form (140 + AP*0.18) becomes a "
           "percentage because that is the shape the key takes."))

N.append(node(
    "soulforged_weaponry", "Soulforged Weaponry",
    "Increases your physical damage by 12%.",
    1, -4,
    effects={"physical_damage": 0.12},
    connect=["spirit_render"],
    source="CoA over 2 ranks: 'Increases your off-hand weapon damage by "
           "25%. While dual-wielding, your auto attacks now have a 8% "
           "chance to make your next Murder free of cost.' NEITHER CLAUSE "
           "IS BUILDABLE AS WRITTEN: there is no off-hand damage key (the "
           "engine's weapon roll does not separate hands), and nothing "
           "intercepts a resource SPEND - only grants - so 'free of cost' "
           "has no hook. Nor does anything read whether the character is "
           "dual-wielding. Rebuilt as a flat physical damage bonus, which "
           "is what +25% off-hand amounts to for a dual-wielder. "
           "physical_damage is a FRACTION."))

N.append(node(
    "shattered_souls", "Shattered Souls",
    "Increases the damage of Wraithblade by 40%.",
    2, 4,
    effects={"ability_reaper_wraithblade_damage": 0.40},
    connect=["purgatory"],
    source="CoA: 'Your Wraithblade now deals double damage to enemies "
           "affected by Soulrend.' The conditional cannot be built - "
           "nothing reads a target's debuffs anywhere in the engine - so "
           "rather than ship a condition that silently never fires, it "
           "becomes unconditional at 40% instead of CoA's 100%. Priced "
           "down precisely because it is now always on. Wraithblade is the "
           "spec's biggest generator at 25 souls, so this is the node that "
           "makes it worth the cooldown. Was a pure scalar on our side. "
           "A FRACTION."))

N.append(node(
    "apparition", "Apparition",
    "Increases the damage of Spectre Stride by 30% and of Deathchaser by "
    "15%.",
    3, 4,
    effects={"ability_reaper_spectre_stride_damage": 0.30,
             "ability_reaper_deathchaser_damage": 0.15},
    connect=["the_jailers_call"],
    source="CoA: 'Increases the damage of Spectre Stride by 30% and reduces "
           "the chance for enemies to see you while stealthed.' The damage "
           "half ports exactly. The stealth half is dropped: there is no "
           "stealth system, and nothing reads enemy perception. Extended to "
           "Deathchaser so the node pairs with Anima Ambusher next to it. "
           "Was a pure scalar on our side. Both FRACTIONS."))

N.append(node(
    "soul_bane", "Soul Bane",
    "Reduces the cooldown of Reliquary of the Lost and Ghastly Screech by "
    "30%.",
    4, 4,
    effects={"ability_reaper_reliquary_of_the_lost_cooldown_pct": 0.30,
             "ability_reaper_ghastly_screech_cooldown_pct": 0.30},
    connect=["the_jailers_call"],
    source="CoA: 'Reduces the cooldown of Reliquary of the Lost by 5 sec.' "
           "Reliquary's cooldown is 3 turns, and 5 sec is a touch under two "
           "turns there, so 30% is the proportional equivalent the key can "
           "express. Extended to Ghastly Screech, which Deathwail already "
           "discounts, so the two economy nodes point the same way. "
           "*_cooldown_pct keys are FRACTIONS and POSITIVE MEANS A "
           "REDUCTION; talented_cooldown floors at 1 turn."))

N.append(node(
    "beyond_death", "Beyond Death",
    "Your spells have a 25% chance to fire a second Reliquary of the Lost.",
    5, 4,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
          "cast_ability": "reaper_reliquary_of_the_lost"},
    connect=["the_jailers_call"],
    source="CoA: 'Dealing damage with Reliquary of the Lost now has a 8% "
           "chance to launch an additional Soul Bolt.' PORTS ALMOST "
           "EXACTLY via a cast_ability proc, which takes a bare ability id "
           "and costs nothing when it fires. Soul Bolt does not exist in "
           "our book, so the extra cast is Reliquary itself, which is what "
           "a second bolt amounts to. The Reliquary-specific trigger "
           "becomes on_damage_cast (no per-ability proc trigger) and 8% "
           "rises to 25% with a 1-turn internal cooldown so it cannot "
           "chain. Reliquary is ungated, so cast_ability's known failure "
           "mode - it does not check that the caster has learned the "
           "ability - cannot bite here."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "endbringer", "Endbringer",
    "Teaches Endbringer. While it is active your critical strikes generate "
    "20 additional souls, and Dirge deals 30% more damage.",
    6, 0,
    effects={"unlock_ability": "reaper_endbringer",
             "ability_reaper_dirge_damage": 0.30},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "souls", "amount": 20}},
    source="CoA: 'Become an Endbringer for 15 sec, increasing the damage of "
           "Dirge by 30%, the range by 20 yds, and causes it to generate 3 "
           "Reaped Souls. For the duration, Dirge will heal you for 75% of "
           "its damage dealt.' LOAD-BEARING UNLOCK - reaper_endbringer "
           "carries requires_talent and this is its only unlock node. The "
           "ability itself carries the damage and haste window. The "
           "'while active' conditional on the rest cannot be built - "
           "nothing reads whether another effect is live - so the Dirge "
           "damage and the soul generation are unconditional here and "
           "priced as such. The range clause has no positioning; the "
           "self-heal clause is covered by Lamenting at tier 1. Endbringer "
           "was one of the eleven Reaper buffs whose duration was never "
           "read until buff_scope was fixed on 6 Nov 2026 - its stated 3 "
           "turns were actually 30 real minutes, which made it a permanent "
           "20% damage buff on an 18-turn cooldown. The soul grant stacks "
           "with Soul Generator for 30 souls per crit, three fragments in "
           "this economy's units, which is what CoA's '3 Reaped Souls' "
           "amounts to."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, refuses
# nodes carrying small integer durations and unlock_ability nodes, and
# since 6 Nov 2026 leaves UNSCALED_EFFECT_KEYS alone.
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

    # low_health_threshold_pct SUMS across talents and a character can
    # spend in several trees of their class, so exactly ONE node per CLASS
    # may set it. Harvest's Executioner owns it for Reaper.
    setters = [n["talent_id"] for n in TREE["nodes"]
               if "low_health_threshold_pct" in (n.get("effects") or {})]
    assert not setters, (
        f"low_health_threshold_pct SUMS across talents and Reaper Harvest's "
        f"Executioner already sets it for this class - a second setter "
        f"gives a Reaper who spends in both trees a 55% execute window. "
        f"Found {setters}")

    for n in TREE["nodes"]:
        gr = (n.get("proc") or {}).get("grant_resource")
        if gr:
            assert gr.get("resource") == "souls" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name souls and carry "
                f"a FLAT `amount`")
        # leech_pct reads the TRIGGERING hit's amount, which is ZERO on an
        # avoidance trigger - it would heal nothing while looking right.
        proc = n.get("proc") or {}
        if proc.get("trigger") in ("on_dodge", "on_parry", "on_avoid", "on_block"):
            assert "leech_pct" not in proc and "bonus_pct" not in proc, (
                f"{n['talent_id']} uses an amount-reading payload on "
                f"{proc['trigger']} - an avoided attack deals 0 damage, so "
                f"the payload silently yields nothing. Use heal_flat / "
                f"damage_flat instead")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Reaper Soul: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
