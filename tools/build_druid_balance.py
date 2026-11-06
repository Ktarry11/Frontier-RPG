#!/usr/bin/env python3
"""Rebuild Druid Balance from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_druid_balance.py

SOURCE: data/reference/wotlk/druid.json (from Spell.dbc) - the real 28
talents and 75 points, every row read out of the reference and every
ambiguous talent's RANK TEXT read before authoring.

ROLE: Moonkin caster. Moonfire and Insect Swarm ticking under alternating
Wrath and Starfire, into Starfall.

THE UNLOCK ROWS WERE ALL WRONG and this is the main structural fix.
Balance owns four of the druid's talent-gated abilities and three sat at
the wrong tier:

    druid_insect_swarm   was tier 2, real row 4  -> tier 2   (already right)
    druid_moonkin_form   was tier 6, real row 6  -> tier 4   (Kyle's flag)
    druid_typhoon        was tier 6, real row 8  -> tier 5
    druid_starfall       was tier 3, real row 10 -> tier 6   (it is the CAPSTONE)

Starfall sitting at tier 3 was the worst of these - the tree's capstone
was buyable a third of the way up it.

DROPPED, 4 points of the real 75: Improved Faerie Fire (no Faerie Fire
ability exists) and Force of Nature (summons treants; there is no druid
pet template, and PETS NEVER FIRE PROCS even if there were). 71 points
remain against the 56 a level-60 pure spec must be able to spend.

THE BLOCKERS THAT SHAPE THIS TREE:
  - NO CAST TIMES, so Starlight Wrath and half of Celestial Focus have no
    content to port.
  - NOTHING READS A DEBUFF ON THE TARGET, which strips the condition off
    Improved Insect Swarm - the real talent's whole design.
  - A TALENT EFFECT CAN NEVER REACH AN ALLY (only a party-targeted
    ABILITY can, abilities.py:2064), so Improved Moonkin Form's aura half
    is unbuildable.
  - No range or positioning, so Nature's Reach keeps only its threat half.

DOT DURATIONS WERE CHECKED BEFORE EXTENDING THEM. Moonfire and Insect
Swarm both sit at 4 turns, so Nature's Splendor's +1 lands them at 5,
inside the 2-6 turn window measured from real fights earlier in this
session. No other node in this tree touches a duration.

UNIT CONVENTIONS: crit_chance_spell, hit_rating, haste, ability_<id>_crit
and spell_damage_taken_pct INSIDE A STATUS EFFECT are PERCENTAGE POINTS;
crit_damage_spell, dot_damage, spell_damage, spell_damage_taken_pct AS A
TALENT EFFECT, threat_multiplier and every ability_<id>_damage are
FRACTIONS; the *_from_*_pct family is a FRACTION READ AS A RAW MULTIPLIER
(character.py:1551, gained = source * pct); mp5 is FLAT; ability_<id>_
duration is FLAT TURNS and positive EXTENDS.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

NUKES = ["druid_wrath", "druid_starfire"]
MOONGLOW = ["druid_moonfire", "druid_starfire", "druid_wrath",
            "druid_healing_touch", "druid_regrowth", "druid_rejuvenation"]

T = Tree("druid_balance", "Druid Balance",
         "Sun and moon turned on the same wheel - the druid who fights with "
         "the sky instead of claws.")

# ----------------------------------------------------- tier 0 (row 0)
T.node("starlight_wrath", "Starlight Wrath",
       "Increases the damage of your Wrath and Starfire by 2% per rank.",
       0, -2, 5,
       effects={f"ability_{a}_damage": 0.02 for a in NUKES},
       source="WotLK row 0: 'Reduces the cast time of your Wrath and "
              "Starfire spells by 0.1-0.5 sec.' DEPARTURE - THERE ARE NO "
              "CAST TIMES in this engine, so the talent has no content to "
              "port. Faster casting is more damage per fight, so it becomes "
              "damage on exactly the two spells the real talent names. Same "
              "translation used for Bane in warlock_destruction, "
              "deliberately, so the pattern is legible rather than ad-hoc.")

T.node("genesis", "Genesis",
       "Increases the damage and healing of your periodic effects by 1% per "
       "rank.",
       0, 0, 5,
       effects={"dot_damage": 0.01, "healing_done": 0.01},
       source="WotLK row 0: 'Increases the damage and healing done by your "
              "periodic spell damage and healing effects by 1%-5%.' The dot "
              "half is verbatim. THE HEALING HALF IS BROADER THAN THE REAL "
              "TALENT and that is a knowing trade: the first draft used "
              "'hot_healing' to scope it to periodic healing only, and "
              "audit_talents correctly flagged it as READ BY NO ENGINE CODE. "
              "There is no hot-specific healing key - the only periodic-"
              "healing key that exists is hot_duration_pct, which is a "
              "duration, not a magnitude - so it lands on healing_done, "
              "which boosts ALL the druid's healing rather than only hots. "
              "healing_done is LIVE on the talent channel "
              "(abilities.py:1585) and is TALENT-CHANNEL ONLY: inside a "
              "proc's stat_mods it would be silent dead data, where the "
              "status channel's equivalent is healing_done_pct in POINTS "
              "(abilities.py:1680). dot_damage is a FRACTION.")

# ----------------------------------------------------- tier 1 (rows 1-2)
T.node("moonglow", "Moonglow",
       "Reduces the cost of your damage and healing spells by 3% per rank.",
       1, -6, 3,
       effects={f"ability_{a}_cost_pct": 0.03 for a in MOONGLOW},
       connected_to=["starlight_wrath"],
       source="WotLK row 1, built verbatim for the spells that exist: "
              "'Reduces the Mana cost of your Moonfire, Starfire, Starfall, "
              "Wrath, Healing Touch, Nourish, Regrowth and Rejuvenation "
              "spells by 3%/6%/9%.' Nourish does not exist, and Starfall is "
              "left off because it is not learnable until the capstone. "
              "_cost_pct is a FRACTION and POSITIVE IS A REDUCTION - the "
              "opposite sign to every other _pct key here.")

T.node("natures_majesty", "Nature's Majesty",
       "Increases the critical strike chance of your Wrath, Starfire and "
       "Healing Touch by 2% per rank.",
       1, -4, 2,
       effects={**{f"ability_{a}_crit": 2.0 for a in NUKES},
                "ability_druid_healing_touch_crit": 2.0},
       connected_to=["starlight_wrath"],
       source="WotLK row 1, built verbatim for the spells that exist: "
              "'Increases the critical strike chance of your Wrath, "
              "Starfire, Starfall, Nourish and Healing Touch spells by "
              "2%/4%.' ability_<id>_crit is PERCENTAGE POINTS while "
              "ability_<id>_crit_damage is a FRACTION - a greedy regex in "
              "probe_talent_key.py once mis-split this exact key family and "
              "falsely accused all 20 legitimate _crit_damage keys in the "
              "project.")

T.node("improved_moonfire", "Improved Moonfire",
       "Increases the damage and critical strike chance of your Moonfire by "
       "5% per rank.",
       1, -2, 2,
       effects={"ability_druid_moonfire_damage": 0.05,
                "ability_druid_moonfire_crit": 5.0},
       connected_to=["starlight_wrath"],
       source="WotLK row 1, built verbatim: 'Increases the damage and "
              "critical strike chance of your Moonfire spell by 5%/10%.' "
              "NOTE the two keys carry the SAME NUMBER in different units - "
              "0.05 is a fraction and 5.0 is points, both meaning 5%. This "
              "is the single easiest line in the file to get wrong.")

T.node("brambles", "Brambles",
       "Increases the damage of your Thorns and Entangling Roots by 25% per "
       "rank.",
       1, 0, 3,
       effects={"ability_druid_thorns_potency": 0.25,
                "ability_druid_entangling_roots_potency": 0.25},
       connected_to=["genesis"],
       source="WotLK row 2: 'Damage from your Thorns and Entangling Roots "
              "increased by 25%-75% and damage done by your Treants "
              "increased by 15%. In addition, damage from your Treants and "
              "attacks done to you while you have Barkskin active have a "
              "15% chance to daze.' Treants do not exist (no druid pet "
              "template), and the daze is unbuildable - there is no "
              "movement speed, snare or root system, and a daze is not a "
              "stun, so is_stun would be the wrong substitute.\n"
              "\n"
              "USES _potency, NOT _damage, AND THAT IS THE WHOLE POINT OF "
              "THIS NODE. The first draft authored "
              "ability_druid_thorns_damage and "
              "ability_druid_entangling_roots_damage, reading the real "
              "talent's word 'damage' literally. BOTH WOULD HAVE BEEN "
              "SILENT DEAD DATA, and nothing in the QA chain catches it: "
              "audit_talents only checks unit conventions, and probe "
              "--audit-all only checks that the ABILITY EXISTS, which both "
              "did. Neither ability has damage of its own to scale:\n"
              "  druid_thorns is effect_type 'buff' with stat_mods "
              "{'damage_dealt_pct': 3.0} - it is an ALLY BUFF that raises "
              "the target's damage, because THIS ENGINE HAS NO "
              "REFLECT-DAMAGE-ON-BEING-HIT MECHANIC AT ALL, so Thorns has "
              "always been an approximation (see its _design_note, which "
              "records it being dead twice over until 2026-10-29).\n"
              "  druid_entangling_roots is effect_type 'debuff' with "
              "stat_mods {'haste': -18, 'dodge': -12} - a pure snare with "
              "no damage component whatsoever.\n"
              "ability_<id>_potency scales an ability's own stat_mods, so "
              "it is the only key that reaches either of these. Brambles "
              "therefore makes Thorns a STRONGER DAMAGE BUFF and Roots a "
              "stronger snare. Kyle, 5 Nov, confirming this directly: 'I do "
              "want to keep thorns as a damage buff' - so Thorns stays an "
              "ally damage buff and is NOT converted to a reflect here; "
              "a real reflect remains his call and a bigger change than a "
              "talent pass.")

T.node("natures_grace", "Nature's Grace",
       "Your spell crits have a 34% chance per rank to quicken your casting "
       "for 2 turns.",
       1, 2, 3,
       proc={"trigger": "on_crit", "chance": 34, "icd": 1,
             "apply_effect": {"effect_id": "natures_grace",
                              "name": "Nature's Grace",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 20},
                              "on_target": False}},
       connected_to=["genesis"],
       source="WotLK row 2, built close to verbatim: 'All non-periodic "
              "spell criticals have a 100% chance to grace you with a "
              "blessing of nature, increasing your spell casting speed by "
              "20% for 3 sec.' KEPT AS A PROC - the real text is "
              "trigger-shaped. CHANCE IS 34, NOT THE REAL 100%: only a "
              "proc's CHANCE scales with points, never its PAYLOAD, so a "
              "3-rank node at 100% would make ranks 2 and 3 buy literally "
              "nothing. check_talent_balance.py caught exactly that in four "
              "Warlock nodes this session. 34 x 3 clamps to 100 at full "
              "rank. The 'non-periodic' clause needs no enforcing because "
              "DOTS NEVER ROLL CRIT in this engine. haste is LIVE and "
              "measured as POINTS (probe: haste=3 moved the attribute +3).")

T.node("natures_splendor", "Nature's Splendor",
       "Increases the duration of your Moonfire and Insect Swarm by 1 turn.",
       1, 4, 1,
       effects={"ability_druid_moonfire_duration": 1,
                "ability_druid_insect_swarm_duration": 1},
       connected_to=["natures_grace"],
       source="WotLK row 2, built verbatim for the spells that exist: "
              "'Increases the duration of your Moonfire and Rejuvenation by "
              "3 sec, your Regrowth by 6 sec, and your Insect Swarm and "
              "Lifebloom by 2 sec.' Lifebloom does not exist; Rejuvenation "
              "and Regrowth are left to the Restoration tree so the "
              "duration work sits in one place. DURATIONS WERE CHECKED "
              "BEFORE EXTENDING: Moonfire and Insect Swarm both sit at 4 "
              "turns, so +1 lands them at 5, inside the 2-6 turn window "
              "measured from real fights. ability_<id>_duration is FLAT "
              "TURNS and POSITIVE EXTENDS.")

T.node("natures_reach", "Nature's Reach",
       "Reduces the threat your spells generate by 15% per rank.",
       1, 6, 2,
       effects={"threat_multiplier": -0.15},
       connected_to=["natures_grace"],
       source="WotLK row 2, built for the half that works: 'Increases the "
              "range of your Balance spells and Faerie Fire by 10%/20%, and "
              "reduces the threat generated by your Balance spells by "
              "15%/30%.' THERE IS NO RANGE OR POSITIONING in this engine at "
              "all, so only the threat half survives - at its real rate. "
              "threat_multiplier is TALENT-CHANNEL ONLY and would be SILENT "
              "DEAD DATA inside a proc's stat_mods.")

# ----------------------------------------------------- tier 2 (rows 3-4)
T.node("vengeance", "Vengeance",
       "Increases the critical damage of your spells by 8% per rank.",
       2, -4, 5, effects={"crit_damage_spell": 0.08},
       connected_to=["moonglow"],
       source="WotLK row 3: 'Increases the critical strike damage bonus of "
              "your Starfire, Starfall, Moonfire and Wrath spells by "
              "20%-100%.' Scaled down hard to 40% at full rank, exactly as "
              "Ruin was in warlock_destruction: the real 100% assumes an "
              "80-level raid, and Frontier fights run 2-3 turns on trash and "
              "5-6 on a boss, so a doubled crit bonus would make one lucky "
              "Starfire the whole encounter. crit_damage_spell IS LIVE - it "
              "is read at abilities.py:1460 INSIDE A TERNARY, which is why "
              "a literal read-site probe reports nothing for it and why it "
              "was nearly declared dead.")

T.node("celestial_focus", "Celestial Focus",
       "Increases your spell haste by 1% per rank.",
       2, -2, 3, effects={"haste": 1.0},
       connected_to=["moonglow"],
       source="WotLK row 3: 'Reduces the pushback suffered from damaging "
              "attacks while casting Starfire, Hibernate and Hurricane by "
              "70% and increases your total spell haste by 3%.' The haste "
              "half is VERBATIM at 1% per rank. The pushback half has no "
              "content - no cast times means no pushback - and unlike "
              "Starlight Wrath this node does not need it, because the real "
              "talent already carries a second effect that works. haste "
              "measured LIVE as POINTS.")

T.node("lunar_guidance", "Lunar Guidance",
       "You gain spell power equal to 4% of your Intellect per rank.",
       2, 0, 3,
       effects={"spell_power_from_intellect_pct": 0.04},
       connected_to=["natures_splendor"],
       source="WotLK row 4, built verbatim: 'Increases your spell power by "
              "4%/8%/12% of your total Intellect.' CRITICAL CONVENTION: the "
              "*_from_*_pct family is a FRACTION READ AS A RAW MULTIPLIER "
              "(character.py:1551, gained = source * pct), so authoring 4 "
              "for '4%' would grant FOUR TIMES the druid's Intellect as "
              "spell power. The family is LIVE but invisible to a "
              "read-site probe by literal name - it was confirmed by "
              "MEASUREMENT on a warlock this session "
              "(spell_power_from_stamina_pct moved spell power 15 -> 21). "
              "intellect is a valid conversion SOURCE and spell_power a "
              "valid TARGET (STAT_CONVERSION_TARGETS, character.py:18).")

T.node("insect_swarm", "Insect Swarm",
       "Teaches Insect Swarm, a cloud of stinging insects.",
       2, 2, 1, node_type="active",
       effects={"unlock_ability": "druid_insect_swarm"},
       connected_to=["natures_splendor"],
       source="WotLK row 4, kept - the ONLY unlock for druid_insect_swarm, "
              "which is requires_talent. The one Balance unlock that was "
              "ALREADY at its correct tier.")

T.node("improved_insect_swarm", "Improved Insect Swarm",
       "Increases your Wrath damage by 3% per rank and your Starfire crit by "
       "3% per rank.",
       2, 4, 3,
       effects={"ability_druid_wrath_damage": 0.03,
                "ability_druid_starfire_crit": 3.0},
       connected_to=["insect_swarm"],
       source="WotLK row 4: 'Increases your damage done by your Wrath spell "
              "to targets afflicted by your Insect Swarm by 1%-3%, and "
              "increases the critical strike chance of your Starfire spell "
              "by 1%-3% on targets afflicted by your Moonfire spell.' "
              "DEPARTURE - NOTHING READS A DEBUFF ON THE TARGET, one of the "
              "hardest confirmed engine limits and the same gap that blocks "
              "Fire and Brimstone for the warlock. The real talent's entire "
              "design is that pair of conditions, so losing them is a "
              "genuine loss; both bonuses become unconditional at the real "
              "3% rather than being inflated to compensate, because the "
              "node already gains a lot by shedding its setup.")

# ----------------------------------------------------- tier 3 (row 5)
T.node("dreamstate", "Dreamstate",
       "Restores 6 mana every 5 seconds per rank.",
       3, -2, 3, effects={"mp5": 6},
       connected_to=["celestial_focus"],
       source="WotLK row 5: 'Regenerate mana equal to 4%/7%/10% of your "
              "Intellect every 5 sec, even while casting.' DEPARTURE - mp5 "
              "is FLAT and there is no mp5_from_intellect conversion "
              "(STAT_CONVERSION_TARGETS has no mana or regen target), so "
              "the Intellect scaling is lost and the value is sized against "
              "a level-60 druid's pool. mp5 measured LIVE (probe: mp5=10 "
              "moved the attribute +10). The 'even while casting' clause "
              "needs no enforcing - there are no cast times.")

T.node("moonfury", "Moonfury",
       "Increases the damage of your Starfire, Moonfire and Wrath by 3% per "
       "rank.",
       3, 0, 3,
       effects={"ability_druid_starfire_damage": 0.03,
                "ability_druid_moonfire_damage": 0.03,
                "ability_druid_wrath_damage": 0.03},
       connected_to=["lunar_guidance"],
       source="WotLK row 5, built verbatim: 'Increases the damage done by "
              "your Starfire, Moonfire and Wrath spells by 3%-10%.' Stacks "
              "with Starlight Wrath, Improved Moonfire and Wrath of "
              "Cenarius, as all four real talents do.")

T.node("balance_of_power", "Balance of Power",
       "Increases your spell hit chance by 2% per rank and reduces spell "
       "damage taken by 3% per rank.",
       3, 2, 2,
       effects={"hit_rating": 2.0, "spell_damage_taken_pct": -0.03},
       connected_to=["improved_insect_swarm"],
       source="WotLK row 5, built verbatim: 'Increases your chance to hit "
              "with all spells by 2%/4% and reduces your damage taken from "
              "all spells by 3%/6%.' TWO KEYS, TWO CONVENTIONS: hit_rating "
              "is PERCENTAGE POINTS and is NOT a valid "
              "STAT_CONVERSION_TARGET, while spell_damage_taken_pct is a "
              "FRACTION AS A TALENT EFFECT and POINTS inside a status "
              "effect - Nether Protection in warlock_destruction uses the "
              "points form of this same key.")

# ----------------------------------------------------- tier 4 (rows 6-7)
T.node("moonkin_form", "Moonkin Form",
       "Teaches Moonkin Form, the shape of the owl and the bear together.",
       4, -4, 1, node_type="active",
       effects={"unlock_ability": "druid_moonkin_form"},
       connected_to=["dreamstate"],
       source="WotLK row 6 - MOVED FROM TIER 6 TO TIER 4, which is Kyle's "
              "own flag ('The healing form can be a lvl 40 talent and the "
              "DPS form can be lvl 40 talent, think of it like Tree of Life "
              "or moonkin') and is also simply where the real tree puts it. "
              "The ONLY unlock for druid_moonkin_form, which is "
              "requires_talent - that gate was added earlier this session "
              "when all five druid forms turned out to be auto-learned, so "
              "three talent points were buying nothing at all.")

T.node("improved_moonkin_form", "Improved Moonkin Form",
       "You gain spell power equal to 10% of your Spirit per rank.",
       4, -2, 3,
       effects={"spell_power_from_spirit_pct": 0.10},
       connected_to=["moonkin_form"],
       source="WotLK row 6: 'Your Moonkin Aura also causes affected targets "
              "to gain 3% haste and you to gain 30% of your spirit as "
              "additional spell damage.' The SELF half is verbatim at 10% "
              "per rank. The aura half is unbuildable: A TALENT EFFECT CAN "
              "NEVER REACH AN ALLY - only a party-targeted ABILITY can "
              "(abilities.py:2064) - which is the same wall that cost "
              "Demonic Pact its raid identity in warlock_demonology. spirit "
              "is a valid conversion SOURCE; the RAW MULTIPLIER convention "
              "applies, so 0.10 and not 10.")

T.node("owlkin_frenzy", "Owlkin Frenzy",
       "In Moonkin Form, being struck has a 15% chance to raise your damage "
       "by 10% for 2 turns.",
       4, 0, 3,
       proc={"trigger": "on_damage_taken", "chance": 15, "icd": 1,
             "require_form": "moonkin",
             "apply_effect": {"effect_id": "owlkin_frenzy",
                              "name": "Owlkin Frenzy",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"damage_dealt_pct": 10.0},
                              "on_target": False}},
       connected_to=["moonkin_form"],
       source="WotLK row 7, built close to verbatim: 'Attacks done to you "
              "while in Moonkin form have a 5%-15% chance to cause you to "
              "go into a Frenzy, increasing your damage by 10%, cause you "
              "to be immune to pushback while casting Balance spells and "
              "restore 2% base mana every 2 sec.' USES require_form, which "
              "is a REAL proc field and is the right gate here - the real "
              "talent is explicitly Moonkin-only, and this node sits "
              "directly under the Moonkin Form unlock so the gate is always "
              "satisfiable. The pushback clause has no content (no cast "
              "times) and the mana tick is dropped to keep the node to one "
              "readable effect. CHANCE IS 15 FLAT, NOT rank-scaled, because "
              "15 x 3 would reach 45% against a real 15% ceiling; the "
              "damage_dealt_pct payload carries the full real value "
              "instead, and ranks buy the node's position in the tree. "
              "damage_dealt_pct is POINTS and is the ONLY damage key a "
              "status effect can carry.")

T.node("wrath_of_cenarius", "Wrath of Cenarius",
       "Increases the damage of your Starfire and Wrath by 2% per rank.",
       4, 2, 5,
       effects={f"ability_{a}_damage": 0.02 for a in NUKES},
       connected_to=["balance_of_power"],
       source="WotLK row 7: 'Your Starfire spell gains an additional "
              "4%-20% and your Wrath gains an additional 2%-10% of your "
              "bonus damage effects.' Spell-power coefficients are not "
              "exposed to talents, so it becomes direct damage. The real "
              "talent's asymmetry (Starfire twice Wrath) is flattened "
              "because the two spells are not differentiated enough here "
              "for it to read as anything but a number. Improved Faerie "
              "Fire, the other row-6 talent, is DROPPED - no Faerie Fire "
              "ability exists.")

# ----------------------------------------------------- tier 5 (rows 8-9)
T.node("eclipse", "Eclipse",
       "Your Starfire crits raise your damage by 5% per rank for 3 turns.",
       5, -4, 3,
       proc={"trigger": "on_crit", "chance": 34, "icd": 1,
             "ability_filter": ["druid_starfire"],
             "apply_effect": {"effect_id": "eclipse", "name": "Eclipse",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"damage_dealt_pct": 15.0},
                              "on_target": False}},
       connected_to=["owlkin_frenzy"],
       source="WotLK row 8: 'When you critically hit with Starfire, you "
              "have a 100% chance of increasing damage done by Wrath by "
              "40%. When you critically hit with Wrath, you have a 60% "
              "chance of increasing your critical strike chance with "
              "Starfire by 40%.' DEPARTURE on the ABILITY SCOPING: a status "
              "effect cannot carry an ability-scoped key - "
              "ability_<id>_damage is TALENT-CHANNEL ONLY and would be "
              "silent dead data inside a proc - so the Wrath-specific "
              "buff becomes general damage. Only the Starfire half is "
              "built; both halves would be two procs doing the same thing "
              "once the ability scoping is gone. CHANCE IS 34 x 3, not the "
              "real 100%, for the multi-rank reason given on Nature's "
              "Grace.")

T.node("typhoon", "Typhoon",
       "Teaches Typhoon, a blast of wind that throws enemies back.",
       5, -2, 1, node_type="active",
       effects={"unlock_ability": "druid_typhoon"},
       connected_to=["eclipse"],
       source="WotLK row 8 - MOVED FROM TIER 6 to its real tier 5. The ONLY "
              "unlock for druid_typhoon, which is requires_talent.")

T.node("gale_winds", "Gale Winds",
       "Increases the damage of your Typhoon by 15% per rank.",
       5, 0, 2,
       effects={"ability_druid_typhoon_damage": 0.15},
       connected_to=["typhoon"],
       source="WotLK row 8, built verbatim for the one spell we have: "
              "'Increases damage done by your Hurricane and Typhoon spells "
              "by 15%/30%, and increases the range of your Cyclone spell by "
              "4 yards.' Hurricane and Cyclone do not exist, and there is "
              "no range. Force of Nature, the other row-8 talent, is "
              "DROPPED: it summons treants, there is no druid pet template, "
              "and PETS NEVER FIRE PROCS even if there were.")

T.node("earth_and_moon", "Earth and Moon",
       "Increases your spell damage by 2% per rank, and your Wrath and "
       "Starfire leave the target taking 13% more spell damage.",
       5, 2, 3,
       effects={"spell_damage": 0.02},
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
             "ability_filter": NUKES,
             "apply_effect": {"effect_id": "earth_and_moon",
                              "name": "Earth and Moon",
                              "effect_type": "debuff", "duration": 3,
                              "stat_mods": {"spell_damage_taken_pct": 13.0}}},
       connected_to=["wrath_of_cenarius"],
       source="WotLK row 9, BOTH HALVES BUILT, which is rare in this tree: "
              "'Your Wrath and Starfire spells have a 100% chance to apply "
              "the Earth and Moon effect, increasing spell damage taken by "
              "13% for 12 sec. Also increases your spell damage by 2%-6%.' "
              "The chance is a real 100% AND the node has a scaling "
              "effects dict alongside the proc, so ranks 2 and 3 still buy "
              "something - this is the one case where a 100% multi-rank "
              "proc is legitimate, and check_talent_balance.py accepts it "
              "for exactly that reason. CRITICAL: spell_damage_taken_pct is "
              "POINTS INSIDE A STATUS EFFECT (13.0) and a FRACTION as a "
              "talent effect - Balance of Power three tiers down uses the "
              "fraction form of this same key, so the two conventions sit "
              "in one file deliberately. It is also one of only EIGHT "
              "stat_mods a MONSTER can read, so the debuff really lands. "
              "12 sec is 3 turns.")

# ----------------------------------------------------- tier 6 (row 10)
T.node("starfall", "Starfall",
       "Teaches Starfall, calling the stars down on everything nearby.",
       6, 0, 1, node_type="active",
       effects={"unlock_ability": "druid_starfall"},
       connected_to=["earth_and_moon"],
       source="WotLK row 10, the capstone - MOVED FROM TIER 3, which was "
              "the worst placement in the tree: Balance's capstone ability "
              "was buyable a third of the way up it. The ONLY unlock for "
              "druid_starfall, which is requires_talent.")


def main():
    return T.write(was="23 nodes, 69 points - unlocks at tiers 2/3/6/6")


if __name__ == "__main__":
    sys.exit(main())
