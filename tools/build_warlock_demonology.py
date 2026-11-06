#!/usr/bin/env python3
"""Rebuild Warlock Demonology from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_warlock_demonology.py

SOURCE: data/reference/wotlk/warlock.json (from Spell.dbc). The real 27
talents and 71 points, read out of the reference rather than recalled -
A FIRST DRAFT OF THIS FILE WAS BUILT FROM MEMORY AND WAS WRONG: it put
six nodes on the wrong row and invented a talent called 'Improved
Voidwalker', which is a CLASSIC talent that does not exist in WotLK,
while omitting Master Demonologist and Nemesis, which do. The real list
is now read first and every row below is the reference's own.

ROLE: the demon does the work. The warlock's own survivability comes from
Stamina and Soul Link, and the damage comes through the pet.

THIS TREE HITS THE PET WALL, exactly as Hunter Beast Mastery did, and
harder - Demonology is MORE pet-centric than BM. The engine exposes
THREE live pet keys and nothing else (entities/pet.py:139-146):

    pet_damage, pet_health, pet_armor

pet_crit and pet_haste are DEAD - measured, not assumed. PETS NEVER FIRE
PROCS: there is no fire_proc_trigger anywhere in entities/pet.py, so
every real talent reading 'when your demon hits' is unbuildable at the
root. Demons also have NO RESOURCE, which kills Mana Feed outright, and
nothing counts how many pets are alive.

Six real talents that are ABOUT the demon therefore land on three keys,
stacking pet_damage to +104% at a full 56-point spend.

THAT WAS MEASURED ON A LIVE PET, NOT INFERRED FROM THE SIM. An earlier
pass "cleared" the identical Hunter Beast Mastery pile-up by observing
that sim_class_balance.py put the Hunter inside the spread - BUT THAT SIM
CONTAINS NO PET MODELLING AT ALL (grep 'pet' in tools/sim_class_balance.py
returns nothing), so it could not have detected a pet problem either way.
That check was vacuous and the same claim on build_hunter_beast_mastery.py
has been corrected. The real measurement, on a level-60 imp:

    no talents   ap=78  sp=137  hp=886
    affliction   ap=85  sp=150  hp=886   (pet_damage 0.10)
    demonology   ap=159 sp=279  hp=1169  (pet_damage 1.04)
    destruction  ap=85  sp=150  hp=886   (pet_damage 0.10)

A roughly doubled demon on the spec whose entire identity is the demon is
defensible, and Demonology pays for it: it is the only Warlock spec with
no crit talent, no per-school damage talent and no crit-damage talent, so
the owner's own output is the weakest of the three. The trade is the point.

SEPARATE PRE-EXISTING FINDING, NOT CAUSED BY THESE TALENTS AND NOT FIXED
HERE: a level-60 warlock has spell_power 15 while their untalented imp has
137 - the pet out-stats its owner by roughly 9x because pet templates
scale off their own level curve rather than the owner's. This affects
Hunter equally. It is a pet-template balance question for its own pass,
and it is flagged rather than quietly patched inside a talent rebuild.

IF DEMONOLOGY EVER READS AS OVERTUNED, THE PET KEY PILE-UP IS THE FIRST
PLACE TO LOOK, and the fix is a real pet talent bus, not shaving these
numbers.

DEMONIC KNOWLEDGE survives translation by luck: '+12% spell damage from
your demon's Stamina and Intellect' cannot read the DEMON, but
spell_power_from_stamina_pct reads the WARLOCK's Stamina, which Demonic
Embrace in this same tree inflates. NOTE the *_from_*_pct family is a
FRACTION READ AS A RAW MULTIPLIER (character.py:1551), so authoring 4 for
'4%' would grant FOUR TIMES the stat.

PROC COUNT FALLS 10 -> 2, AND THAT IS CORRECT. The outgoing tree had ten
procs; only TWO of the real 27 talents have chance-based text (Fel
Synergy, which is 'heals you for % of damage you deal', and Molten Core,
which is a literal 'have a 6%-18% chance'). Both are built as procs. The
other eight outgoing procs were invented, not faithful - on_cast mana
returns and on_kill buffs attached to talents whose real text is a flat
passive. This is the inverse of the Mage Arcane mistake, where a proc
count that FELL signalled real damage; here the real tree is genuinely
near-all-passive, which was checked against the reference rather than
assumed. DO NOT "RESTORE" PROCS HERE to make the number look better.

DROPPED, 4 points: Mana Feed (demons have no resource), Master Conjuror
(Firestone and Spellstone do not exist - no item system), Summon Felguard
(no felguard ability). 71 - 4 = 67 points, comfortably over the 56 a
level-60 pure spec must be able to spend.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

DEMONS = ("imp", "voidwalker", "succubus", "felhunter")

T = Tree("warlock_demonology", "Warlock Demonology",
         "The demon fights, the warlock endures - power borrowed and paid "
         "for in flesh.")

# ----------------------------------------------------- tier 0 (rows 0)
T.node("improved_healthstone", "Improved Demon Armor",
       "Increases the armor your Demon Armor grants by 10% per rank.",
       0, -6, 2,
       effects={"ability_warlock_demon_armor_potency": 0.10},
       source="WotLK row 0 'Improved Healthstone': 'Increases the amount of "
              "Health restored by your Healthstone by 10%/20%.' "
              "HEALTHSTONES DO NOT EXIST - there is no item-creation system "
              "at all - so the node is retargeted onto Demon Armor, the "
              "Demonology defensive that does exist, keeping the "
              "10%-per-rank shape. ability_<id>_potency scales the "
              "ability's own stat_mods, which for Demon Armor is its armor "
              "grant. It stacks with Demonic Aegis, as the real tree's two "
              "separate armour talents do.")

T.node("improved_imp", "Improved Imp",
       "Increases your demon's damage by 10% per rank.",
       0, -4, 3, effects={"pet_damage": 0.10},
       source="WotLK row 0: 'Increases the effect of your Imp's Firebolt, "
              "Blood Pact and Fire Shield by 10%/20%/30%.' Individual pet "
              "ABILITIES are not addressable - there is no "
              "per-pet-ability talent key - so it becomes general pet "
              "damage. First of six real demon talents that must land on "
              "the three live pet keys; see the module docstring.")

T.node("demonic_embrace", "Demonic Embrace",
       "Increases your total Stamina by 3% per rank.",
       0, -2, 3, effects={"stamina_pct": 3.0},
       source="WotLK row 0, built verbatim: 'Increases your total Stamina "
              "by 4%/7%/10%' - stepped in the real tree, flattened to 3% "
              "per rank, which lands within a point of the real total. "
              "stamina_pct is PERCENTAGE POINTS: it is read off `bonuses` "
              "at character.py:1262 and DIVIDED BY 100, which is why a "
              "literal read-site probe finds nothing and the key is "
              "nonetheless LIVE. Authoring 0.03 would be a 0.03% bonus. "
              "This node is Demonic Knowledge's whole reason for working.")

T.node("fel_synergy", "Fel Synergy",
       "Your attacks heal you for 5% of the damage per rank as your demon "
       "feeds it back.",
       0, 0, 2,
       proc={"trigger": "on_weapon_swing", "chance": 50, "icd": 0,
             "leech_pct": 0.05},
       source="WotLK row 0: 'Your summoned demon heals you for 15%/30% of "
              "the damage you deal.' DEPARTURE ON THE SOURCE, which is "
              "forced: PETS NEVER FIRE PROCS - entities/pet.py contains no "
              "fire_proc_trigger at all - so nothing a demon does can be a "
              "trigger. Note the real talent's direction is already "
              "inverted (the demon heals YOU off YOUR damage), so this "
              "rides the warlock's own swings, the nearest real trigger. "
              "leech_pct is one of only three payloads that read the "
              "triggering hit's amount. 5% rather than 15% because a "
              "warlock swinging a staff is a last resort, not a rotation. "
              "CHANCE IS 50, NOT 100: only a proc's CHANCE scales with "
              "points, never its payload, so a 2-rank node at 100% would "
              "give rank 2 nothing - check_talent_balance.py caught exactly "
              "that in the first draft. 50 x 2 = 100 at full rank.")

# ----------------------------------------------------- tier 1 (rows 1-2)
T.node("improved_health_funnel", "Improved Health Funnel",
       "Increases the health your Health Funnel transfers by 10% per rank.",
       1, -6, 2,
       effects={"ability_warlock_health_funnel_healing": 0.10},
       connected_to=["improved_healthstone"],
       source="WotLK row 1, built verbatim: 'Increases the amount of health "
              "transferred by your Health Funnel spell by 10%/20%.' "
              "warlock_health_funnel EXISTS, so this is one of the few "
              "Demonology nodes that needs no translation at all. USES "
              "_healing, not _potency or _damage - Health Funnel's content "
              "is a heal, and _damage here would be SILENT DEAD DATA, the "
              "mistake that left 18 talents dead across four classes.")

T.node("demonic_brutality", "Demonic Brutality",
       "Increases your demon's damage by 3% per rank.",
       1, -4, 3, effects={"pet_damage": 0.03},
       connected_to=["improved_imp"],
       source="WotLK row 1: 'Increases the critical strike chance of your "
              "Felguard's Cleave and the effect of Intercept.' The Felguard "
              "does not exist, pet_crit IS DEAD (measured on a live pet - "
              "no attribute moved), and there is no charge system for "
              "Intercept. All three halves blocked, so it becomes the one "
              "pet key that works. Second of six.")

T.node("fel_vitality", "Fel Vitality",
       "Increases your maximum health and your demon's health by 3% per "
       "rank.",
       1, -2, 3,
       effects={"max_health_pct": 0.03, "pet_health": 0.03},
       connected_to=["demonic_embrace"],
       source="WotLK row 1: 'Increases your maximum health and mana by "
              "1%/2%/3%.' Mana is swapped for the demon's health, which is "
              "closer to Demonology's intent and uses pet_health. "
              "max_health_pct is a FRACTION (character.py:1411, NOT "
              "divided) while stamina_pct one tier up is POINTS - two "
              "health keys with opposite conventions, and audit_talents is "
              "the only thing that catches a mix-up.")

T.node("improved_succubus", "Improved Succubus",
       "Increases your demon's damage by 4% per rank.",
       1, 0, 3, effects={"pet_damage": 0.04},
       connected_to=["fel_synergy"],
       source="WotLK row 2: 'Increases the effect of your Succubus' "
              "Lash of Pain and Soothing Kiss, and the duration of "
              "Seduction and Lesser Invisibility.' No per-pet-ability key, "
              "and there is NO STEALTH SYSTEM for the invisibility half. "
              "Third of six. (A first draft of this file invented "
              "'Improved Voidwalker' here, which is a CLASSIC talent, not a "
              "WotLK one - the reference is now read rather than recalled.)")

T.node("soul_link", "Soul Link",
       "Your demon shares your pain - you take 10% less damage.",
       1, 2, 1, effects={"damage_taken_pct": -0.10},
       connected_to=["fel_synergy"],
       source="WotLK row 2, the signature Demonology talent: '20% of all "
              "damage you take is instead taken by your demon.' DEPARTURE - "
              "there is NO DAMAGE REDIRECTION and no threat transfer in this "
              "engine, confirmed by probe rather than assumed. What a player "
              "feels is that they take less, so it is straight mitigation "
              "at 10%. The real 'while your demon lives' clause is NOT "
              "enforced and is deliberately left out of the description "
              "too, because nothing reads a live pet count - stating it "
              "would be a lie in the tooltip. BARE damage_taken_pct is read "
              "RAW ON BOTH SIDES, so -0.10 is 10%; this is the key that was "
              "authored as 5.0 in Warrior Death Wish and meant 500%.")

T.node("fel_domination", "Fel Domination",
       "Your demon arrives braced - 20% more armor.",
       1, 4, 1,
       effects={"pet_armor": 0.20},
       connected_to=["soul_link"],
       source="WotLK row 2: 'Your next Imp, Voidwalker, Succubus, Felhunter "
              "or Felguard Summoning spell has its casting time reduced by "
              "5.5 sec and its Mana cost reduced by 50%.' DEPARTURE - there "
              "is no next-cast-modifier mechanic at all (no cast counter, no "
              "streak, no accumulator). The first draft made it a shorter "
              "cooldown on all four summons AND ALL FOUR KEYS WERE DEAD - "
              "every warlock_summon_* ability has cooldown 0, so the node "
              "did NOTHING AT ALL. Caught by "
              "tools/qa_ability_scoped_fields.py, which exists because "
              "audit_talents checks unit conventions and probe --audit-all "
              "only checks the ability EXISTS; both passed this. Summoning "
              "here is free, instant and off cooldown, so the real talent "
              "has NO CONTENT TO PORT in any form. It is retargeted onto "
              "the demon itself. pet_armor rather than pet_damage "
              "deliberately: pet_damage already carries six talents and "
              "reaches +104% in this tree, and pet_armor carries one.")

T.node("demonic_aegis", "Demonic Aegis",
       "Increases the armor your Demon Armor grants by 10% per rank.",
       1, 6, 3,
       effects={"ability_warlock_demon_armor_potency": 0.10},
       connected_to=["soul_link"],
       source="WotLK row 2, built verbatim for the one armour spell we "
              "have: 'Increases the effectiveness of your Demon Armor and "
              "Fel Armor spells by 10%/20%/30%.' Fel Armor does not exist.")

# ----------------------------------------------------- tier 2 (rows 3-4)
T.node("unholy_power", "Unholy Power",
       "Increases your demon's damage by 4% per rank.",
       2, -2, 5, effects={"pet_damage": 0.04},
       connected_to=["demonic_brutality"],
       source="WotLK row 3, built verbatim: 'Increases the damage done by "
              "your Voidwalker, Succubus, Felhunter and Felguard's melee "
              "attacks by 4%-20%.' This is the one demon talent whose real "
              "text IS general pet damage, so it needs no translation at "
              "all. Fourth of six.")

T.node("master_summoner", "Master Summoner",
       "Increases your demon's health by 5% per rank.",
       2, 0, 2,
       effects={"pet_health": 0.05},
       connected_to=["improved_succubus"],
       source="WotLK row 3: 'Reduces the casting time of your summoning "
              "spells by 2/4 sec and the Mana cost by 20%/40%.' No cast "
              "times, so only the mana half survives, at 10% per rank "
              "rather than 20% because summoning is a one-off rather than a "
              "rotational cost. THE FIRST DRAFT DID EXACTLY THAT AND ALL "
              "FOUR KEYS WERE DEAD: every warlock_summon_* ability has cost "
              "0 on every rank, so there was nothing to reduce and the node "
              "did nothing. Same cause and same catch as Fel Domination "
              "above (tools/qa_ability_scoped_fields.py). Summoning is free "
              "AND instant AND off cooldown, so both of this tree's "
              "summoning talents have no content in this engine and both "
              "are retargeted onto the demon. pet_health, not pet_damage, "
              "for the pile-up reason given on Fel Domination. Mana Feed "
              "and Master Conjuror, the other two real "
              "talents on these rows, are DROPPED: demons have no resource, "
              "and Firestone and Spellstone are items in a game with no "
              "item-creation system.")

# ----------------------------------------------------- tier 3 (row 5)
T.node("master_demonologist", "Master Demonologist",
       "You and your demon grow together - 2% more demon damage and 1% less "
       "damage taken per rank.",
       3, -2, 5,
       effects={"pet_damage": 0.02, "damage_taken_pct": -0.01},
       connected_to=["unholy_power"],
       source="WotLK row 5: 'Grants both you and your summoned demon an "
              "effect as long as that demon is active' - a DIFFERENT effect "
              "per demon (Imp grants fire damage, Voidwalker threat and "
              "mitigation, Succubus damage, Felhunter resistances). NOTHING "
              "BRANCHES ON WHICH PET IS ACTIVE in this engine, so the five "
              "variants collapse into the two things common to all of them: "
              "the demon hits harder and the warlock takes less. Fifth of "
              "six. This talent was MISSING ENTIRELY from the first draft "
              "of this file, which is why the reference is now read first.")

T.node("molten_core", "Molten Core",
       "Your Immolate and Corruption have a 5% chance per rank to raise "
       "your spell damage by 10% for 3 turns.",
       3, 0, 3,
       proc={"trigger": "on_damage_cast", "chance": 5, "icd": 0,
             "ability_filter": ["warlock_immolate", "warlock_corruption"],
             "apply_effect": {"effect_id": "molten_core",
                              "name": "Molten Core",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"damage_dealt_pct": 10.0},
                              "on_target": False}},
       connected_to=["master_demonologist"],
       source="WotLK row 5: 'Your shadow and fire damage spells have a "
              "6%-18% chance to increase your spell damage by 6% and reduce "
              "the cast time of Soul Fire.' KEPT AS A PROC because the real "
              "text IS proc-shaped - this is the Mage Arcane lesson, where "
              "flattening proc-shaped talents made the tree worse. Soul "
              "Fire does not exist, so only the spell-damage half lands, "
              "and the filter is the warlock's one fire dot and one shadow "
              "dot. The chance IS rank-scaled by the engine (capped at 100, "
              "only when max_points > 1) while the PAYLOAD IS NOT, which is "
              "the project's existing multi-rank proc idiom. NOTE the "
              "stat_mod is damage_dealt_pct in PERCENTAGE POINTS - "
              "spell_damage here would be SILENT DEAD DATA inside a status "
              "effect, which is the single most common bug class in this "
              "project.")

# ----------------------------------------------------- tier 4 (rows 6-7)
T.node("demonic_resilience", "Demonic Resilience",
       "Reduces damage you take by 2% per rank and increases your demon's "
       "health by 5% per rank.",
       4, -6, 3,
       effects={"damage_taken_pct": -0.02, "pet_health": 0.05},
       connected_to=["master_demonologist"],
       source="WotLK row 6: 'Reduces the chance you'll be critically hit by "
              "melee and spells by 1%-3% and reduces all damage your "
              "summoned demon takes by 5%-15%.' crit_taken_reduction IS A "
              "DEAD TALENT KEY - measured, and the same dead key that was "
              "replaced in sun_cleric_blessings this session - so the "
              "player half becomes plain mitigation. There is no pet "
              "MITIGATION key either, so the demon half becomes pet_health, "
              "the same survivability by another route.")

T.node("demonic_empowerment", "Demonic Empowerment",
       "Your demon hits 8% harder and has 8% more health.",
       4, -4, 1,
       effects={"pet_damage": 0.08, "pet_health": 0.08},
       connected_to=["demonic_resilience"],
       source="WotLK row 6: an ACTIVE ability granting your current demon a "
              "different buff depending on which demon it is - Imp gets "
              "haste, Voidwalker health, Succubus invisibility, Felguard a "
              "stun break. FOUR separate blockers: there is no "
              "warlock_demonic_empowerment ability to unlock, nothing "
              "branches on which pet is active, pet_haste is DEAD, and "
              "there is no stealth system. Reduced to a passive giving every "
              "demon the two things that do work. Sixth of six, and the most "
              "compromised node in the tree - it is a 1-point node doing a "
              "passive's job, which is honest about how little survived.")

T.node("demonic_knowledge", "Demonic Knowledge",
       "You gain spell power equal to 4% of your Stamina per rank.",
       4, -2, 3,
       effects={"spell_power_from_stamina_pct": 0.04},
       connected_to=["molten_core"],
       source="WotLK row 6: 'Increases your spell damage by an amount equal "
              "to 4%/8%/12% of the total of your active demon's Stamina "
              "plus Intellect.' THE DEMON'S stats cannot be read, but the "
              "WARLOCK's Stamina can, and Demonic Embrace at tier 0 of this "
              "same tree inflates it - so the talent's actual flavour, "
              "stamina becoming spell power, survives with the source "
              "swapped, and the real 4%-per-rank is kept exactly. CRITICAL "
              "CONVENTION: the *_from_*_pct family is a FRACTION READ AS A "
              "RAW MULTIPLIER (character.py:1551, gained = source * pct), so "
              "authoring 4 for '4%' would grant FOUR TIMES the warlock's "
              "Stamina as spell power. stamina is a valid conversion SOURCE "
              "and spell_power a valid TARGET (STAT_CONVERSION_TARGETS, "
              "character.py:18); stamina is NOT a valid target, so the "
              "reverse would silently do nothing.")

T.node("demonic_tactics", "Demonic Tactics",
       "Increases your critical strike chance by 1% per rank and your "
       "demon's damage by 3% per rank.",
       4, 0, 5,
       effects={"crit_chance": 1.0, "pet_damage": 0.03},
       connected_to=["molten_core"],
       source="WotLK row 7, built verbatim for the half that works: "
              "'Increases melee and spell critical strike chance for you "
              "and your summoned demon by 1%-5%.' pet_crit IS DEAD - "
              "measured on a live pet, no attribute moved - so the demon's "
              "half becomes pet_damage. crit_chance is PERCENTAGE POINTS.")

T.node("decimation", "Decimation",
       "Your spells hit wounded targets 10% harder per rank.",
       4, 2, 2,
       effects={"low_health_damage_pct": 0.10},
       connected_to=["demonic_tactics"],
       source="WotLK row 7: 'When your Shadow Bolt, Incinerate or Soul Fire "
              "hits a target at or below 35% health, the cast time of your "
              "next Soul Fire is reduced by 20%/40%.' Soul Fire and "
              "Incinerate do not exist and there are no cast times either "
              "way, so THE EXECUTE-RANGE CONDITION is what is kept - it is "
              "the talent's whole identity. low_health_damage_pct reads the "
              "TARGET's health with a DEFAULT 0.35 THRESHOLD, which is "
              "exactly the real talent's 35%, so low_health_threshold_pct "
              "is NOT authored - the kit refuses that key outright because "
              "it is UNSCALED, SUMS across talents, and is SHARED with the "
              "actor-reading reduction key. These values are FRACTIONS and "
              "PER RANK: 0.15 on a 3-point node measured as 45% on a live "
              "rogue earlier this session.")

# ----------------------------------------------------- tier 5 (rows 8-9)
T.node("improved_demonic_tactics", "Improved Demonic Tactics",
       "Increases your critical strike chance by 1% per rank.",
       5, -2, 3, effects={"crit_chance": 1.0},
       connected_to=["demonic_tactics"],
       source="WotLK row 8: 'Increases your summoned demon's spell critical "
              "strike chance by an amount equal to 10%/20%/30% of your "
              "own.' TWO blockers: pet_crit is DEAD, and nothing computes "
              "one stat from another ON THE PET (the *_from_*_pct family "
              "lands on the CHARACTER only). Rather than make this a "
              "SEVENTH pet_damage node - the pile-up is already six talents "
              "deep and that is the documented risk in this tree - it "
              "becomes the warlock's own crit, which is at least the stat "
              "the real talent is about. Summon Felguard, the other row-8 "
              "talent, is DROPPED: no felguard ability exists.")

T.node("nemesis", "Nemesis",
       "Reduces the cooldown of your Metamorphosis by 1 turn per rank.",
       5, 0, 3,
       effects={"ability_warlock_metamorphosis_cooldown": 1},
       connected_to=["decimation"],
       source="WotLK row 8, built verbatim for the one ability we have: "
              "'Reduces the cooldown of your Metamorphosis, Demonic "
              "Empowerment and Demon Charge by 10%/20%/30%.' Demon Charge "
              "does not exist and Demonic Empowerment is a passive here, so "
              "only Metamorphosis remains - which is fitting, since it "
              "makes this node the capstone's natural prerequisite. FLAT "
              "turns rather than _cooldown_pct because Metamorphosis is a "
              "long cooldown and the percentage form clamps at 0.90.")

T.node("demonic_pact", "Demonic Pact",
       "Increases your spell damage by 2% per rank.",
       5, 2, 5, effects={"spell_damage": 0.02},
       connected_to=["improved_demonic_tactics"],
       source="WotLK row 9: 'Your summoned demon grants you and your party "
              "spell power equal to 2%-10% of your own.' A TALENT EFFECT "
              "CAN NEVER REACH AN ALLY - only a PARTY-TARGETED ABILITY can "
              "(abilities.py:2064) - so the party half is unbuildable and "
              "the raid-buff identity is lost. The self half is kept as "
              "direct spell damage rather than a conversion, because "
              "spell_power from spell_power is circular. A genuine loss, "
              "and one for the list of things a real party-buff talent "
              "channel would restore.")

# ----------------------------------------------------- tier 6 (row 10)
T.node("metamorphosis", "Metamorphosis",
       "Teaches Metamorphosis, becoming the demon you command.",
       6, 0, 1, node_type="active",
       effects={"unlock_ability": "warlock_metamorphosis"},
       connected_to=["nemesis"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "warlock_metamorphosis, which is requires_talent. Already at "
              "its real row in the outgoing tree.")


def main():
    return T.write(was="22 nodes, 61 points - 10 proc, 5 ability-scoped, "
                       "5 flat stat, 1 unlock, 1 conditional")


if __name__ == "__main__":
    sys.exit(main())
