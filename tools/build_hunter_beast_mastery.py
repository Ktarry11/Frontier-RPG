#!/usr/bin/env python3
"""Rebuild Hunter Beast Mastery from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_hunter_beast_mastery.py

SOURCE: data/reference/wotlk/hunter.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/hunter.md.

ROLE: the pet is the weapon. Over half this tree's real talents modify the
pet rather than the hunter.

THE PET IS THE WALL, AND IT IS A HARD ONE. This engine's pets are far
simpler than WotLK's, and the limits were measured rather than assumed:

    pet_damage / pet_health / pet_armor   LIVE, read at pet.py:139-146
    pet_crit / pet_haste                  DEAD - no read site anywhere
    PETS NEVER FIRE PROCS                 there is no fire_proc_trigger in
                                          entities/pet.py at all
    no pet resource                       no Focus, nothing to regenerate
    no live pet count                     nothing reads whether a pet is out

So of Beast Mastery's 26 real talents, the ones that work are the three
scaling keys. Everything written on pet crit, pet attack speed, pet Focus,
a pet's critical hit, or "while your pet is active" has no mechanism at
all. Each is rebuilt as the nearest thing that does work - usually pet
damage, or the hunter's own stat - and each node says which.

That makes this the most heavily-substituted tree in the project, and it is
honest to say so rather than present it as a faithful port.

THINGS THAT ARE REAL AND BUILT EXACTLY: Endurance Training (pet and own
health), Thick Hide (pet and own armour), Unleashed Fury (pet damage),
Kindred Spirits (pet damage), Focused Fire (own damage), Catlike Reflexes
(own dodge), Serpent's Swiftness (own haste), The Beast Within (own
damage), Cobra Strikes (a real on-crit proc).

ABILITIES THE REAL TREE WANTS AND WE LACK: Intimidation, Bestial Wrath,
Master's Call, Aspect of the Cheetah/Pack/Monkey/Viper, Kill Shot. Aspect
Mastery, Pathfinding, Improved Aspect of the Monkey and Beast Mastery
(the capstone, which teaches taming exotic pets) are DROPPED.

UNIT CONVENTIONS: pet_damage / pet_health / pet_armor / armor_pct /
all_damage are FRACTIONS; agility_pct / stamina_pct / dodge / haste /
crit_chance_physical are PERCENTAGE POINTS; max_health_pct is a FRACTION.

KEPT MANDATORY: none in this tree - Beast Mastery unlocks no gated
ability, so every node here is a design choice rather than a requirement.

PET DAMAGE STACKS TO +106% ACROSS THIS TREE, and that is measured rather
than accidental. Five real talents that are NOT pet-damage talents -
Ferocity (pet crit), Bestial Discipline (pet Focus), Animal Handler (pet
attack power), Frenzy (pet attack speed), Serpent's Swiftness (pet attack
speed) - all have to land on pet_damage, because it is one of only three
pet keys that exist. Each substitution is individually faithful and
together they pile onto one key.

THE ORIGINAL CHECK HERE WAS VACUOUS AND IS CORRECTED. This docstring used
to say the pile-up "was checked rather than assumed" because
tools/sim_class_balance.py reported the Hunter inside the spread at every
level with beast_mastery its best build. THAT SIM CONTAINS NO PET
MODELLING AT ALL - grep 'pet' in tools/sim_class_balance.py returns
nothing - so it could not have detected a pet problem in either
direction, and citing it was false reassurance. The error was caught while
building warlock_demonology, which hits the identical wall.

The honest measurement is on a live pet, and on a level-60 imp the
equivalent Warlock pile-up roughly doubles the pet (ap 78 -> 159,
sp 137 -> 279). A doubled pet on the pet spec is defensible, and the spec
pays for it elsewhere in the tree. BUT THE CLAIM NOW RESTS ON A DIRECT
MEASUREMENT, not on a sim that cannot see pets. If a pet-aware sim is ever
added, re-run this tree against it; this node set is where to look first.

SEPARATE PRE-EXISTING FINDING, not caused by these talents: pet templates
scale off their own level curve rather than the owner's, so an untalented
level-60 pet out-stats its owner by a wide margin. That is a pet-template
balance question for its own pass, flagged rather than patched inside a
talent rebuild.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("hunter_beast_mastery", "Hunter Beast Mastery",
         "The bond with the beast - your pet as the sharper half of the "
         "pair.")

# ----------------------------------------------------------------- tier 0
T.node("improved_aspect_of_the_hawk", "Improved Aspect of the Hawk",
       "Increases the effect of your Aspect of the Hawk by 10% per rank.",
       0, -1, 5,
       effects={"ability_hunter_aspect_of_the_hawk_potency": 0.10},
       source="WotLK row 0: 'While Aspect of the Hawk is active, all normal "
              "ranged attacks have a 2%-10% chance of increasing ranged "
              "attack speed by 15% for 8 sec.' DEPARTURE - a talent cannot "
              "attach a proc that is conditional on another buff being "
              "active, because nothing reads whether the ACTOR carries a "
              "specific effect. Delivered as the aspect simply being "
              "better. ability_<id>_potency scales its own stat_mods. Kept "
              "from the outgoing tree, which used _duration instead.")

T.node("endurance_training", "Endurance Training",
       "Increases your pet's health by 2% per rank and your own by 1% per "
       "rank.",
       0, 1, 5,
       effects={"pet_health": 0.02, "max_health_pct": 0.01},
       source="WotLK row 0, built verbatim with both halves: 'Increases the "
              "health of your pet by 2%-10% and your total health by "
              "1%-5%.' pet_health is a FRACTION read at pet.py:143 - one of "
              "only three pet keys that work. The outgoing version granted "
              "FLAT stamina, which is neither half and is also not a valid "
              "STAT_CONVERSION_TARGET.")

# ----------------------------------------------------------------- tier 1
T.node("focused_fire", "Focused Fire",
       "Increases all your damage by 2% per rank.",
       1, -5, 2, effects={"all_damage": 0.02},
       connected_to=["improved_aspect_of_the_hawk"],
       source="WotLK row 1: 'All damage caused by you is increased by "
              "1%/2% while your pet is active.' DEPARTURE on the condition "
              "only - NOTHING reads whether a pet is currently out - so the "
              "damage is unconditional at the real per-rank value. The "
              "outgoing node had an EMPTY effects dict and no proc.")

T.node("thick_hide", "Thick Hide",
       "Increases your pet's armor by 13% per rank and your own by 3% per "
       "rank.",
       1, -3, 3,
       effects={"pet_armor": 0.13, "armor_pct": 3.0},
       connected_to=["improved_aspect_of_the_hawk"],
       source="WotLK row 1, built verbatim with both halves: 'Increases the "
              "armor rating of your pets by 13%-40% and your armor "
              "contribution from items by 3%-10%.' This is the one talent in "
              "the whole WotLK data set with NO description in the source "
              "file - the text was filled from knowledge and marked as such "
              "in data/reference/wotlk_worksheets/hunter.md, so it is the "
              "one second-hand line in 741 talents. pet_armor is a FRACTION "
              "read at pet.py:146.")

T.node("unleashed_fury", "Unleashed Fury",
       "Increases your pet's damage by 3% per rank.",
       1, -1, 5, effects={"pet_damage": 0.03},
       connected_to=["endurance_training"],
       source="WotLK row 1, built verbatim: 'Increases the damage done by "
              "your pets by 3%-15%.' pet_damage is a FRACTION read at "
              "pet.py:139 and is the single most important key in this "
              "tree. The outgoing version granted the HUNTER's Steady Shot "
              "damage, which is not this talent at all.")

T.node("improved_revive_pet", "Improved Revive Pet",
       "Reduces the cooldown and cost of your Revive Pet by 1 turn and 20% "
       "per rank.",
       1, 1, 2,
       effects={"ability_hunter_revive_pet_cooldown": 1,
                "ability_hunter_revive_pet_cost_pct": 0.20},
       connected_to=["endurance_training"],
       source="WotLK row 1: 'Revive Pet's casting time is reduced by 3/6 "
              "sec, mana cost is reduced by 20%/40%, and increases the "
              "health your pet returns with.' No cast times; the cost half "
              "is verbatim and the cast-time half becomes cooldown. Kept "
              "from the outgoing tree.")

# ----------------------------------------------------------------- tier 2
T.node("spirit_bond", "Spirit Bond",
       "You and your pet regenerate health over time.",
       2, -5, 2,
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 3,
             "apply_effect": {"effect_id": "spirit_bond",
                              "name": "Spirit Bond",
                              "effect_type": "hot", "duration": 3,
                              "potency": 30, "on_target": False}},
       connected_to=["focused_fire"],
       source="WotLK row 2: 'While your pet is active, you and your pet "
              "will regenerate 1%/2% of total health every 10 sec., and "
              "increases healing done to you and your pet.' DEPARTURE - "
              "nothing reads whether a pet is active, and a talent effect "
              "cannot reach the PET either (the pet reads only the three "
              "scaling keys from its owner). Delivered as a self-hot every "
              "third turn. Kept as a proc from the outgoing tree.")

T.node("improved_mend_pet", "Improved Mend Pet",
       "Increases the healing of your Mend Pet by 10% per rank and reduces "
       "its cost by 20% per rank.",
       2, -3, 2,
       effects={"ability_hunter_mend_pet_healing": 0.10,
                "ability_hunter_mend_pet_cost_pct": 0.20},
       connected_to=["thick_hide"],
       source="WotLK row 2: 'Reduces the mana cost of your Mend Pet spell "
              "by 10%/20% and gives it a 50% chance of cleansing one "
              "effect.' The cost half is verbatim; there is no dispel "
              "chance to add. USES _healing, not _damage - Mend Pet is a "
              "heal. Kept from the outgoing tree.")

T.node("ferocity", "Ferocity",
       "Increases your pet's damage by 2% per rank.",
       2, -1, 5, effects={"pet_damage": 0.02},
       connected_to=["unleashed_fury"],
       source="WotLK row 2: 'Increases the critical strike chance of your "
              "pet by 2%-10%.' DEPARTURE - pet_crit IS DEAD DATA. Probed: "
              "it reaches the talent bus and has zero read sites, and "
              "entities/pet.py reads only pet_damage, pet_health and "
              "pet_armor from its owner. A pet's crit chance cannot be "
              "raised at all, so the talent delivers the same thing crit "
              "delivers - more pet damage. Stacks with Unleashed Fury. It "
              "is Frenzy's prerequisite, preserved below. The outgoing node "
              "had an EMPTY effects dict.")

T.node("bestial_discipline", "Bestial Discipline",
       "Increases your pet's damage by 3% per rank.",
       2, 1, 2, effects={"pet_damage": 0.03},
       connected_to=["improved_revive_pet"],
       source="WotLK row 2: 'Increases the Focus regeneration of your pets "
              "by 50%/100%.' DEPARTURE - pets have NO RESOURCE in this "
              "engine. There is no Focus, nothing to regenerate and no key "
              "for it. A pet with more Focus attacks more, so it is "
              "delivered as pet damage. The outgoing version reduced the "
              "HUNTER's Steady Shot cost.")

# ----------------------------------------------------------------- tier 3
T.node("animal_handler", "Animal Handler",
       "Increases your pet's damage by 5% per rank.",
       3, -3, 2, effects={"pet_damage": 0.05},
       connected_to=["spirit_bond"],
       source="WotLK row 3: 'Increases your pet's attack power by 5%/10%, "
              "and increases the duration of your Master's Call effect.' "
              "There is no pet_attack_power key - the pet scales off "
              "pet_damage - and no Master's Call. pet_damage at the real "
              "per-rank value is the faithful translation. The outgoing "
              "version granted the HUNTER flat hit_rating.")

T.node("frenzy", "Frenzy",
       "Increases your pet's damage by 4% per rank.",
       3, -1, 5, effects={"pet_damage": 0.04},
       connected_to=["ferocity"],
       source="WotLK row 3: 'Gives your pet a 20%-100% chance to gain a 30% "
              "attack speed increase for 8 sec after dealing a critical "
              "strike.' DEPARTURE, and the clearest statement of this "
              "tree's problem: PETS NEVER FIRE PROCS. There is no "
              "fire_proc_trigger in entities/pet.py at all, so no pet event "
              "can drive anything, and pet_haste is dead data besides. Both "
              "halves of the real talent are unbuildable. Delivered as pet "
              "damage. The real talent requires Ferocity, which "
              "connected_to reproduces. The outgoing node had an EMPTY "
              "effects dict.")

T.node("catlike_reflexes", "Catlike Reflexes",
       "Increases your dodge by 1% per rank and your pet's armor by 3% per "
       "rank.",
       3, 1, 3,
       effects={"dodge": 1.0, "pet_armor": 0.03},
       connected_to=["bestial_discipline"],
       source="WotLK row 3, built with both halves: 'Increases your chance "
              "to dodge by 1%/2%/3% and your pet's chance to dodge by an "
              "additional 3%-9%.' There is no pet dodge key, so the pet "
              "half becomes armour, which is the pet's only real defensive "
              "knob. dodge is PERCENTAGE POINTS and pet_armor is a "
              "FRACTION - mixed conventions on one node. The outgoing node "
              "was a proc with an empty effects dict.")

# ----------------------------------------------------------------- tier 4
T.node("ferocious_inspiration", "Ferocious Inspiration",
       "Increases all your damage by 1% per rank.",
       4, -3, 3, effects={"all_damage": 0.01},
       connected_to=["animal_handler"],
       source="WotLK row 4: 'All party and raid members have all damage "
              "increased by 1%/2%/3% within 100 yards of your pet.' "
              "DEPARTURE - A TALENT EFFECT CAN NEVER REACH AN ALLY, and "
              "nothing reads a pet's position or presence. The real "
              "per-rank value applies to the hunter alone. It is "
              "Invigoration's prerequisite, preserved below.")

T.node("invigoration", "Invigoration",
       "Your critical strikes restore 100 mana.",
       4, -1, 2,
       proc={"trigger": "on_crit", "chance": 50, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 100}},
       connected_to=["ferocious_inspiration"],
       source="WotLK row 4: 'When your pet scores a critical hit with a "
              "special ability, you have a 50%/100% chance to instantly "
              "regenerate 10% of your total mana.' DEPARTURE on the trigger "
              "- PETS NEVER FIRE PROCS, so a pet's crit cannot be detected. "
              "It fires on the HUNTER's crit instead. grant_resource takes "
              "a FLAT amount with no pct_max, so 100 stands in for 10% of "
              "the pool. The real talent requires Ferocious Inspiration, "
              "reproduced. Kept as a proc from the outgoing tree.")

T.node("serpents_swiftness", "Serpent's Swiftness",
       "Increases your haste by 4% per rank and your pet's damage by 4% per "
       "rank.",
       4, 1, 5,
       effects={"haste": 4.0, "pet_damage": 0.04},
       connected_to=["catlike_reflexes"],
       source="WotLK row 4, built with both halves: 'Increases ranged "
              "combat attack speed by 4%-20% and your pet's melee attack "
              "speed by 4%-20%.' The hunter half is real haste; the pet half "
              "has no key (pet_haste is DEAD DATA, probed) so it becomes pet "
              "damage, which is what faster attacks deliver. It is Cobra "
              "Strikes' prerequisite, preserved below. The outgoing version "
              "granted the HUNTER crit on two shots.")

# ----------------------------------------------------------------- tier 5
T.node("longevity", "Longevity",
       "Reduces the cooldown of your Aspect of the Hawk and Aspect of the "
       "Wild by 1 turn per rank.",
       5, -3, 3,
       effects={"ability_hunter_aspect_of_the_hawk_cooldown": 1,
                "ability_hunter_aspect_of_the_wild_cooldown": 1},
       connected_to=["ferocious_inspiration"],
       source="WotLK row 5: 'Reduces the cooldown of your Bestial Wrath, "
              "Intimidation and Pet Special Abilities by 10%/20%/30%.' "
              "DEPARTURE - none of those three exist, and pets have no "
              "special abilities with cooldowns for a talent to touch. The "
              "two Aspects are this tree's real cooldowns, so the reduction "
              "lands there. Kept from the outgoing tree.")

T.node("the_beast_within", "The Beast Within",
       "Increases all your damage by 10%.",
       5, -1, 1, effects={"all_damage": 0.10},
       connected_to=["serpents_swiftness"],
       source="WotLK row 5: 'Increases all damage you deal by 10% and while "
              "your pet is under the effects of Bestial Wrath, you also go "
              "into a rage.' The 10% is REAL AND EXACT; the Bestial Wrath "
              "clause has no ability to hang on. The real talent requires "
              "Bestial Wrath, which does not exist here, so connected_to "
              "points at Serpent's Swiftness instead. The outgoing node had "
              "an EMPTY effects dict - 1 point for nothing.")

T.node("kindred_spirits", "Kindred Spirits",
       "Increases your pet's damage by 4% per rank.",
       5, 1, 5, effects={"pet_damage": 0.04},
       connected_to=["catlike_reflexes"],
       source="WotLK row 5: 'Increases your pet's damage by 4%-20% and you "
              "and your pet's movement speed by 10% while your pet is "
              "active.' The damage half is built verbatim; there is no "
              "movement speed. The outgoing version granted the HUNTER's "
              "auto-attack damage.")

T.node("cobra_strikes", "Cobra Strikes",
       "Your critical strikes have a 20% chance per rank to raise your pet's "
       "ferocity, increasing its damage for 3 turns.",
       5, 3, 3,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "apply_effect": {"effect_id": "cobra_strikes",
                              "name": "Cobra Strikes",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"damage_dealt_pct": 10.0},
                              "on_target": False}},
       connected_to=["serpents_swiftness"],
       source="WotLK row 5: 'You have a 20%-60% chance when you critically "
              "hit with Arcane Shot, Steady Shot or Kill Shot to cause your "
              "pet's next 2 special attacks to critically hit.' DEPARTURE - "
              "a talent effect cannot reach the PET (it reads only "
              "pet_damage/health/armor from its owner) and pet crit is dead "
              "data besides, so the buff lands on the HUNTER. The trigger "
              "and chance curve are real. NOTE the stat_mod is "
              "damage_dealt_pct in PERCENTAGE POINTS: all_damage would be "
              "SILENT DEAD DATA inside a status effect. Kept as a proc from "
              "the outgoing tree.")

# ----------------------------------------------------------------- tier 6
T.node("marked_for_death", "Marked for Death",
       "Increases the damage of your shots by 5% and your pet's damage by "
       "5%.",
       6, 0, 1,
       effects={"ability_hunter_steady_shot_damage": 0.05,
                "ability_hunter_arcane_shot_damage": 0.05,
                "ability_hunter_aimed_shot_damage": 0.05,
                "ability_hunter_multi_shot_damage": 0.05,
                "pet_damage": 0.05},
       connected_to=["kindred_spirits"],
       source="Real 3.3.5a's Beast Mastery capstone is Beast Mastery "
              "itself - 'teaches you to tame Exotic pets and increases your "
              "pet's total damage' - and taming exotic pets has no "
              "mechanism here at all, so that half is unbuildable. Marked "
              "for Death is a real MARKSMANSHIP talent (row 9) whose "
              "wording fits what is left ('increases your damage done by "
              "your shots and the damage done by your pet's special "
              "abilities by 5%'), so it takes the capstone slot. Recorded "
              "as a deliberate cross-tree borrow rather than an invention. "
              "The outgoing tree had Marked for Death here too, as a proc.")


def main():
    return T.write(was="23 nodes, 68 points - 12 proc, 7 ability-scoped, "
                       "3 flat stat (6 of the 12 procs had EMPTY effects "
                       "and did nothing)")


if __name__ == "__main__":
    sys.exit(main())
