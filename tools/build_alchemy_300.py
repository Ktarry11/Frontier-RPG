#!/usr/bin/env python3
"""Carry Alchemy from skill 225 to 300, and give the six new herbs a sink.

    PYTHONPATH=. python3 tools/build_alchemy_300.py [--apply]

Idempotent. Prints the plan by default; --apply writes it.

=============================================================================
WHY
=============================================================================

Kyle, 7 Nov 2026: "I want to expand out the crafting... expand it out to skill
level 275 for all crafting", then "Go to skill 300."

Alchemy stopped at 225. tools/reanchor_gathering_ladders.py then added six
herbs - Wild Steelbloom, Purple Lotus, Golden Sansam, Dreamfoil, Icecap, Black
Lotus - from node art that had been installed and never wired up, and nothing
consumed them. tools/qa_materials.py caught that immediately and correctly:
"no chain of recipes turns it into anything a player can equip, use or carry".
A gathered material with no sink is a node that wastes a zone slot.

=============================================================================
TRANSMUTE: ARCANITE, AND WHY IT MATTERS MORE THAN A RECIPE
=============================================================================

Verified at warcraft.wiki.gg/wiki/Arcanite_Bar (7 Nov 2026): Arcanite Bar is
NOT smelted. It is an Alchemy transmute at skill 275, from 1 Arcane Crystal +
1 Thorium Bar. I assumed smelting first and checked before building it.

Kyle picked Arcanite as the blacksmithing terminal, which means the top of
blacksmithing now runs through alchemy. That is deliberate and it is the whole
answer to "I want crafting to be FULLY viable as a path alternative to raids
and Dungeons": a raid is a group activity, so the crafting path that competes
with it should be one too. A smith who wants Arcanite needs an alchemist, who
needs a miner carrying Arcane Crystal, which drops at 7% from Thorium veins
(world.gathering_manager.CRYSTAL_FROM_MATERIAL). That is an economy, not a
vending machine.

=============================================================================
WHAT GETS ADDED
=============================================================================

Each new herb gets ONE recipe pitched just above the skill at which the herb
itself becomes gatherable, so finding the herb and being able to use it land
together. Potency follows the existing elixirs' own shape (stat_bonuses,
buff_category, required_level) rather than a new convention.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "data" / "crafting" / "recipes.json"
CONSUM = ROOT / "data" / "consumables" / "consumable_types.json"
MATS = ROOT / "data" / "gathering" / "materials.json"


def spread(lo):
    return [lo + 5, lo + 15, lo + 25, lo + 35]


#: material_id -> definition, for materials this tool must create.
NEW_MATERIALS = {
    "bar_arcanite": dict(
        name="Arcanite Bar", material_type="bar", profession="mining",
        tier="endgame", icon_id="arcanite", stack_limit=20, sell_price=900,
        skill_range=spread(275),
        description="Thorium and raw magic, argued into one metal. It is never quite still."),
}

#: Consumables created here, appended to their list in consumable_types.json.
NEW_CONSUMABLES = {
    "elixirs": [
        dict(consumable_id="elixir_steelbloom", name="Elixir of Steelbloom",
             consumable_type="elixir",
             description="Grants +18 Armor for 30 minutes. Guardian buff.",
             effect_value=0, effect_duration=1800, level_multiplier=0.0,
             required_level=22, cooldown_seconds=5, stack_limit=20,
             vendor_price=900, sell_price=225, buff_category="guardian",
             stat_bonuses={"armor": 18}),
        dict(consumable_id="elixir_purple_lotus", name="Elixir of the Purple Lotus",
             consumable_type="elixir",
             description="Grants +14 Intellect for 30 minutes. Battle buff.",
             effect_value=0, effect_duration=1800, level_multiplier=0.0,
             required_level=40, cooldown_seconds=5, stack_limit=20,
             vendor_price=2200, sell_price=550, buff_category="battle",
             stat_bonuses={"intellect": 14}),
        dict(consumable_id="elixir_icecap", name="Elixir of Icecap",
             consumable_type="elixir",
             description="Grants +22 Stamina and +10 Armor for 30 minutes. Guardian buff.",
             effect_value=0, effect_duration=1800, level_multiplier=0.0,
             required_level=46, cooldown_seconds=5, stack_limit=20,
             vendor_price=4200, sell_price=1050, buff_category="guardian",
             stat_bonuses={"stamina": 22, "armor": 10}),
        dict(consumable_id="flask_black_lotus", name="Flask of the Black Lotus",
             consumable_type="elixir",
             description="Grants +25 to all primary stats for 1 hour. Guardian buff, and the best "
                         "an alchemist can make.",
             effect_value=0, effect_duration=3600, level_multiplier=0.0,
             required_level=50, cooldown_seconds=5, stack_limit=5,
             vendor_price=20000, sell_price=5000, buff_category="guardian",
             stat_bonuses={"strength": 25, "agility": 25, "intellect": 25,
                           "spirit": 25, "stamina": 25}),
    ],
    "health_potions": [
        dict(consumable_id="healing_potion_sansam", name="Major Healing Potion",
             consumable_type="health_potion",
             description="Restores a large amount of health.",
             effect_value=1400, effect_duration=0, level_multiplier=2.4,
             required_level=42, cooldown_seconds=5, stack_limit=20,
             vendor_price=2600, sell_price=650, buff_category=None),
    ],
    "mana_potions": [
        dict(consumable_id="mana_potion_dreamfoil", name="Major Mana Potion",
             consumable_type="mana_potion",
             description="Restores a large amount of mana.",
             effect_value=1200, effect_duration=0, level_multiplier=2.2,
             required_level=44, cooldown_seconds=5, stack_limit=20,
             vendor_price=2800, sell_price=700, buff_category=None),
    ],
}

#: recipe_id -> recipe. Skill sits just above where the herb becomes
#: gatherable, so finding it and being able to use it arrive together.
NEW_RECIPES = {
    "alch_elixir_steelbloom": dict(
        name="Elixir of Steelbloom", skill_required=120, source="trainer",
        inputs={"herb_wild_steelbloom": 2, "vial_empty": 1},
        output={"kind": "consumable", "consumable_id": "elixir_steelbloom"}),
    "alch_elixir_purple_lotus": dict(
        name="Elixir of the Purple Lotus", skill_required=215, source="trainer",
        inputs={"herb_purple_lotus": 2, "herb_khadgar": 1, "vial_empty": 1},
        output={"kind": "consumable", "consumable_id": "elixir_purple_lotus"}),
    "alch_major_healing": dict(
        name="Major Healing Potion", skill_required=260, source="trainer",
        inputs={"herb_golden_sansam": 2, "herb_sungrass": 1, "vial_empty": 1},
        output={"kind": "consumable", "consumable_id": "healing_potion_sansam"}),
    "alch_major_mana": dict(
        name="Major Mana Potion", skill_required=270, source="trainer",
        inputs={"herb_dreamfoil": 2, "herb_blindweed": 1, "vial_empty": 1},
        output={"kind": "consumable", "consumable_id": "mana_potion_dreamfoil"}),
    "alch_elixir_icecap": dict(
        name="Elixir of Icecap", skill_required=290, source="trainer",
        inputs={"herb_icecap": 2, "herb_dreamfoil": 1, "vial_empty": 1},
        output={"kind": "consumable", "consumable_id": "elixir_icecap"}),
    "alch_flask_black_lotus": dict(
        name="Flask of the Black Lotus", skill_required=300, source="vendor",
        vendor_location="Gadgetzan",
        inputs={"herb_black_lotus": 1, "herb_icecap": 2, "herb_dreamfoil": 2,
                "vial_empty": 1},
        output={"kind": "consumable", "consumable_id": "flask_black_lotus"}),
    # The terminal of traditional crafting - see the module docstring.
    "alch_transmute_arcanite": dict(
        name="Transmute: Arcanite", skill_required=275, source="vendor",
        vendor_location="Gadgetzan",
        inputs={"crystal_arcane": 1, "bar_thorium": 1},
        output={"kind": "material", "material_id": "bar_arcanite"}),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    mats_doc = json.loads(MATS.read_text(encoding="utf-8"))
    mats = mats_doc["materials"]
    rec_doc = json.loads(RECIPES.read_text(encoding="utf-8"))
    alch = rec_doc["professions"]["alchemy"]["recipes"]
    con_doc = json.loads(CONSUM.read_text(encoding="utf-8"))

    # every input must already exist, or the recipe is unbuildable
    missing = sorted({i for r in NEW_RECIPES.values() for i in r["inputs"]}
                     - set(mats) - set(NEW_MATERIALS))
    if missing:
        print(f"  REFUSING - {len(missing)} recipe input(s) do not exist: {', '.join(missing)}")
        return 1

    made_m = [m for m in NEW_MATERIALS if m not in mats]
    made_c = {k: [c for c in v if c["consumable_id"] not in
                  {x["consumable_id"] for x in con_doc.get(k, [])}]
              for k, v in NEW_CONSUMABLES.items()}
    made_r = [r for r in NEW_RECIPES if r not in alch]

    before = max((r.get("skill_required", 0) for r in alch.values()
                  if isinstance(r, dict)), default=0)
    after = max(before, max(r["skill_required"] for r in NEW_RECIPES.values()))
    print(f"  alchemy reaches skill {before} -> {after}  ({len(alch)} -> {len(alch) + len(made_r)} recipes)\n")

    if made_m:
        print(f"  materials  {', '.join(made_m)}")
    for k, v in made_c.items():
        if v:
            print(f"  {k:11}{', '.join(c['name'] for c in v)}")
    if made_r:
        print(f"\n  {'recipe':34}{'skill':>6}   consumes")
        for rid in made_r:
            r = NEW_RECIPES[rid]
            ins = ", ".join(f"{n}x{q}" for n, q in r["inputs"].items() if n != "vial_empty")
            print(f"  {r['name'][:32]:34}{r['skill_required']:>6}   {ins}")
    if not (made_m or made_r or any(made_c.values())):
        print("  nothing to do - already applied")

    # icon check: a bar with no art renders as a text box, which is legible but
    # worth saying out loud rather than discovering in game.
    for mid in made_m:
        spec = NEW_MATERIALS[mid]
        folder = {"bar": "bars"}.get(spec["material_type"], spec["material_type"])
        art = ROOT / "assets" / "gathering_nodes" / folder / f"{spec['icon_id']}.png"
        if not art.exists():
            print(f"\n  ICON PENDING  {spec['name']} wants {art.relative_to(ROOT)}"
                  f"  (bag shows a text box until it lands)")

    if args.apply:
        for mid in made_m:
            mats[mid] = NEW_MATERIALS[mid]
        MATS.write_text(json.dumps(mats_doc, indent=2) + "\n", encoding="utf-8")
        for k, v in made_c.items():
            con_doc.setdefault(k, []).extend(v)
        CONSUM.write_text(json.dumps(con_doc, indent=2) + "\n", encoding="utf-8")
        for rid in made_r:
            r = dict(NEW_RECIPES[rid])
            r["skill_range"] = spread(r["skill_required"])
            alch[rid] = r
        RECIPES.write_text(json.dumps(rec_doc, indent=2) + "\n", encoding="utf-8")
        print("\n  wrote materials.json, consumable_types.json, recipes.json")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
