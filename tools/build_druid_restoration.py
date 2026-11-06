#!/usr/bin/env python3
"""Rebuild Druid Restoration from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_druid_restoration.py

SOURCE: data/reference/wotlk/druid.json (from Spell.dbc) - the real 27
talents and 80 points, every row read from the reference and every
ambiguous talent's RANK TEXT read before authoring.

THIS TREE WAS UNDER A NO-TOUCH RULE ALL SESSION. Kyle retired it on 5 Nov
("Rebuild all three").

ROLE: the healer. Rejuvenation and Regrowth rolling, Swiftmend to catch a
spike, Tree of Life as the throughput cooldown.

SPIRIT IS THE TREE'S STAT. Kyle, 5 Nov: "resto druid does really well
with spirit gear" and "i play resto druid as my main and i love spirit".
So Spirit is built as the scaling stat rather than Intellect: Living
Spirit raises it, Improved Tree of Life converts it into healing power,
and the mana talents feed off it. That is a design instruction and it
decided several keys below that would otherwise have gone to Intellect.

MEASURED ON A LIVE LEVEL-60 DRUID BEFORE AUTHORING (the probe reports
most of these as "no read site found" because they are read off the
`bonuses` pool, not by literal name):

    spirit_pct = 20                  -> healing power 23 -> 25   POINTS
    healing_power_from_spirit_pct=0.5 -> healing power 23 -> 50
                                        RAW MULTIPLIER (gained = src*pct)
    max_mana_pct = 0.20              -> mana 1285 -> 1542      FRACTION
       (authoring 20 for "20%" gives mana 1285 -> 26985 - a 21x pool)
    haste = 5                        -> haste 9 -> 14            POINTS
    mp5 = 5                          -> +5                        FLAT

HEALS NEVER ROLL CRIT IN THIS ENGINE, and that shapes two talents.
_roll_crit is called only from the four DAMAGE branches
(abilities.py:2597/2656/2748/2799) and nowhere in the healing path. The
outgoing tree had THREE DEAD KEYS from exactly this -
ability_druid_regrowth_crit, ability_druid_healing_touch_crit and
ability_druid_swiftmend_crit, all found by
tools/qa_ability_scoped_fields.py - so Nature's Bounty and Improved
Regrowth are rebuilt on _healing instead, and Living Seed cannot use an
on_crit trigger at all.

THE UNLOCK ROWS WERE ALL WRONG. Restoration owns four talent-gated
abilities and every one sat at the wrong tier:

    druid_natures_swiftness  was tier 6, real row 4  -> tier 2
    druid_swiftmend          was tier 2, real row 6  -> tier 4
    druid_tree_of_life       was tier 3, real row 8  -> tier 5
    druid_wild_growth        was tier 4, real row 10 -> tier 6  (CAPSTONE)

DROPPED, 2 points of the real 80: Improved Tranquility (no Tranquility
ability exists). 78 points remain against the 56 a pure spec must spend.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

SHIFTS = ["druid_bear_form", "druid_cat_form", "druid_moonkin_form",
          "druid_tree_of_life", "druid_dire_bear_form"]
DIRECT_HEALS = ["druid_healing_touch", "druid_regrowth", "druid_swiftmend"]

T = Tree("druid_restoration", "Druid Restoration",
         "Life given back - the slow green work of keeping everyone "
         "standing.")

# ----------------------------------------------------- tier 0 (row 0)
T.node("improved_mark_of_the_wild", "Improved Mark of the Wild",
       "Increases the effect of your Mark of the Wild by 10% per rank.",
       0, -2, 2,
       effects={"ability_druid_mark_of_the_wild_potency": 0.10},
       source="WotLK row 0, built verbatim: 'Increases the effect of your "
              "Mark of the Wild by 10%/20%.' USES _potency because "
              "druid_mark_of_the_wild is effect_type 'buff' whose entire "
              "content is its stat_mods - _healing or _damage here would be "
              "SILENT DEAD DATA, the exact bug that killed Brambles in "
              "druid_balance and 99 keys across the project "
              "(tools/qa_ability_scoped_fields.py).")

T.node("natures_focus", "Nature's Focus",
       "Reduces the cost of your Healing Touch and Regrowth by 4% per rank.",
       0, 0, 3,
       effects={"ability_druid_healing_touch_cost_pct": 0.04,
                "ability_druid_regrowth_cost_pct": 0.04},
       source="WotLK row 0: 'Reduces the pushback suffered from damaging "
              "attacks while casting your Healing Touch, Regrowth, "
              "Nourish, Tranquility and Cyclone spells by 70%.' DEPARTURE - "
              "no cast times means NO PUSHBACK to reduce. Being able to "
              "keep casting under fire becomes being able to afford it, the "
              "same translation used for Fel Concentration and Intensity in "
              "the Warlock trees, deliberately, so the pattern is legible "
              "rather than ad-hoc. _cost_pct is a FRACTION and POSITIVE IS "
              "A REDUCTION.")

T.node("furor", "Furor",
       "Increases your maximum mana by 2% per rank.",
       0, 2, 5, effects={"max_mana_pct": 0.02},
       source="WotLK row 0: 'Gives you 20%-100% chance to gain 10 Rage when "
              "you shapeshift into Bear Form, or 40 Energy when you "
              "shapeshift into Cat Form, and increases your maximum mana by "
              "2%-10%.' SHAPESHIFTING IS NOT A PROC TRIGGER - the twelve "
              "triggers are all cast/damage/heal/avoid events and none "
              "fires on a form change - so the resource half cannot be "
              "built. The mana half is VERBATIM. CRITICAL: max_mana_pct is "
              "a FRACTION, measured - 0.20 moved mana 1285 -> 1542, while "
              "authoring 20 for '20%' moved it to 26985, a 21x pool. It is "
              "the opposite convention to stamina_pct and spirit_pct, which "
              "are POINTS.")

# ----------------------------------------------------- tier 1 (rows 1-2)
T.node("naturalist", "Naturalist",
       "Increases your physical damage by 2% per rank.",
       1, -6, 5, effects={"physical_damage": 0.02},
       connected_to=["improved_mark_of_the_wild"],
       source="WotLK row 1: 'Reduces the cast time of your Healing Touch by "
              "0.1-0.5 sec and increases the damage you deal with physical "
              "attacks by 2%-10%.' No cast times, so only the damage half "
              "survives - at its real value. physical_damage is LIVE on the "
              "talent bus with 4 read sites.")

T.node("subtlety", "Subtlety",
       "Reduces the threat your healing generates by 7% per rank.",
       1, -4, 3, effects={"threat_multiplier": -0.07},
       connected_to=["improved_mark_of_the_wild"],
       source="WotLK row 1, built verbatim: 'Reduces the threat generated "
              "by your healing spells by 7%-20%.' threat_multiplier is "
              "TALENT-CHANNEL ONLY and would be SILENT DEAD DATA inside a "
              "proc's stat_mods - and it is a FRACTION there, while the "
              "status channel's threat_generation_pct is POINTS. "
              "audit_talents caught that exact mix-up in Shadowstep this "
              "session.")

T.node("natural_shapeshifter", "Natural Shapeshifter",
       "Reduces the cost of your shapeshifting by 10% per rank.",
       1, -2, 3,
       effects={f"ability_{a}_cost_pct": 0.10 for a in SHIFTS},
       connected_to=["natures_focus"],
       source="WotLK row 1, built verbatim: 'Reduces the mana cost of all "
              "shapeshifting by 10%/20%/30%.' ALL FIVE FORMS CARRY A REAL "
              "COST (bear 20, cat 25, moonkin 30, tree 35, dire bear 30), "
              "which was CHECKED rather than assumed - the Warlock's Master "
              "Summoner node was authored the same way and ALL FOUR of its "
              "keys were dead because summons are free.")

T.node("intensity", "Intensity",
       "Restores 5 mana every 5 seconds per rank.",
       1, 0, 3, effects={"mp5": 5},
       connected_to=["natures_focus"],
       source="WotLK row 2: 'Allows 17%-50% of your Mana regeneration to "
              "continue while casting.' DEPARTURE - there is no "
              "casting/not-casting distinction without cast times, so "
              "regen-while-casting becomes plain regen. mp5 is FLAT and "
              "measured LIVE (mp5=5 moved the attribute +5); there is no "
              "mp5-from-Spirit conversion, because STAT_CONVERSION_TARGETS "
              "has no mana or regen target at all.")

T.node("omen_of_clarity", "Omen of Clarity",
       "Your heals sometimes cost you nothing at all.",
       1, 2, 1,
       proc={"trigger": "on_heal_cast", "chance": 15, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 70}},
       connected_to=["natures_focus"],
       source="WotLK row 2: 'Your damage and healing spells have a chance "
              "to cause your next damage or healing spell to be cast "
              "without consuming mana.' DEPARTURE - THERE IS NO "
              "NEXT-CAST-MODIFIER MECHANIC (no cast counter, no streak, no "
              "accumulator of any kind), so a free next cast is not "
              "expressible. Refunding the mana directly is the same outcome "
              "by a route the engine has. grant_resource takes a FLAT "
              "amount - there is no pct_max - and 70 is roughly one "
              "Regrowth, so it reads as 'that one was free'. Druid resource "
              "confirmed MANA before authoring, per the standing "
              "check-the-resource-first rule.")

T.node("master_shapeshifter", "Master Shapeshifter",
       "In Tree of Life form, increases your healing by 2% per rank.",
       1, 4, 2,
       effects={"healing_done": 0.02},
       require_form="tree_of_life",
       connected_to=["omen_of_clarity"],
       source="WotLK row 2: 'Grants an effect which lasts while you are "
              "within the respective shapeshift form - Bear: 4% physical "
              "damage, Cat: 4% crit, Moonkin: 4% spell damage, Tree of "
              "Life: 4% healing.' ONLY THE TREE BRANCH IS BUILT, because "
              "require_form gates the WHOLE NODE and there is no way to "
              "give one node four different payloads by form. Tree is the "
              "right branch for the Restoration tree, and the node sits "
              "below the Tree of Life unlock's own branch. healing_done is "
              "TALENT-CHANNEL ONLY (abilities.py:1585); the status "
              "channel's equivalent is healing_done_pct in POINTS.")

# ----------------------------------------------------- tier 2 (rows 3-4)
T.node("tranquil_spirit", "Tranquil Spirit",
       "Reduces the cost of your Healing Touch by 2% per rank.",
       2, -4, 5,
       effects={"ability_druid_healing_touch_cost_pct": 0.02},
       connected_to=["naturalist"],
       source="WotLK row 3, built verbatim for the spell we have: 'Reduces "
              "the mana cost of your Healing Touch, Nourish and Tranquility "
              "spells by 2%-10%.' Nourish and Tranquility do not exist. "
              "Stacks with Nature's Focus, as the real pair does.")

T.node("improved_rejuvenation", "Improved Rejuvenation",
       "Increases the healing of your Rejuvenation by 5% per rank.",
       2, -2, 3,
       effects={"ability_druid_rejuvenation_healing": 0.05},
       connected_to=["subtlety"],
       source="WotLK row 3, built verbatim: 'Increases the effect of your "
              "Rejuvenation spell by 5%/10%/15%.' USES _healing: "
              "druid_rejuvenation is effect_type 'hot', so _healing is read "
              "(abilities.py:1584, inside the school == 'healing' branch). "
              "NOT _potency - the outgoing tree's Gift of the Earthmother "
              "used ability_druid_rejuvenation_potency and it was DEAD, "
              "because rejuvenation carries no stat_mods for potency to "
              "scale.")

T.node("natures_swiftness", "Nature's Swiftness",
       "Teaches Nature's Swiftness, one heal that will not wait.",
       2, 0, 1, node_type="active",
       effects={"unlock_ability": "druid_natures_swiftness"},
       connected_to=["intensity"],
       source="WotLK row 4 - MOVED FROM TIER 6 to its real tier 2. The ONLY "
              "unlock for druid_natures_swiftness, which is "
              "requires_talent.")

T.node("gift_of_nature", "Gift of Nature",
       "Increases all your healing by 2% per rank.",
       2, 2, 5, effects={"healing_done": 0.02},
       connected_to=["intensity"],
       source="WotLK row 4, built verbatim: 'Increases the effect of all "
              "healing spells by 2%-10%.' The tree's backbone throughput "
              "talent. Improved Tranquility, the other row-4 talent, is "
              "DROPPED - no Tranquility ability exists.")

T.node("empowered_touch", "Empowered Touch",
       "Increases the healing of your Healing Touch by 10% per rank.",
       2, 4, 2,
       effects={"ability_druid_healing_touch_healing": 0.10},
       connected_to=["gift_of_nature"],
       source="WotLK row 5: 'Your Healing Touch and Nourish spells gain an "
              "additional 20%/40% of your bonus healing effects.' "
              "Spell-power coefficients are not exposed to talents, so it "
              "becomes direct healing. druid_healing_touch is effect_type "
              "'heal', so _healing lands - and NOT _crit, which the "
              "outgoing tree used on this very ability and which was dead, "
              "because HEALS NEVER ROLL CRIT in this engine.")

# ----------------------------------------------------- tier 3 (row 5)
T.node("natures_bounty", "Nature's Bounty",
       "Increases the critical strike chance of your Regrowth, Healing Touch "
       "and Swiftmend by 5% per rank.",
       3, -2, 5,
       effects={f"ability_{a}_crit": 5.0 for a in DIRECT_HEALS},
       connected_to=["improved_rejuvenation"],
       source="WotLK row 5: 'Increases the critical strike chance of your "
              "Regrowth, Healing Touch, Nourish and Swiftmend spells by "
              "5%-25%.' BUILT VERBATIM, and it only became buildable "
              "TODAY. Until 5 Nov 2026 heals never rolled crit in this "
              "engine - _roll_crit was called from the four DAMAGE "
              "branches and nowhere in the healing path - so the outgoing "
              "tree's ability_druid_healing_touch_crit and "
              "ability_druid_swiftmend_crit were SILENT DEAD DATA, found "
              "by tools/qa_ability_scoped_fields.py. An interim version of "
              "this node was rebuilt on _healing to work around it. Then "
              "Kyle said 'spells should be able to crit!' and healing crits "
              "were added to combat/abilities.py, so the real talent is "
              "now authorable as written and the workaround is reverted. "
              "ability_<id>_crit is PERCENTAGE POINTS and feeds "
              "crit_chance_spell, which is the stat the new healing crit "
              "roll reads. Nourish does not exist.")

T.node("living_spirit", "Living Spirit",
       "Increases your total Spirit by 5% per rank.",
       3, 0, 3, effects={"spirit_pct": 5.0},
       connected_to=["gift_of_nature"],
       source="WotLK row 6, built verbatim: 'Increases your total Spirit by "
              "5%/10%/15%.' THE TREE'S KEYSTONE STAT TALENT, and it is "
              "built on Spirit on purpose - Kyle, 5 Nov: 'resto druid does "
              "really well with spirit gear' and 'i love spirit'. "
              "spirit_pct is PERCENTAGE POINTS (read off `bonuses` at "
              "character.py:1263 and divided by 100), which is why a "
              "literal read-site probe finds nothing and the key is "
              "nonetheless LIVE - measured: spirit_pct=20 moved healing "
              "power 23 -> 25. It pairs directly with Improved Tree of "
              "Life below, which turns that Spirit into healing power.")

# ----------------------------------------------------- tier 4 (rows 6-7)
T.node("swiftmend", "Swiftmend",
       "Teaches Swiftmend, spending a heal-over-time all at once.",
       4, -4, 1, node_type="active",
       effects={"unlock_ability": "druid_swiftmend"},
       connected_to=["natures_bounty"],
       source="WotLK row 6 - MOVED FROM TIER 2 to its real tier 4. The ONLY "
              "unlock for druid_swiftmend, which is requires_talent.")

T.node("natural_perfection", "Natural Perfection",
       "Reduces the damage you take by 2% per rank.",
       4, -2, 3,
       effects={"damage_taken_pct": -0.02},
       connected_to=["natures_bounty"],
       source="WotLK row 6: 'Reduces the chance you'll be critically hit by "
              "4%-12% and your spell damage taken is reduced by 1%-3% after "
              "being the victim of a critical strike.' BOTH CLAUSES "
              "BLOCKED: crit_taken_reduction IS A DEAD TALENT KEY "
              "(measured, and replaced in sun_cleric_blessings, "
              "warlock_demonology and druid_feral this session), and there "
              "is NO ON-CRIT-TAKEN TRIGGER - the twelve proc triggers "
              "include on_damage_taken but nothing that fires only on a "
              "critical hit against you. So it becomes flat mitigation. "
              "BARE damage_taken_pct is read RAW ON BOTH SIDES, so -0.02 is "
              "2%.")

T.node("empowered_rejuvenation", "Empowered Rejuvenation",
       "Increases the healing of your heal-over-time spells by 2% per rank.",
       4, 0, 5,
       effects={"ability_druid_rejuvenation_healing": 0.02,
                "ability_druid_regrowth_healing": 0.02,
                "ability_druid_wild_growth_healing": 0.02},
       connected_to=["living_spirit"],
       source="WotLK row 7: 'The bonus healing effects of your "
              "heal-over-time spells is increased by 4%-20%.' Built on the "
              "three hots by name rather than a global key, because there "
              "is no hot-specific healing MAGNITUDE key - hot_duration_pct "
              "is a duration, and Genesis in druid_balance had to fall back "
              "to the much broader healing_done for the same reason. All "
              "three are effect_type 'hot', so _healing lands on each.")

T.node("living_seed", "Living Seed",
       "Your critical heals plant a seed that blooms into more healing.",
       4, 2, 3,
       proc={"trigger": "on_crit", "chance": 100, "icd": 1,
             "ability_filter": ["druid_regrowth", "druid_healing_touch"],
             "smart_heal_pct": 0.30},
       connected_to=["living_spirit"],
       source="WotLK row 7: 'When you critically heal your target with "
              "Regrowth, Healing Touch or Nourish you plant a Living Seed "
              "on the target for 30% of the amount healed.' BUILT WITH "
              "ITS REAL ON_CRIT TRIGGER, which only became possible on "
              "5 Nov 2026. The whole premise of this talent is a CRITICAL "
              "HEAL, and heals could not crit in this engine until then - "
              "an interim version rode on_heal_cast at a 15% chance as a "
              "workaround. The healing crit change sets self._last_crit in "
              "the heal branch exactly as the damage branches do, which is "
              "what makes ProcTrigger.ON_CRIT fire from a heal, so this is "
              "now the real talent. 100% chance is correct and legitimate "
              "on a multi-rank node ONLY because the crit itself is the "
              "gate - but note the payload does not scale with points, so "
              "ranks buy reliability of access rather than size. "
              "smart_heal_pct reads the triggering heal's amount, one of "
              "only three payloads that read the trigger's value, so the "
              "seed genuinely scales with the crit that planted it.")

# ----------------------------------------------------- tier 5 (rows 8-9)
T.node("revitalize", "Revitalize",
       "Your heal-over-time spells return mana to you.",
       5, -4, 3,
       proc={"trigger": "on_heal_cast", "chance": 10, "icd": 0,
             "ability_filter": ["druid_rejuvenation", "druid_wild_growth"],
             "grant_resource": {"resource": "mana", "amount": 80}},
       connected_to=["empowered_rejuvenation"],
       source="WotLK row 8: 'Your Rejuvenation and Wild Growth ticks have a "
              "5%-15% chance to restore 8 energy, 4 rage, 1% mana or 16 "
              "runic power to the target.' DEPARTURE - A DOT OR HOT TICK IS "
              "NOT A TRIGGER (the twelve triggers are cast, damage, heal, "
              "kill and avoidance events; nothing fires per tick), so it "
              "rides the CAST of those two spells instead. The resource "
              "goes to the DRUID rather than the target, because a talent "
              "effect can never reach an ally. grant_resource is a FLAT "
              "amount - there is no pct_max - so the real 1% is not "
              "expressible. ability_filter is validated by the kit against "
              "the real ability list.")

T.node("tree_of_life", "Tree of Life",
       "Teaches Tree of Life form, rooted and giving.",
       5, -2, 1, node_type="active",
       effects={"unlock_ability": "druid_tree_of_life"},
       connected_to=["living_seed"],
       source="WotLK row 8 - MOVED FROM TIER 3 to its real tier 5. The ONLY "
              "unlock for druid_tree_of_life, which is requires_talent - a "
              "gate set earlier this session, when all five druid forms "
              "turned out to be auto-learned and the talent points spent on "
              "them bought nothing at all.")

T.node("improved_tree_of_life", "Improved Tree of Life",
       "In Tree of Life form, you gain healing power equal to 10% of your "
       "Spirit per rank.",
       5, 0, 3,
       effects={"healing_power_from_spirit_pct": 0.10},
       require_form="tree_of_life",
       connected_to=["tree_of_life"],
       source="WotLK row 8: 'Increases your armor while in Tree of Life "
              "Form by 67%-200%, and increases your healing spells by "
              "5%-15% of your Spirit.' THE SPIRIT HALF IS THE POINT OF THIS "
              "NODE and is built verbatim at 10% per rank - Kyle, 5 Nov: "
              "'resto druid does really well with spirit gear'. It is the "
              "direct payoff for Living Spirit two tiers down: that node "
              "grows Spirit, this one turns Spirit into healing power. "
              "MEASURED: healing_power_from_spirit_pct=0.5 moved healing "
              "power 23 -> 50. RAW MULTIPLIER convention (gained = source * "
              "pct, character.py:1551), so 0.10 and never 10. spirit is a "
              "valid conversion SOURCE and healing_power a valid TARGET. "
              "The armour half is dropped - a tree-form armour bonus is "
              "real but this node already does one clear thing.")

T.node("improved_barkskin", "Improved Barkskin",
       "Increases the effect of your Barkskin by 15% per rank.",
       5, 2, 2,
       effects={"ability_druid_barkskin_potency": 0.15},
       connected_to=["natural_perfection"],
       source="WotLK row 9: 'Increases the damage reduction granted by your "
              "Barkskin spell by 5%/10%, and reduces the chance you'll be "
              "critically hit by melee attacks by 2%/4%.' USES _potency "
              "because druid_barkskin is effect_type 'buff' whose content "
              "is its stat_mods - CHECKED, it really does carry them. The "
              "crit-taken half is dropped: crit_taken_reduction is a DEAD "
              "talent key.")

T.node("gift_of_the_earthmother", "Gift of the Earthmother",
       "Increases your haste by 1% per rank.",
       5, 4, 5, effects={"haste": 1.0},
       connected_to=["improved_tree_of_life"],
       source="WotLK row 9: 'Increases your spell haste by 2%-10% and your "
              "Rejuvenation instantly heals for an additional amount.' The "
              "haste half is built at 1% per rank; haste is POINTS and was "
              "MEASURED (haste=5 moved the attribute 9 -> 14). THE OUTGOING "
              "TREE'S VERSION OF THIS NODE WAS DEAD: it used "
              "ability_druid_rejuvenation_potency, and rejuvenation carries "
              "no stat_mods at all, so there was no potency to scale. The "
              "instant-heal clause is dropped rather than rebuilt as "
              "_healing, because Improved Rejuvenation and Empowered "
              "Rejuvenation already buff that spell and a third node doing "
              "it would read as the same talent printed three times.")

# ----------------------------------------------------- tier 6 (row 10)
T.node("wild_growth", "Wild Growth",
       "Teaches Wild Growth, healing the whole party at once.",
       6, 0, 1, node_type="active",
       effects={"unlock_ability": "druid_wild_growth"},
       connected_to=["gift_of_the_earthmother"],
       source="WotLK row 10, the capstone - MOVED FROM TIER 4 to its real "
              "tier 6. The ONLY unlock for druid_wild_growth, which is "
              "requires_talent. Every one of this tree's four unlocks was "
              "at the wrong tier before this rebuild.")


def main():
    return T.write(was="23 nodes, 73 points - all 4 unlocks at wrong tiers, "
                       "3 dead _crit keys on heals, 1 dead _potency key")


if __name__ == "__main__":
    sys.exit(main())
