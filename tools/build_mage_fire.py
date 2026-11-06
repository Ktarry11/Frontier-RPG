#!/usr/bin/env python3
"""Rebuild Mage Fire from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_mage_fire.py

SOURCE: data/reference/wotlk/mage.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/mage.md.

ROLE: burn. Crits that set the target on fire, and a tree built entirely
around making crits happen and then compound.

IGNITE IS THE TREE'S ENGINE and it is buildable almost exactly: "your
critical strikes from Fire damage spells cause the target to burn" is
on_crit applying a dot, which this engine does natively. That one talent
does more for Fire's identity than any amount of flat crit, so it is
built first and the rest of the tree feeds it.

HOT STREAK CANNOT BE BUILT, and it is worth naming because it is Fire's
signature in WotLK: "any time you score 2 non-periodic spell criticals IN A
ROW" needs a memory of the previous cast's outcome, and nothing in this
engine remembers anything between casts - no cast counter, no streak, no
accumulator. It becomes a single-crit proc instead.

ABILITIES THE REAL TREE WANTS AND WE LACK: Scorch, Flamestrike, Dragon's
Breath, Frostfire Bolt, Fire Ward, Frost Ward, Living Bomb. Improved
Scorch, Molten Shields and Firestarter are DROPPED. Living Bomb's capstone
role goes to living_flame, which is the kit's real burn spell.

UNIT CONVENTIONS: crit_chance_spell is PERCENTAGE POINTS; fire_spell_damage
/ spell_damage / spell_damage_taken_pct / crit_damage_spell /
low_health_damage_pct / low_health_damage_reduction_pct are FRACTIONS;
fire_spell_damage is built by f-string (abilities.py:1371) so grep cannot
see it and it is LIVE.

KEPT MANDATORY: Pyroblast, Blast Wave and Combustion are the only unlocks
for their abilities, all three requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("mage_fire", "Mage Fire",
         "Fire and ruin - critical strikes that leave the target burning.")

# ----------------------------------------------------------------- tier 0
T.node("improved_fire_blast", "Improved Fire Blast",
       "Reduces the cooldown of your Fire Blast by 1 turn per rank.",
       0, -2, 2,
       effects={"ability_mage_fire_blast_cooldown": 1},
       source="WotLK row 0: 'Reduces the cooldown of your Fire Blast spell "
              "by 0.5/1 sec.' Built verbatim as cooldown. "
              "ability_<id>_cooldown is FLAT turns and talented_cooldown "
              "clamps at 1, so it cannot reach zero.")

T.node("incineration", "Incineration",
       "Increases the critical chance of your Fire Blast and Cone of Cold "
       "by 2% per rank.",
       0, 0, 3,
       effects={"ability_mage_fire_blast_crit": 2.0,
                "ability_mage_cone_of_cold_crit": 2.0},
       source="WotLK row 0: 'Increases the critical strike chance of your "
              "Fire Blast, Scorch, Arcane Blast and Cone of Cold spells by "
              "2%/4%/6%.' Built verbatim for the two that exist. "
              "ability_<id>_crit is PERCENTAGE POINTS.")

T.node("improved_fireball", "Improved Fireball",
       "Increases the damage of your Fireball by 3% per rank.",
       0, 2, 5,
       effects={"ability_mage_fireball_damage": 0.03},
       source="WotLK row 0: 'Reduces the casting time of your Fireball "
              "spell by 0.1-0.5 sec.' DEPARTURE - no cast times. A shorter "
              "cast is more throughput, so it is delivered as damage.")

# ----------------------------------------------------------------- tier 1
T.node("ignite", "Ignite",
       "Your critical strikes set the target burning for 3 turns.",
       1, -6, 5,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "apply_effect": {"effect_id": "ignite", "name": "Ignite",
                              "effect_type": "dot", "duration": 3,
                              "potency": 50, "damage_school": "fire"}},
       connected_to=["improved_fire_blast"],
       source="WotLK row 1: 'Your critical strikes from Fire damage spells "
              "cause the target to burn for an additional 8%-40% of your "
              "spell's damage over 4 sec.' THE TREE'S ENGINE, and almost "
              "exactly buildable: on_crit applying a dot is native here. "
              "Percentage-of-the-triggering-damage is not available to a "
              "dot payload - potency is a FLAT PER-TURN number, where an "
              "ABILITY rank's effect_value is the TOTAL and gets divided - "
              "so 50 a turn over 3 turns stands in. Ranked by chance, since "
              "a proc's payload does not scale with points.")

T.node("impact", "Impact",
       "Your damaging spells have a 3% chance per rank to stun the target.",
       1, -4, 3,
       proc={"trigger": "on_damage_cast", "chance": 3, "icd": 2,
             "apply_effect": {"effect_id": "impact", "name": "Impact",
                              "effect_type": "debuff", "duration": 2,
                              "is_stun": True}},
       connected_to=["improved_fire_blast"],
       source="WotLK row 1: 'Gives your damaging spells a 3%/7%/10% chance "
              "to cause the next Fire Blast you cast to stun the target for "
              "2 sec.' Built with the real chance curve and a real stun - "
              "is_stun is this engine's only incapacitate. DEPARTURE on the "
              "delivery: 'the next Fire Blast you cast' needs a buff that "
              "is consumed on use, which does not exist, so the stun lands "
              "directly. icd 2 keeps it from being permanent control.")

T.node("world_in_flames", "World in Flames",
       "Increases the critical chance of your Pyroblast, Blast Wave and "
       "Living Flame by 2% per rank.",
       1, -2, 3,
       effects={"ability_mage_pyroblast_crit": 2.0,
                "ability_mage_blast_wave_crit": 2.0,
                "ability_mage_living_flame_crit": 2.0},
       connected_to=["incineration"],
       source="WotLK row 1, built verbatim for the three real spells that "
              "exist: 'Increases the critical strike chance of your "
              "Flamestrike, Pyroblast, Blast Wave, Dragon's Breath and "
              "Living Bomb spells by 2%/4%/6%.' Living Flame is this kit's "
              "Living Bomb. Feeds Ignite, which is the point.")

T.node("pyroblast", "Pyroblast",
       "Teaches Pyroblast, hurling an immense fiery boulder.",
       1, 0, 1, node_type="active",
       effects={"unlock_ability": "mage_pyroblast"},
       connected_to=["incineration"],
       source="WotLK row 1, kept - the ONLY unlock for mage_pyroblast, "
              "which is requires_talent. It is Blast Wave's prerequisite in "
              "the real tree, preserved below.")

T.node("burning_soul", "Burning Soul",
       "Reduces the threat your spells generate by 10% per rank.",
       1, 2, 2, effects={"threat_generation_pct": -0.10},
       connected_to=["improved_fireball"],
       source="WotLK row 1: 'Reduces the pushback suffered from damaging "
              "attacks while casting Fire spells by 35%/70% and reduces the "
              "threat caused by your Fire spells by 5%/10%.' The threat "
              "half is built - there is no per-school threat key, only the "
              "global threat_generation_pct, which is a FRACTION. No cast "
              "times means no pushback.")

T.node("burning_determination", "Burning Determination",
       "Reduces the duration of Stun effects against you by 15% per rank.",
       1, 4, 2,
       effects={"stun_duration_reduction_pct": 0.15},
       connected_to=["improved_fireball"],
       source="WotLK row 1, NEW to our tree: 'When Interrupted or Silenced "
              "you have a 50%/100% chance to become immune to the next "
              "Interrupt or Silence effect for 10 sec.' DEPARTURE - there "
              "is no interrupt and no silence; is_stun is this engine's "
              "only incapacitate, so the resistance applies to that. "
              "stun_duration_reduction_pct is a FRACTION and floors a stun "
              "at 1 turn.")

# ----------------------------------------------------------------- tier 2
T.node("playing_with_fire", "Playing with Fire",
       "Increases all your spell damage by 1% per rank, and all spell damage "
       "you take by 1% per rank.",
       2, -4, 3,
       effects={"spell_damage": 0.01, "spell_damage_taken_pct": 0.01},
       connected_to=["ignite"],
       source="WotLK row 2, built verbatim with BOTH halves including the "
              "drawback: 'Increases all spell damage caused by 1%/2%/3% and "
              "all spell damage taken by 1%/2%/3%.' The downside is kept "
              "because it is what makes the talent a choice. "
              "spell_damage_taken_pct is a FRACTION as a talent effect and "
              "POSITIVE INCREASES damage taken.")

T.node("critical_mass", "Critical Mass",
       "Increases your spell critical chance by 2% per rank.",
       2, -2, 3, effects={"crit_chance_spell": 2.0},
       connected_to=["world_in_flames"],
       source="WotLK row 2: 'Increases the critical strike chance of your "
              "Fire spells by 2%/4%/6%.' crit_chance_spell covers all "
              "spells rather than one school - there is no per-school crit "
              "key - and every spell this tree cares about is Fire anyway. "
              "It is Combustion's prerequisite, preserved below.")

T.node("blast_wave", "Blast Wave",
       "Teaches Blast Wave, a ring of flame radiating outward.",
       2, 0, 1, node_type="active",
       effects={"unlock_ability": "mage_blast_wave"},
       connected_to=["pyroblast"],
       source="WotLK row 2, kept - the ONLY unlock for mage_blast_wave, "
              "which is requires_talent. The real talent requires "
              "Pyroblast, which connected_to reproduces.")

T.node("master_of_elements", "Master of Elements",
       "Your spell criticals refund 120 mana.",
       2, 2, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 120}},
       connected_to=["burning_soul"],
       source="WotLK row 2, NEW to our tree: 'Your spell criticals will "
              "refund 10%/20%/30% of their base mana cost.' Built on the "
              "real trigger. A refund proportional to the spell's cost is "
              "not available - grant_resource takes a FLAT amount with no "
              "pct_max - so 120 stands in, with the chance carrying the "
              "rank curve.")

# ----------------------------------------------------------------- tier 3
T.node("blazing_speed", "Blazing Speed",
       "Being struck has a 10% chance per rank to quicken you by 20% for 2 "
       "turns.",
       3, -2, 2,
       proc={"trigger": "on_damage_taken", "chance": 10, "icd": 1,
             "apply_effect": {"effect_id": "blazing_speed",
                              "name": "Blazing Speed",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 20},
                              "on_target": False}},
       connected_to=["playing_with_fire"],
       source="WotLK row 3, NEW to our tree: 'Gives you a 5%/10% chance "
              "when hit by a melee or ranged attack to increase your "
              "movement speed by 50% and dispel all movement impairing "
              "effects.' DEPARTURE - there is no movement speed and no "
              "movement impairment. Moving faster becomes acting faster. "
              "haste inside status stat_mods is PERCENTAGE POINTS.")

T.node("fire_power", "Fire Power",
       "Increases your Fire spell damage by 2% per rank.",
       3, 0, 5, effects={"fire_spell_damage": 0.02},
       connected_to=["critical_mass"],
       source="WotLK row 3, built verbatim: 'Increases the damage done by "
              "your Fire spells by 2%-10%.' USES THE PER-SCHOOL KEY "
              "DELIBERATELY. fire_spell_damage is built as "
              "f'{school}_spell_damage' at abilities.py:1371, so a literal "
              "grep cannot see it - the family that caused "
              "arcane_spell_damage to be WRONGLY declared dead in this "
              "project. It is LIVE and it is the right key here.")

# ----------------------------------------------------------------- tier 4
T.node("pyromaniac", "Pyromaniac",
       "Increases your spell critical chance by 1% per rank and restores 5 "
       "mana every 5 seconds per rank.",
       4, -4, 3,
       effects={"crit_chance_spell": 1.0, "mp5": 5},
       connected_to=["blazing_speed"],
       source="WotLK row 4, built with both halves: 'Increases chance to "
              "critically hit by 1%/2%/3% and allows 17%/33%/50% of your "
              "mana regeneration to continue while casting.' There are no "
              "cast times, so the regeneration clause becomes flat mp5, "
              "which is FLAT and lands on the attribute.")

T.node("fiery_payback", "Fiery Payback",
       "While below half health, reduces all damage you take by 10% per "
       "rank.",
       4, -2, 2,
       effects={"low_health_damage_reduction_pct": 0.10},
       connected_to=["critical_mass"],
       source="WotLK row 4, NEW to our tree: 'When below 35% health all "
              "damage taken is reduced by 10%/20% and your Pyroblast "
              "spell's cast time is reduced.' The mitigation half is built "
              "as a REAL conditional: low_health_damage_reduction_pct reads "
              "the ACTOR's own health and defaults to a 50% threshold, so "
              "low_health_threshold_pct is NOT authored - it SUMS across "
              "talents. No cast times for the second half.")

T.node("combustion", "Combustion",
       "Teaches Combustion, stoking your criticals into an inferno.",
       4, 0, 1, node_type="active",
       effects={"unlock_ability": "mage_combustion"},
       connected_to=["critical_mass"],
       source="WotLK row 4, kept - the ONLY unlock for mage_combustion, "
              "which is requires_talent. The real talent requires Critical "
              "Mass, which connected_to reproduces.")

T.node("molten_fury", "Molten Fury",
       "Increases your damage by 6% per rank against targets below 35% "
       "health.",
       4, 2, 2, effects={"low_health_damage_pct": 0.06},
       connected_to=["master_of_elements"],
       source="WotLK row 4, NEW to our tree, built almost verbatim: "
              "'Increases damage of all spells against targets with less "
              "than 35% health by 6%/12%.' A REAL conditional - "
              "low_health_damage_pct reads the TARGET's health and defaults "
              "to exactly the 35% threshold the real talent names, which is "
              "why low_health_threshold_pct is NOT authored.")

T.node("empowered_fire", "Empowered Fire",
       "Increases the damage of your Fireball and Pyroblast by 3% per rank.",
       4, 4, 3,
       effects={"ability_mage_fireball_damage": 0.03,
                "ability_mage_pyroblast_damage": 0.03},
       connected_to=["master_of_elements"],
       source="WotLK row 4: 'Increases the damage of your Fireball, "
              "Frostfire Bolt and Pyroblast spells by an amount equal to "
              "5%/10%/15% of your spell power.' Spell-power coefficients "
              "are not exposed to talents, so it is direct damage. "
              "Frostfire Bolt does not exist.")

# ----------------------------------------------------------------- tier 5
T.node("burnout", "Burnout",
       "Increases the critical damage of your spells by 10% per rank.",
       5, -2, 5, effects={"crit_damage_spell": 0.10},
       connected_to=["pyromaniac"],
       source="WotLK row 5: 'Increases your spell critical damage bonus "
              "with all spells by 10%-50% but your non-periodic spell "
              "criticals cost 1% more mana.' The crit-damage half is built "
              "verbatim; the mana drawback has no per-crit cost mechanism. "
              "crit_damage_spell is a FRACTION, read at abilities.py:1460 "
              "inside a ternary - live despite the probe finding no literal "
              "read site, and DEAD inside a status effect, so the "
              "talent-effect form used here is the only one that works.")

T.node("hot_streak", "Hot Streak",
       "Your critical strikes have a 33% chance per rank to make your next "
       "spells hit 30% harder for 2 turns.",
       5, 0, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "hot_streak",
                              "name": "Hot Streak",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"damage_dealt_pct": 30.0},
                              "on_target": False}},
       connected_to=["combustion"],
       source="WotLK row 5: 'Any time you score 2 non-periodic spell "
              "criticals IN A ROW using Fireball, Fire Blast, Scorch, "
              "Living Bomb or Frostfire Bolt, you have a 33%-100% chance "
              "your next Pyroblast spell is instant cast.' DEPARTURE, and "
              "the biggest one in the Mage: nothing in this engine "
              "remembers the previous cast's outcome - there is no cast "
              "counter, no streak and no accumulator - so 'two criticals in "
              "a row' cannot be detected. It fires on a single crit "
              "instead, and since there are no cast times either, the "
              "payoff is damage rather than an instant Pyroblast. NOTE the "
              "stat_mod is damage_dealt_pct in PERCENTAGE POINTS: "
              "spell_damage would be SILENT DEAD DATA here, read through "
              "the talent channel while a status effect's stat_mods go to "
              "get_status_stat_mod.")

# ----------------------------------------------------------------- tier 6
T.node("living_bomb", "Living Bomb",
       "Increases the damage of your Living Flame by 40%.",
       6, 0, 1,
       effects={"ability_mage_living_flame_damage": 0.40},
       connected_to=["hot_streak"],
       source="WotLK row 10, the capstone: 'The target becomes a Living "
              "Bomb, taking 612 Fire damage over 12 sec. After 12 sec or "
              "when the spell is dispelled, the target explodes.' "
              "DEPARTURE - there is no mage_living_bomb ability to unlock, "
              "and no trigger on an effect EXPIRING for the explosion. "
              "mage_living_flame is this kit's equivalent burn spell, so "
              "the capstone makes it hit considerably harder. The "
              "delayed-explosion mechanic is the single most distinctive "
              "thing lost in the Mage rebuild and is recorded as such.")


def main():
    return T.write(was="23 nodes, 71 points - 12 proc, 11 with no proc and "
                       "no unlock")


if __name__ == "__main__":
    sys.exit(main())
