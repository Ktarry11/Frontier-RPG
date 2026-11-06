#!/usr/bin/env python3
"""Rebuild Druid Feral Combat from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_druid_feral.py

SOURCE: data/reference/wotlk/druid.json (from Spell.dbc) - the real 30
talents and 78 points, every row read out of the reference and every
ambiguous talent's RANK TEXT read before authoring.

THIS TREE WAS UNDER A NO-TOUCH RULE ALL SESSION. Kyle retired it on 5 Nov
("Rebuild all three") when he asked for all druid talents fixed up.

ROLE: one tree, two jobs - bear tank and cat damage - which is why it is
the biggest druid tree.

THE BEAR IS AN AGILITY TANK, NOT A STRENGTH ONE. Kyle, 5 Nov: "druid tank
is an agility/dodge/armor based tank", and "my friend plays guardian druid
and his agi stacking made for the best tank i've ever seen". So this tree
stacks AGILITY, DODGE and ARMOR rather than strength or block, and the
mitigation talents are built on keys that pay agility stackers. That is a
design instruction, not a flavour note, and it decided several key choices
below that would otherwise have gone to strength or stamina.

EVERY STAT KEY HERE WAS MEASURED ON A LIVE LEVEL-60 DRUID BEFORE BEING
AUTHORED, because the probe reports most of them as "no read site found"
(they are read off the `bonuses` pool via f-strings, not by literal name):

    agility_pct = 20      -> dodge 12.25 -> 13.7, ap 34 -> 37   POINTS
    armor_pct = 20        -> armor 80 -> 96                     POINTS
    armor_from_agility_pct = 0.5 -> armor 80 -> 94      RAW MULTIPLIER
    dodge_from_agility_pct = 0.5 -> dodge 12.25 -> 26.75 RAW MULTIPLIER
    attack_power_pct = 20 -> ap 34 -> 40                        POINTS
    max_health_pct = 0.10 -> health 420 -> 462               FRACTION
    dodge = 2             -> +1.905 (SCALED x0.9524 - not 1:1)

agility_pct is the key talent of this rebuild: it feeds DODGE AND ATTACK
POWER AT THE SAME TIME, so one stat serves tank and cat alike. That is
exactly the agi-stacking Kyle described, and it is why Heart of the Wild
and Survival of the Fittest lean on it.

FORM GATING IS REAL AND USED. entities/talent_node.py form_matches()
accepts a LIST, and its docstring already warns why bear talents must be
gated on ["bear", "dire_bear"] and never the bare string "bear" - Dire
Bear Form is unlocked INSIDE THIS TREE, so a "bear"-only gate would
switch itself off the moment the player finished their own tree. Every
bear gate below is the list.

DROPPED, 1 point of the real 78: Feral Charge (no ability, and there is
NO CHARGE SYSTEM at all). Dire Bear Form is ADDED as a node that is not a
real WotLK talent - see that node for why it has to exist here.

ABILITIES THE REAL TREE WANTS AND WE LACK: Demoralizing Roar, Lacerate,
Pounce, Prowl, Tiger's Fury, Feral Charge, Survival Instincts, Leader of
the Pack (as an aura), Faerie Fire (Feral).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

BEAR = ["bear", "dire_bear"]
CAT = "cat"
FEROCITY = ["druid_maul", "druid_swipe_cat", "druid_claw", "druid_rake",
            "druid_mangle"]
SAVAGE = ["druid_claw", "druid_rake", "druid_mangle", "druid_maul"]

T = Tree("druid_feral", "Druid Feral Combat",
         "Claw and hide - the druid who stops talking and starts biting.")

# ----------------------------------------------------- tier 0 (row 0)
T.node("ferocity", "Ferocity",
       "Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle by 1 per "
       "rank.",
       0, -2, 5,
       effects={f"ability_{a}_cost": 1 for a in FEROCITY},
       source="WotLK row 0, built verbatim: 'Reduces the cost of your Maul, "
              "Swipe, Claw, Rake and Mangle abilities by 1-5 Rage or "
              "Energy.' All five abilities exist and ALL FIVE CARRY A REAL "
              "COST (maul 20, swipe 45, claw 40, rake 40, mangle 30), which "
              "was CHECKED rather than assumed - "
              "tools/qa_ability_scoped_fields.py found 19 keys elsewhere in "
              "the project reducing the cost of abilities that are free. "
              "ability_<id>_cost is FLAT, not a fraction.")

T.node("feral_aggression", "Feral Aggression",
       "Increases the damage of your Ferocious Bite by 3% per rank.",
       0, 0, 5,
       effects={"ability_druid_ferocious_bite_damage": 0.03},
       source="WotLK row 0: 'Increases the attack power reduction of your "
              "Demoralizing Roar by 8%-40% and the damage caused by your "
              "Ferocious Bite by 3%-15%.' Demoralizing Roar does not exist. "
              "The Ferocious Bite half is VERBATIM at 3% per rank.")

# ----------------------------------------------------- tier 1 (rows 1-2)
T.node("feral_instinct", "Feral Instinct",
       "Increases the damage of your Swipe by 10% per rank.",
       1, -6, 3,
       effects={"ability_druid_swipe_cat_damage": 0.10},
       connected_to=["ferocity"],
       source="WotLK row 1: 'Increases the damage done by your Swipe "
              "ability by 10%-30% and reduces the chance enemies have to "
              "detect you while Prowling.' The Swipe half is VERBATIM. "
              "THERE IS NO STEALTH SYSTEM in this engine - no Prowl, no "
              "detection - which is the same gap that reshaped three Rogue "
              "Subtlety nodes earlier this session.")

T.node("savage_fury", "Savage Fury",
       "Increases the damage of your Claw, Rake, Mangle and Maul by 10% per "
       "rank.",
       1, -4, 2,
       effects={f"ability_{a}_damage": 0.10 for a in SAVAGE},
       connected_to=["ferocity"],
       source="WotLK row 1, built verbatim: 'Increases the damage caused by "
              "your Claw, Rake, Mangle (Cat), Mangle (Bear) and Maul "
              "abilities by 10%/20%.' Cat and Bear Mangle are one ability "
              "here. All four deal real damage (rake is a dot, the rest are "
              "damage), so _damage lands on every one.")

T.node("thick_hide", "Thick Hide",
       "Increases your armor by 3% per rank, and a further 4% of your "
       "Agility per rank.",
       1, -2, 3,
       effects={"armor_pct": 3.0, "armor_from_agility_pct": 0.04},
       connected_to=["ferocity"],
       source="WotLK row 1: 'Increases your Armor contribution from cloth "
              "and leather items by 4%-10%.' There is no armour-by-item-"
              "type key, so it is general armour - AND A SECOND HALF IS "
              "ADDED DELIBERATELY. Kyle, 5 Nov: 'druid tank is an "
              "agility/dodge/armor based tank'. armor_from_agility_pct "
              "makes the tank's own stacked Agility feed his armour, which "
              "is the real WoW bear relationship and the thing that makes "
              "agi-stacking work. MEASURED: armor_pct=20 moved armour "
              "80->96 (POINTS), armor_from_agility_pct=0.5 moved it 80->94 "
              "(A RAW MULTIPLIER, gained = source * pct, character.py:1551 "
              "- so 0.04 and never 4).")

T.node("feral_swiftness", "Feral Swiftness",
       "Increases your dodge by 2% per rank.",
       1, 0, 2, effects={"dodge": 2.0},
       connected_to=["feral_aggression"],
       source="WotLK row 2: 'Increases your movement speed by 15%/30% in "
              "Cat Form and increases your chance to dodge while in Cat "
              "Form, Bear Form and Dire Bear Form by 2%/4%.' THERE IS NO "
              "MOVEMENT SPEED in this engine. The dodge half is verbatim "
              "and is left UNGATED by form on purpose: the real talent "
              "covers all three forms, which is every form this tree uses, "
              "so a gate would only cost the caster forms a small dodge "
              "bonus for no design gain. NOTE dodge lands SCALED x0.9524 "
              "(probe: dodge=2 moved the attribute +1.905), not 1:1.")

T.node("survival_instincts", "Survival Instincts",
       "Increases your maximum health by 8%.",
       1, 2, 1, effects={"max_health_pct": 0.08},
       connected_to=["feral_aggression"],
       source="WotLK row 2: 'When activated, temporarily grants you 30% of "
              "your maximum health for 20 sec while in Bear, Cat or Dire "
              "Bear Form.' DEPARTURE - there is no druid_survival_instincts "
              "ability to unlock and no temporary-max-health mechanic, so "
              "the panic button becomes a permanent, much smaller cushion. "
              "max_health_pct is a FRACTION and was MEASURED (0.10 moved "
              "health 420->462), unlike stamina_pct which is POINTS - two "
              "health keys, opposite conventions.")

T.node("sharpened_claws", "Sharpened Claws",
       "Increases your critical strike chance by 2% per rank.",
       1, 4, 3, effects={"crit_chance": 2.0},
       connected_to=["feral_aggression"],
       source="WotLK row 2, built verbatim: 'Increases your critical strike "
              "chance while in Bear, Dire Bear or Cat Form by 2%-6%.' Left "
              "ungated for the same reason as Feral Swiftness - the real "
              "gate covers every form this tree uses. crit_chance is "
              "PERCENTAGE POINTS.")

# ----------------------------------------------------- tier 2 (rows 3-4)
T.node("shredding_attacks", "Shredding Attacks",
       "Reduces the cost of your Shred by 9 per rank.",
       2, -6, 2,
       effects={"ability_druid_shred_cost": 9},
       connected_to=["feral_instinct"],
       source="WotLK row 3: 'Reduces the energy cost of your Shred ability "
              "by 9/18 and the rage cost of your Lacerate ability by 1/2.' "
              "The Shred half is VERBATIM (shred costs 60, so two ranks cut "
              "it by nearly a third). Lacerate does not exist.")

T.node("predatory_strikes", "Predatory Strikes",
       "Increases your attack power by 4% per rank.",
       2, -4, 3, effects={"attack_power_pct": 4.0},
       connected_to=["savage_fury"],
       source="WotLK row 3: 'Increases your melee attack power in Cat, Bear "
              "and Dire Bear Forms by 50%-150% of your level and 20% of any "
              "attack power on your equipped weapon.' There is no "
              "attack-power-from-level or from-weapon conversion (weapon is "
              "a valid conversion SOURCE but level is not a stat), so it "
              "becomes a straight percentage. MEASURED: attack_power_pct=20 "
              "moved attack power 34->40, so POINTS.")

T.node("primal_fury", "Primal Fury",
       "Your critical strikes in bear form generate 5 extra Rage.",
       2, -2, 2,
       proc={"trigger": "on_crit", "chance": 50, "icd": 0,
             "require_form": BEAR,
             "grant_resource": {"resource": "rage", "amount": 5}},
       connected_to=["thick_hide"],
       source="WotLK row 3, built close to verbatim: 'Gives you a 100% "
              "chance to gain an additional 5 Rage anytime you get a "
              "critical strike while in Bear and Dire Bear Form.' "
              "rage_generation_pct IS A DEAD KEY (measured), so the rage has "
              "to arrive as a proc payload. CHANCE IS 50, NOT THE REAL 100%: "
              "only a proc's CHANCE scales with points, never its payload, "
              "so a 2-rank node at 100% would give rank 2 nothing - the bug "
              "check_talent_balance.py caught in four Warlock nodes this "
              "session. 50 x 2 = 100 at full rank. GATED ON THE BEAR LIST "
              "['bear','dire_bear'], never the bare string 'bear', because "
              "Dire Bear Form is unlocked inside this very tree and a "
              "single-form gate would switch itself off when the player "
              "took their own upgrade (see talent_node.form_matches).")

T.node("primal_precision", "Primal Precision",
       "Increases your chance to hit by 2% per rank.",
       2, 0, 2, effects={"hit_rating": 2.0},
       connected_to=["thick_hide"],
       source="WotLK row 3: 'Increases your expertise by 10/20, and you are "
              "refunded 80% of the energy cost of a finishing move if it "
              "fails to land.' Kyle, this session: 'So expertise is "
              "basically hit rating' - so expertise becomes hit_rating, "
              "which is PERCENTAGE POINTS and is NOT a valid "
              "STAT_CONVERSION_TARGET. The refund clause needs no building: "
              "there is no on-miss trigger, and with hit rating applied "
              "there is less to refund.")

T.node("brutal_impact", "Brutal Impact",
       "Increases the duration of your Bash by 1 turn and reduces its "
       "cooldown by 1 turn per rank.",
       2, 2, 2,
       effects={"ability_druid_bash_duration": 1,
                "ability_druid_bash_cooldown": 1},
       connected_to=["feral_swiftness"],
       source="WotLK row 4, built verbatim for the one ability we have: "
              "'Increases the stun duration of your Bash and Pounce "
              "abilities by 0.5/1 sec and decreases the cooldown of Bash by "
              "15/30 sec.' Pounce does not exist. BOTH KEYS WERE CHECKED "
              "AGAINST THE ABILITY: druid_bash really does carry duration 1 "
              "and cooldown 5, so both land - the first draft of this file "
              "used ability_druid_bash_damage, which "
              "qa_ability_scoped_fields.py correctly flagged as dead, "
              "because bash is effect_type 'debuff' with no damage at all. "
              "_duration is FLAT TURNS and POSITIVE EXTENDS; _cooldown is "
              "FLAT turns and clamps at 1.")

T.node("nurturing_instinct", "Nurturing Instinct",
       "You gain healing power equal to 15% of your Agility per rank.",
       2, 4, 2,
       effects={"healing_power_from_agility_pct": 0.15},
       connected_to=["feral_swiftness"],
       source="WotLK row 4: 'Increases your healing spells by up to 35%/70% "
              "of your Agility, and increases healing done to you by 10%/20% "
              "while in Cat form.' The Agility half is VERBATIM and is "
              "exactly the agility-stacking payoff Kyle described - a feral "
              "druid's Agility making his out-of-form healing matter. "
              "agility is a valid conversion SOURCE and healing_power a "
              "valid TARGET (STAT_CONVERSION_TARGETS, character.py:18). RAW "
              "MULTIPLIER convention, so 0.15 and never 15. The "
              "healing-taken half is dropped: healing_taken_pct is a status "
              "key, not a talent one, and there is no self-scoped form of "
              "it.")

# ----------------------------------------------------- tier 3 (row 5)
T.node("natural_reaction", "Natural Reaction",
       "Increases your dodge by 2% per rank, and dodging in bear form "
       "generates Rage.",
       3, -4, 3,
       effects={"dodge": 2.0},
       proc={"trigger": "on_dodge", "chance": 100, "icd": 0,
             "require_form": BEAR,
             "grant_resource": {"resource": "rage", "amount": 3}},
       connected_to=["predatory_strikes"],
       source="WotLK row 5, BOTH HALVES BUILT VERBATIM: 'Increases your "
              "dodge while in Bear Form or Dire Bear Form by 2%-6%, and you "
              "regenerate 1-3 rage every time you dodge.' This is the "
              "tank's engine and the clearest expression of Kyle's "
              "agi/dodge brief - more Agility means more dodges means more "
              "Rage. The 100% proc chance is legitimate here because the "
              "node ALSO carries a scaling effects dict, so ranks 2 and 3 "
              "still buy dodge; check_talent_balance.py accepts a 100% "
              "multi-rank proc for exactly that reason. ON AN AVOIDANCE "
              "TRIGGER THE INCOMING AMOUNT IS ZERO, so the payload must be "
              "grant_resource/damage_flat/heal_flat/apply_effect - a "
              "leech_pct or bonus_pct here would silently do nothing.")

T.node("heart_of_the_wild", "Heart of the Wild",
       "Increases your Intellect by 4% per rank and your Agility by 2% per "
       "rank.",
       3, -2, 5,
       effects={"intellect_pct": 4.0, "agility_pct": 2.0},
       connected_to=["primal_fury"],
       source="WotLK row 5: 'Increases your Intellect by 4%-20%. In "
              "addition, while in Bear or Dire Bear Form your Stamina is "
              "increased by 10% and while in Cat Form your attack power is "
              "increased by 10%.' The Intellect half is VERBATIM. THE "
              "FORM-SPLIT HALVES ARE DELIBERATELY MERGED INTO AGILITY "
              "rather than built as two form-gated nodes, and that is a "
              "design call from Kyle's brief: agility_pct feeds DODGE AND "
              "ATTACK POWER AT ONCE (measured: agility_pct=20 moved dodge "
              "12.25->13.7 AND attack power 34->37), so one key delivers "
              "the bear's survivability and the cat's damage exactly as the "
              "real talent's two branches do - with the bonus that it keeps "
              "paying when the druid swaps forms mid-fight. Both keys are "
              "POINTS.")

T.node("survival_of_the_fittest", "Survival of the Fittest",
       "Increases all your attributes by 2% per rank and your armor by 2% "
       "per rank.",
       3, 0, 3,
       effects={"all_stats_pct": 2.0, "armor_pct": 2.0},
       connected_to=["primal_precision"],
       source="WotLK row 5, built close to verbatim: 'Increases all "
              "attributes by 2%-6%, reduces the chance you'll be critically "
              "hit by melee attacks by 2%-6%, and increases your armor "
              "contribution in Bear Form by 11%-33%.' "
              "CRIT_TAKEN_REDUCTION IS A DEAD TALENT KEY - measured, and "
              "the same dead key replaced in sun_cleric_blessings and "
              "warlock_demonology this session - so that third is dropped "
              "rather than faked. all_stats_pct is POINTS and multiplies "
              "every attribute INCLUDING Agility, which is why it belongs "
              "in an agi-stacking tank tree; armor_pct is POINTS too.")

# ----------------------------------------------------- tier 4 (rows 6-7)
T.node("leader_of_the_pack", "Leader of the Pack",
       "Increases your critical strike chance by 5%.",
       4, -6, 1, effects={"crit_chance": 5.0},
       connected_to=["natural_reaction"],
       source="WotLK row 6: 'While in Cat, Bear or Dire Bear Form, "
              "increases ranged and melee critical chance of all party and "
              "raid members by 5%.' A TALENT EFFECT CAN NEVER REACH AN ALLY "
              "- only a party-targeted ABILITY can (abilities.py:2064) - so "
              "the aura becomes self-only at the real 5%. The same wall "
              "cost Demonic Pact its raid identity in warlock_demonology "
              "and Improved Moonkin Form its aura in druid_balance; it is "
              "the single most-hit limit across these nine classes.")

T.node("improved_leader_of_the_pack", "Improved Leader of the Pack",
       "Your critical strikes heal you.",
       4, -4, 2,
       proc={"trigger": "on_crit", "chance": 50, "icd": 1,
             "heal_flat": 90},
       connected_to=["leader_of_the_pack"],
       source="WotLK row 6: 'Your Leader of the Pack ability also causes "
              "affected targets to heal themselves for 4% of their total "
              "health when they critically hit.' The party half is "
              "unbuildable as above, so it is the druid healing himself. "
              "heal_flat is FLAT - there is no heal-for-%-of-max-health "
              "payload - so 90 is sized against a level-60 druid's pool. "
              "CHANCE IS 50 x 2 rather than the real 100% so the second "
              "rank buys something; icd 1 stops a crit streak chaining it.")

T.node("primal_tenacity", "Primal Tenacity",
       "Reduces the duration of stuns by 10% per rank and the damage you "
       "take by 2% per rank.",
       4, -2, 3,
       effects={"stun_duration_reduction_pct": 0.10,
                "damage_taken_pct": -0.02},
       connected_to=["heart_of_the_wild"],
       source="WotLK row 6: 'Reduces the duration of fear effects by "
              "10%-30%, reduces all damage taken while stunned by 10%-30% "
              "while in Cat Form.' There is no fear-duration key, and "
              "nothing branches on BEING stunned, so the two clauses merge "
              "into the nearest pair that works: "
              "stun_duration_reduction_pct (a FRACTION, and it floors a "
              "stun at 1 turn) and flat mitigation. BARE damage_taken_pct "
              "is read RAW ON BOTH SIDES, so -0.02 is 2% - this is the key "
              "that was authored as 5.0 in Warrior Death Wish and meant "
              "500%.")

T.node("protector_of_the_pack", "Protector of the Pack",
       "In bear form, increases your attack power by 2% per rank and "
       "reduces damage taken by 4% per rank.",
       4, 0, 3,
       effects={"attack_power_pct": 2.0, "damage_taken_pct": -0.04},
       require_form=BEAR,
       connected_to=["survival_of_the_fittest"],
       source="WotLK row 7, built verbatim: 'Increases your attack power by "
              "2%-6% and reduces the damage you take by 4%-12%, while in "
              "Bear or Dire Bear Form.' THE FORM GATE IS REAL AND IS "
              "ENFORCED - this is the tank's main mitigation talent and it "
              "should do nothing in cat form, which require_form delivers "
              "(TalentNode.require_form, read through "
              "talent_tree.get_total_effects). Gated on the LIST, never the "
              "bare string 'bear', because Dire Bear Form is unlocked in "
              "this same tree.")

T.node("predatory_instincts", "Predatory Instincts",
       "In cat form, increases your critical strike damage by 10% per rank.",
       4, 2, 3,
       effects={"crit_damage_physical": 0.10},
       require_form=CAT,
       connected_to=["survival_of_the_fittest"],
       source="WotLK row 7: 'While in Cat Form increases your damage from "
              "melee critical strikes by 3%-10% and reduces the damage "
              "taken from area of effect attacks by 10%-30%.' "
              "aoe_damage_taken_pct IS A DEAD KEY (measured), so only the "
              "crit half is built. crit_damage_physical IS LIVE - it is "
              "read at abilities.py:1460 INSIDE A TERNARY, which is why a "
              "literal read-site probe reports nothing for it and why it "
              "was nearly declared dead. The cat gate is a single form id, "
              "which is safe here because there is no second cat form.")

T.node("dire_bear_form", "Dire Bear Form",
       "Teaches Dire Bear Form, the greater shape.",
       4, 4, 1, node_type="active",
       effects={"unlock_ability": "druid_dire_bear_form"},
       connected_to=["protector_of_the_pack"],
       source="NOT A REAL WOTLK TALENT - Dire Bear Form is trained at level "
              "40 in 3.3.5a. It exists as a node here because "
              "druid_dire_bear_form is requires_talent IN THIS PROJECT (set "
              "earlier this session, when all five druid forms turned out "
              "to be auto-learned and three talent points were buying "
              "nothing), and THIS TREE IS ITS ONLY SOURCE. Removing the "
              "node would make the ability unobtainable, which "
              "qa_abilities_obtainable.py would catch - the same failure "
              "that hit rogue_evasion earlier this session. Kept rather "
              "than ungated because taking a form out of the tank spec's "
              "progression is a bigger gameplay change than a talent pass "
              "should make unasked. Placed at tier 4, whose 20-point gate "
              "lands around level 40, matching where it is really learned, "
              "and matching Kyle's own framing of forms as level-40 "
              "talents. Infected Wounds, the other real row-7 talent, is "
              "DROPPED: its content is a movement-speed and attack-speed "
              "debuff, and neither is buildable - there is no movement "
              "speed, and HASTE IS NOT ONE OF THE EIGHT STAT_MODS A MONSTER "
              "CAN READ, so a haste debuff on an enemy is silently dead.")

# ----------------------------------------------------- tier 5 (rows 8-9)
T.node("king_of_the_jungle", "King of the Jungle",
       "In bear form, increases your damage by 5% per rank.",
       5, -4, 3,
       effects={"physical_damage": 0.05},
       require_form=BEAR,
       connected_to=["protector_of_the_pack"],
       source="WotLK row 8: 'While using your Enrage ability in Bear Form, "
              "your damage is increased by 5%-15%, and your Tiger's Fury "
              "ability also instantly restores 20-60 energy.' Tiger's Fury "
              "does not exist, and NOTHING BRANCHES ON ANOTHER BUFF BEING "
              "ACTIVE - there is no way to read 'while Enrage is up' - so "
              "the Enrage condition is dropped and the bonus is gated on "
              "bear form instead, which is the part that can be enforced. "
              "ability_druid_enrage_potency was considered and rejected: "
              "druid_enrage is effect_type 'restore_resource' with NO "
              "stat_mods, so _potency would be silent dead data "
              "(qa_ability_scoped_fields.py).")

T.node("mangle", "Mangle",
       "Teaches Mangle, a wound that will not close.",
       5, -2, 1, node_type="active",
       effects={"unlock_ability": "druid_mangle"},
       connected_to=["king_of_the_jungle"],
       source="WotLK row 8, kept as a talent because IT IS ONE in the real "
              "tree. NOTE this requires druid_mangle to be requires_talent "
              "in data/abilities/druid.json; it was form-gated only before "
              "this rebuild, so the gate is set alongside this builder, the "
              "same treatment moonkin/tree_of_life/dire_bear got earlier "
              "this session. A FORM GATE IS NOT A TALENT GATE: without the "
              "flag, this node would unlock an ability every druid already "
              "had, which is precisely the 'three talent points buying "
              "nothing' bug Kyle flagged.")

T.node("improved_mangle", "Improved Mangle",
       "Reduces the cost of your Mangle by 3 per rank.",
       5, 0, 3,
       effects={"ability_druid_mangle_cost": 3},
       connected_to=["mangle"],
       source="WotLK row 8: 'Reduces the cooldown of your Mangle (Bear) by "
              "0.5-1.5 sec and reduces the energy cost of your Mangle (Cat) "
              "by 2-6.' Mangle is ONE ability here with a cooldown of 1 "
              "turn, which is already the floor talented_cooldown clamps "
              "to - so a cooldown reduction would be dead on arrival and "
              "only the cost half is built. Mangle costs 30, so three ranks "
              "cut it by nearly a third.")

T.node("rend_and_tear", "Rend and Tear",
       "Increases the damage of your Maul and Shred by 4% per rank.",
       5, 2, 5,
       effects={"ability_druid_maul_damage": 0.04,
                "ability_druid_shred_damage": 0.04},
       connected_to=["mangle"],
       source="WotLK row 9: 'Increases damage done by your Maul and Shred "
              "attacks on bleeding targets by 4%-20%, and increases the "
              "critical strike chance of your Ferocious Bite on bleeding "
              "targets.' DEPARTURE - NOTHING READS A DEBUFF ON THE TARGET, "
              "one of the hardest confirmed engine limits, so the bleeding "
              "condition is dropped from both halves. The Ferocious Bite "
              "clause is dropped entirely rather than made unconditional, "
              "because Feral Aggression at tier 0 already buffs that "
              "ability and two unconditional Ferocious Bite nodes would "
              "read as one talent printed twice.")

T.node("primal_gore", "Primal Gore",
       "Increases the damage of your bleeds by 15%.",
       5, 4, 1, effects={"dot_damage": 0.15},
       connected_to=["rend_and_tear"],
       source="WotLK row 9: 'Grants the periodic damage from your Lacerate "
              "and Rip abilities the ability to critically hit.' DEPARTURE, "
              "and the same one Pandemic hit in warlock_affliction: DOTS "
              "NEVER ROLL CRIT in this engine - there is no mechanism at "
              "all - so the talent's entire content is unbuildable and "
              "becomes flat dot damage, which delivers roughly the same "
              "expected value without the variance. Lacerate and Rip do not "
              "exist either; Rake is the druid's bleed here. dot_damage is "
              "a FRACTION.")

# ----------------------------------------------------- tier 6 (row 10)
T.node("berserk", "Berserk",
       "Teaches Berserk, a brief and total abandon.",
       6, 0, 1, node_type="active",
       effects={"unlock_ability": "druid_berserk"},
       connected_to=["primal_gore"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "druid_berserk, which is requires_talent. Already at its real "
              "row in the outgoing tree.")


def main():
    return T.write(was="24 nodes, 66 points - NO-TOUCH rule retired by Kyle "
                       "on 5 Nov")


if __name__ == "__main__":
    sys.exit(main())
