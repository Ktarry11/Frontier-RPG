#!/usr/bin/env python3
"""Rebuild Tinker's Invention tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_tinker_invention.py [--check]

SOURCE: data/reference/coa/tinker.json tab 74 - 37 real Invention talents
from Ascension's own CoA Builder payload, the same data allthingscoa.com
presents. Identity from data/reference/coa_playstyles.json: Invention is a
HEALER that "plays like Restoration Shaman + Holy Paladin".

The shipped tree was 27 nodes with exactly ONE proc between them. Twelve of
those nodes were real and are kept - they are the unlock_ability nodes that
teach the kit, and Frontier already has nearly all of the Invention
abilities (repair_shot, emergency_heal, med_pack, zap, nanobot_swarm /
_cleanser / _reconstruction, healing_radiator, three Beacons, ZIGGI-6K,
my_greatest_invention, battery_reclaimer). The other fifteen were 2-4%
scalars on real CoA names. Those are what this replaces.

WHAT THE SPEC IS. CoA's Invention heals by SPREADING: Stim Augmentation
splashes direct heals onto nearby allies, Bandage Gun widens that splash,
Healing Radiator leaks Nanobot ticks to five more, Emergency Enhancer makes
Zap! chase the lowest-health ally. That is a mechanic this engine supports
directly and the old tree expressed nowhere - splash_heal, smart_heal_pct,
shield_pct and leech_pct are all live proc payloads.

CONVENTIONS THIS TREE HAD TO GET RIGHT. They are not consistent with each
other, and every one of them is a way to ship a node that looks authored
and does nothing:
  splash_heal / shield_pct / leech_pct   FRACTION (0.20 = 20%)
  smart_heal_pct                         PERCENT  (status_effects.py
                                         divides by 100)
  crit_chance_spell / ability_*_crit     PERCENT  (5.0 = 5%)
  crit_damage_spell                      FRACTION (0.10 = 10%)
  *_cost_pct / *_cooldown_pct            FRACTION, and POSITIVE MEANS A
                                         REDUCTION
  <target>_from_<source>_pct             FRACTION, and only for the pairs
                                         in STAT_CONVERSION_TARGETS

WHAT A PROC CANNOT DO HERE, learned the hard way while authoring this.
CoA's Eureka! ("heal crits make your next Repair Shot 30% stronger") is not
buildable as written. The natural shape - a proc applying a buff whose
stat_mods carry ability_tinker_repair_shot_healing - is dead data:
get_talent_effects() aggregates talent trees, stances, forms and the
guardian stance, and NOT status effects, while ability_*_healing is only
ever read through it. So that node is rerouted to a payload that does fire
(see its _source) rather than shipped as a 30% buff that never applies.

TURN-BASED CUTS. Dropped outright: Build: Battery Recharge Station's
movement-speed aura and "run to the battery", Build: Noise Box (a
school-lockout interrupt on a ground object), Electromagnetic Resistors
(movement-impairing resistance), Technician's spell pushback half, and
every yard radius in the tree. Charges have no engine support, so Rapid
Fire Healing's "refresh a charge of Beacons" becomes cooldown recovery.
Graftbolts and Improved Graftbolts both hang off a mechanical pet's own
damage, which no talent key reaches; the shield half of Improved Graftbolts
is buildable and is the one that survives.

PARTY-WIDE AURAS DO NOT EXIST. Fine Tuning and Cybernetic Revivification
are both "all nearby allies get +X%" in CoA. A talent effect applies to its
own character only, so both keep the half that lands on the Tinker and say
so in their description rather than promising the party something.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/tinker_invention.json"

#: The direct heals Stim Augmentation and friends hang off. Frontier's
#: equivalents of CoA's Repair Shot / Emergency Heal / Zap!.
DIRECT_HEALS = ["tinker_repair_shot", "tinker_emergency_heal", "tinker_zap"]

TREE = {
    "spec_name": "Tinker Invention",
    "tree_id": "tinker_invention",
    "description": ("Field engineer healer - patches one ally and lets the "
                    "overflow wash across the rest of the party."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/tinker.json tab 74 "
        "(37 real CoA Invention talents) with identity from "
        "data/reference/coa_playstyles.json ('Restoration Shaman + Holy "
        "Paladin', Healer). Replaces a 27-node tree that carried real CoA "
        "names on fifteen 2-4% scalars and had exactly one proc in it. The "
        "twelve unlock_ability nodes were already correct and are kept. "
        "Every node below records the CoA text it came from and what was "
        "changed for a turn-based engine."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"tinker_invention_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"tinker_invention_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


def unlock(nid, name, ability, blurb, tier, x, *, connect=None, source=""):
    """An unlock node. These twelve were the only sound part of the old tree."""
    return node(nid, name, f"Learn {name.rstrip('!')}. {blurb}", tier, x,
                effects={"unlock_ability": ability}, connect=connect,
                source=source, active=True)


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "scientific_nature", "Scientific Nature",
    "Increases your healing power by 20% of your Intellect and your spell "
    "critical strike chance by 15% of your Intellect.",
    0, -3,
    effects={"healing_power_from_intellect_pct": 0.20,
             "crit_chance_spell_from_intellect_pct": 0.15},
    connect=["over_repaired"],
    source="CoA verbatim: 'Level 20 Passive. Increases your healing power by "
           "20% of your Intellect and your critical strike rating by 15% of "
           "your Intellect.' Built as the real stat conversion it is - both "
           "pairings are in STAT_CONVERSION_TARGETS/SOURCES, so both are "
           "live. Was healing_power_pct 2.0 per rank over 5 ranks, which is "
           "a flat 10% and not this talent at all."))

N.append(node(
    "over_repaired", "Over-Repaired",
    "Increases the healing done by Repair Shot by 15% per rank.",
    0, -1, ranks=2,
    effects={"ability_tinker_repair_shot_healing": 0.15},
    connect=["eureka"],
    source="CoA verbatim: 'Increases the healing done by Repair Shot by "
           "15%.' 2 ranks, as CoA has it."))

N.append(node(
    "field_medic", "Field Medic",
    "Increases your spell critical strike chance by 5%.",
    0, 1,
    effects={"crit_chance_spell": 5.0},
    connect=["eureka"],
    source="CoA: 'Increases your and your summons critical strike chance by "
           "5%.' The summon half is dropped: no talent key reaches a pet's "
           "crit. crit_chance_spell is a PERCENT here, so 5.0."))

N.append(node(
    "technician", "Technician",
    "Increases the healing done by your critical heals by up to 20%.",
    0, 3, ranks=2,
    effects={"crit_damage_spell": 0.10},
    connect=["triage_protocol"],
    source="CoA: 'Reduces spell pushback suffered from damaging attacks by "
           "35% and increases your critical healing by 10%.' Pushback does "
           "not exist in a turn-based engine with no cast bars, so that half "
           "is dropped rather than repriced. crit_damage_spell is the key a "
           "heal crit reads (abilities.py routes anything non-physical "
           "there) and it is a FRACTION, so 0.10."))

# ---- tier 1 -------------------------------------------------------------
N.append(unlock(
    "ziggi", "Build: ZIGGI-6K", "tinker_build_ziggi_6k",
    "A regenerative drone that heals your allies until dismissed.",
    1, -4, connect=["nanobot_swarm"],
    source="CoA: 'Level 10 Passive. Teaches you Build: ZIGGI-6K.' Kept from "
           "the previous tree - the unlock nodes were already right."))

N.append(unlock(
    "healing_radiator", "Healing Radiator", "tinker_healing_radiator",
    "Periodic healing from Nanobot Reconstruction leaks out to the rest of "
    "the party.",
    1, -2, connect=["nanobot_reconstruction"],
    source="CoA: 'Periodic healing done by Nanobot Reconstruction now "
           "restores health to 5 allied players within 10 yds of the "
           "affected target.' The yard radius is dropped; the ability itself "
           "already targets the party. Kept from the previous tree."))

N.append(node(
    "eureka", "Eureka!",
    "Your critical heals send a surge of healing to your most wounded ally.",
    1, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": DIRECT_HEALS,
          "smart_heal_pct": 30},
    connect=["fine_tuning"],
    source="CoA: 'Direct healing critical strikes now increase the healing "
           "done by your next Repair Shot or Emergency Heal by 30% for 10 "
           "seconds.' NOT buildable as written, and this is the one node in "
           "the tree where that is worth spelling out. A 'your next cast is "
           "stronger' buff has to reach ability_tinker_repair_shot_healing, "
           "which is read ONLY through get_talent_effects() - and that "
           "aggregates talent trees, stances, forms and the guardian stance, "
           "never status effects. A proc applying that buff is dead data. So "
           "the 30% is spent where it does fire: smart_heal_pct, which heals "
           "the lowest-health ally off the crit that triggered it. Note "
           "smart_heal_pct is a PERCENT (status_effects.py divides by 100), "
           "unlike every other heal payload here, which are fractions."))

N.append(unlock(
    "nanobot_swarm", "Nanobot Swarm", "tinker_nanobot_swarm",
    "Nanobots ride an ally, damaging nearby enemies and pulling your threat "
    "onto the host.",
    1, 2, connect=["nanobot_cleanser"],
    source="CoA: 'Send Nanobots to an ally, dealing damage to nearby enemies "
           "every 4 sec for 1 min. All threat generated by you is redirected "
           "to the target.' Kept from the previous tree."))

N.append(node(
    "triage_protocol", "Triage Protocol",
    "Your healing is 15% stronger on allies below 35% health.",
    1, 4,
    effects={"low_health_healing_pct": 0.15},
    connect=["macro_designer"],
    source="Not a CoA node - kept from the previous tree, where it was 3%, "
           "because it is one of the few things in that tree that was a real "
           "mechanic rather than a flat number. low_health_healing_pct keys "
           "off the RECIPIENT's health and was genuinely dead for a while; "
           "it was wired up at abilities.py:1574 once the heal path started "
           "passing the recipient through, and audit_talents.py's docstring "
           "still says otherwise. Threshold is the engine-wide "
           "low_health_threshold_pct default of 35%."))

# ---- tier 2 -------------------------------------------------------------
N.append(unlock(
    "nanobot_cleanser", "Nanobot Cleanser", "tinker_nanobot_cleanser",
    "Nanobots strip a poison and a disease from an ally each turn.",
    2, -3, connect=["stim_augmentation"],
    source="CoA: 'Send Nanobots to an ally removing 1 poison and disease "
           "effect every 3 sec for up to 15 sec.' Kept from the previous "
           "tree; 3 sec per tick is already one turn."))

N.append(unlock(
    "nanobot_reconstruction", "Nanobot Reconstruction",
    "tinker_nanobot_reconstruction",
    "A sustained repair patch that mends an ally over several turns.",
    2, -1, connect=["stim_augmentation"],
    source="Kept from the previous tree. The ability Healing Radiator "
           "spreads, so it has to be learnable before it."))

N.append(node(
    "fine_tuning", "Fine Tuning",
    "Increases your spell critical strike chance by 3%.",
    2, 1,
    effects={"crit_chance_spell": 3.0},
    connect=["bandage_gun"],
    source="CoA: 'Increases critical strike chance of all party and raid "
           "members by 3%. Does not stack with similar effects. In addition, "
           "not critically healing now increases your critical strike chance "
           "by 1%, stacking 10 times, until your next effective critical "
           "heal.' Two halves, neither portable as written. A talent effect "
           "applies to its own character, so the party-wide aura becomes "
           "self-only and the description says 'your' rather than promising "
           "the party a buff it will not get. The stacking half needs a "
           "'healed and did NOT crit' trigger, which no trigger in this "
           "engine expresses - on_heal_cast cannot see the crit result - so "
           "it is dropped rather than approximated."))

N.append(node(
    "macro_designer", "Macro Designer",
    "Increases the duration of Med Pack by 1 turn.",
    2, 3,
    effects={"ability_tinker_med_pack_duration": 1},
    connect=["trust_the_science"],
    source="CoA: 'Increases the duration of your Beacons by 5 sec and Med "
           "Pack by 3 sec.' 3 sec is one turn. The Beacon half is dropped: "
           "Frontier's Beacons are party buffs whose duration no "
           "ability_*_duration key reaches, while Med Pack is a hot and does "
           "take one."))

# ---- tier 3 -------------------------------------------------------------
N.append(unlock(
    "stim_rounds", "Stim Rounds", "tinker_stim_rounds",
    "Load stim rounds into your gun, so your shots carry a dose of medicine.",
    3, -5, connect=["stim_augmentation"],
    source="Kept from the previous tree. tinker_stim_rounds carries "
           "requires_talent, so this node is the ONLY way the ability can be "
           "learned - dropping it would strand the ability at every level. "
           "Paired deliberately with Stim Augmentation, which is what makes "
           "the dose splash."))

N.append(node(
    "stim_augmentation", "Stim Augmentation",
    "Your Repair Shot splashes 20% of its healing onto up to 3 nearby allies.",
    3, -3,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_repair_shot"],
          "splash_heal": {"pct": 0.20, "max_targets": 3}},
    connect=["med_pack"],
    source="CoA verbatim: 'Add a Stim Augmentation to your gun for 1 hour, "
           "causing your direct healing abilities to heal up to 3 nearby "
           "allies for an additional 20% of the amount healed.' This is the "
           "spec's defining mechanic and the old tree had no form of it. "
           "splash_heal is a live proc payload with a max_targets field, so "
           "CoA's number goes in directly. The 1-hour self-buff framing is "
           "dropped - a weapon augmentation lasting an hour is a passive in "
           "this engine. pct is a FRACTION."))

N.append(unlock(
    "med_pack", "Med Pack", "tinker_med_pack",
    "A pack that keeps mending an ally for several turns.",
    3, -1, connect=["improved_graftbolts"],
    source="Kept from the previous tree."))

N.append(node(
    "bandage_gun", "Bandage Gun",
    "Your Emergency Heal and Zap! splash 20% of their healing onto up to 5 "
    "nearby allies.",
    3, 1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_emergency_heal", "tinker_zap"],
          "splash_heal": {"pct": 0.20, "max_targets": 5}},
    connect=["zap"],
    source="CoA verbatim: 'Healing from Stim Augmentation now affects 2 "
           "additional allies near the primary target.' A talent cannot "
           "widen ANOTHER talent's proc - there is no key that edits a "
           "sibling node's max_targets - so instead of faking that, this "
           "node carries its own splash at CoA's widened count (3 + 2 = 5) "
           "over the other two direct heals. Net effect matches what the "
           "pair is for: spending both points means the whole direct-heal "
           "kit splashes, and widely. Was a 3% cost reduction."))

N.append(node(
    "stim_shots", "Stim Shots",
    "Increases the healing done by Repair Shot and Emergency Heal by 10%.",
    3, 3,
    effects={"ability_tinker_repair_shot_healing": 0.10,
             "ability_tinker_emergency_heal_healing": 0.10},
    connect=["trust_the_science"],
    source="CoA: 'Your Stim Augmentation now heals for an additional 10% of "
           "the amount healed.' Routed onto the heals themselves rather than "
           "onto the splash: the splash is sized from the triggering heal, so "
           "raising the heal raises the splash with it, and there is no key "
           "that reaches a proc's own pct."))

# ---- tier 4 -------------------------------------------------------------
N.append(unlock(
    "zap", "Zap!", "tinker_zap",
    "A long jolt of current that mends an ally. Scales with Repair Shot.",
    4, -4, connect=["rejuvenating_gadget"],
    source="Real screenshot: Requires Level 38, Zap! (Rank 1) - real "
           "self-rank gate, Kyle-confirmed. Kept from the previous tree."))

N.append(unlock(
    "battery_reclaimer", "Build: Battery Reclaimer", "tinker_battery_reclaimer",
    "A station that gives the party back health and resources.",
    4, -2, connect=["self_sustaining_technology"],
    source="CoA: 'Build a Battery Recharge Station for 30 sec that allies "
           "can interact with once to replenish 15% maximum health and mana, "
           "and 50% maximum Rage, Energy, Focus and Runic Power. Applies "
           "Depleting Battery to party and raid members within 40 yds.' The "
           "movement-speed aura and the 'run to the battery' interaction are "
           "both positional and both dropped. Kept from the previous tree."))

N.append(node(
    "trust_the_science", "Trust the Science!",
    "Reduces the cooldown of Zap! by 20%.",
    4, 0,
    effects={"ability_tinker_zap_cooldown_pct": 0.20},
    connect=["emergency_circumvented"],
    source="CoA: 'Reduces the cooldown of Zap! by -5 sec.' Expressed as a "
           "percentage because a flat 5 sec is under two turns and would "
           "round to nothing useful. NOTE the sign convention: _cooldown_pct "
           "is POSITIVE for a reduction here, so 0.20 makes Zap! cheaper to "
           "come back to, not slower."))

N.append(node(
    "resourceful_tech", "Resourceful Tech",
    "Increases the critical strike chance of Zap! by 35%.",
    4, 2,
    effects={"ability_tinker_zap_crit": 35.0},
    connect=["emergency_enhancer"],
    source="CoA: 'Your Zap! is now guaranteed to critically strike allies "
           "affected by Nanobots.' The condition is what balances it, and no "
           "effect key can read whether the heal target carries a specific "
           "buff. Shipped as a large but not guaranteed crit bonus instead "
           "of an unconditional ability_tinker_zap_crit of 100.0, which is "
           "what the literal reading would have been and would have been a "
           "permanent free crit. ability_*_crit is a PERCENT."))

N.append(node(
    "rejuvenating_gadget", "Rejuvenating Gadget",
    "Critical strikes with Zap! leave behind rejuvenating gas, healing the "
    "target for 3 turns.",
    4, 4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_zap"],
          "apply_effect": {"effect_id": "tinker_rejuvenating_gas",
                           "name": "Rejuvenating Gas", "effect_type": "hot",
                           "duration": 3, "potency": 24, "on_target": True}},
    connect=["my_greatest_invention"],
    source="CoA: 'Critical strikes with Zap! now apply Rejuvenating Gas to "
           "up to 12 allies within 8 yards of your target that restores 15% "
           "of the value of the shot as health every 2 sec for 10 sec.' The "
           "12-ally yard radius is dropped (no positioning) and the hot lands "
           "on the heal target. A proc-applied hot has a flat potency - there "
           "is no 'percentage of the triggering amount' form for apply_effect "
           "- so 15% of a Zap! is approximated as a flat 24 per turn, in the "
           "same range as Frontier's other mid-level hots."))

# ---- tier 5 -------------------------------------------------------------
N.append(unlock(
    "my_greatest_invention", "My Greatest Invention!",
    "tinker_my_greatest_invention",
    "Show off the masterpiece, healing the whole party over several turns.",
    5, -3, connect=["emergency_enhancer"],
    source="Kept from the previous tree."))

N.append(node(
    "improved_graftbolts", "Improved Graftbolts",
    "Your Repair Shot also shields the target for 50% of the healing done.",
    5, -1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_repair_shot"],
          "shield_pct": {"pct": 0.50, "duration": 3,
                         "effect_id": "tinker_graftbolt_shield",
                         "name": "Graftbolt Shield"}},
    connect=["emergency_enhancer"],
    source="CoA: 'Level 50 Passive. Effective healing done by Stim "
           "Augmentation now applies a shield to the target equal to 50% of "
           "the healing done. Up to 10% of their maximum health.' shield_pct "
           "is a live payload sized from the triggering heal, which is "
           "exactly this. The 10%-max-health cap is NOT modelled: shield_pct "
           "has no cap field, and absorb_pct_max_health sizes off max health "
           "instead of off the heal, so it is the wrong mechanism. Flagged "
           "rather than faked - this node is slightly stronger than CoA's on "
           "a very large heal. CoA's base Graftbolts (a pet mana/damage buff "
           "off a 25% chance) is not built at all: it hangs entirely on a "
           "mechanical pet's own output, which no talent key reaches."))

N.append(node(
    "emergency_circumvented", "Emergency Circumvented",
    "Increases the critical strike chance of Emergency Heal by 15%.",
    5, 1,
    effects={"ability_tinker_emergency_heal_crit": 15.0},
    connect=["emergency_enhancer"],
    source="CoA: 'Increases the critical strike chance of Emergency Heal by "
           "15% and allows the periodic healing done by Med Pack to "
           "critically strike.' The second half is an engine-wide rule about "
           "whether hot ticks can crit, not a per-character bonus, so it is "
           "not a talent effect at all and is dropped."))

N.append(node(
    "self_sustaining_technology", "Self-Sustaining Technology",
    "15% of the healing you do is also routed to your most wounded ally.",
    5, 3,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 1,
          "leech_pct": {"pct": 0.15, "smart": True}},
    connect=["emergency_enhancer"],
    source="CoA: 'Damage or healing done by your pet or summons now heals "
           "you equal to 15% of the value. In addition, damage or healing "
           "done by you now restores health and mana to your pet equal to "
           "15% of the value. Each of these effects can only occur once per "
           "sec.' Both halves of CoA's version are pet-side and unreachable. "
           "The identity worth keeping is 'your output feeds back into the "
           "group', so leech_pct with smart:true sends it to the worst-off "
           "ally. CoA's once-per-second becomes icd 1, i.e. once a turn. "
           "Was max_mana_pct 0.02."))

N.append(node(
    "surge_protector", "Surge Protector",
    "While above 65% mana, your healing is 8% stronger.",
    5, 5,
    effects={"high_mana_healing_pct": 0.08},
    connect=["emergency_enhancer"],
    source="Not a CoA node - kept from the previous tree (where it was 3%) "
           "for the same reason as Triage Protocol: it is a real conditional "
           "rather than a flat number. high_mana_healing_pct fires above "
           "1 - low_health_threshold_pct of max mana, i.e. 65%, and pairs "
           "with Triage Protocol's low-health window."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "emergency_enhancer", "Emergency Enhancer",
    "Zap! now also fires from your active constructions, healing your most "
    "wounded ally for 90% of the amount.",
    6, 0,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_zap"],
          "smart_heal_pct": 90},
    source="CoA: 'Zap! now causes your active Build abilities to zap the "
           "lowest health nearby ally, healing them for 990 + 90% healing.' "
           "smart_heal_pct is the payload for 'heal the lowest-health ally' "
           "and this is almost a literal port - the only cut is the flat 990, "
           "which is a level-60 raid number. PERCENT, so 90 means 90% of the "
           "Zap! that triggered it."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026, asked directly: multi-rank the real mechanics
# rather than padding the tree back out with flat scalars.
#
# Rebuilding a spec from CoA trades multi-rank scalars for single-rank
# mechanics, which is the point - but it also cut this tree's POINT
# CAPACITY to around 31 against a project median of 71, and a character
# earns 56 points by level 60 that a pure-spec build must be able to spend
# in ONE tree. See tools/talent_ranks.py, which does the rescaling so a
# ranked node lands on exactly the ceiling it had at one rank.
#
# Three ranks for every node that can take them. Left at one rank:
#   - unlock nodes, since an ability cannot be learned a third of the way
#   - the tier 6 capstone, which reads as a single decisive pick
from tools.talent_ranks import rankable, spread  # noqa: E402

for _n in TREE["nodes"]:
    if _n["max_points"] < 3 and _n["tier"] < 6 and rankable(_n):
        spread(_n, 3)


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    unlocks = sum(1 for n in TREE["nodes"] if "unlock_ability" in n["effects"])
    print(f"Tinker Invention: {len(ids)} nodes, {procs} with procs, "
          f"{unlocks} unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
