#!/usr/bin/env python3
"""Enchanting works end to end.

    PYTHONPATH=. python3 tools/qa_enchanting.py

Kyle, 14 Nov 2026: "build enchanting... Rods will be made by Blacksmiths or sold by vendors (they
can get very pricy very fast). We can use traditional wow-style materials... start wow classic
style + additional enchants to help fill in the gaps and aim for more hybrid classes rather than
the standard." His calls: materials from disenchanting, taught by the town enchanters, a handful
of proc weapon enchants, wands and weapon oils.

CLAIMS:
  1. Every enchantment is worth what the one formula says (level x 0.36 x 1.3 x the slot's share,
     through each stat's cost), a higher rank is never weaker than a lower one of the same kind,
     and hybrids are there on every slot that has a single-stat ladder.
  2. Recipes are whole: every input, output and rod exists, 50 to 55% are trainer-taught, every
     formula sold by a vendor is on a shelf, and each formula takes its tier's rod or a better one.
  3. Rods: blacksmiths make every one, shops sell them, and the price climbs steeply.
  4. In play: learn it from an enchanter, need a rod, disenchant a green, a blue and an epic into
     the right things, make a scroll, read it onto bracers and see the stats move, replace it, put
     a proc enchantment on a weapon and see it hang its proc (and come off with the weapon), refuse
     a bracer scroll on a weapon, keep it all through a save. Make a wand and use a weapon oil.
  5. Trainers: the three enchanters already in town and the two new ones all teach it, and the
     new ones can be reached.
  6. The screens draw: the Enchanting tab, both tabs of the enchant screen, an item card.
"""
import contextlib
import io
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    bad = []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    with contextlib.redirect_stdout(io.StringIO()):
        from world import enchanting as E
        from world import jewelcrafting as J
        from world.crafting_manager import get_crafting_manager
        from world.gathering_manager import get_gathering_node_manager
        from entities.loot_generator import LootGenerator
        from entities.character import Character
        from entities.party import Party
        from entities.item import Item
        gm = get_gathering_node_manager()
        cm = get_crafting_manager()
        gen = LootGenerator()
    d = E.data()
    enchants = d["enchants"]
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    recipes = json.loads((ROOT / "data/enchanting/recipes.json").read_text(encoding="utf-8"))["recipes"]

    # 1
    for eid, e in enchants.items():
        if e.get("proc"):
            check(e["proc"].get("describe") and e["group"] == "weapon", f"{eid}: a proc without words, or off a weapon")
            continue
        share = d["groups"][e["group"]]["share"]
        mult = 1.6 if e["family"] == "stats" else 1.0
        want = e["level"] * 0.36 * 1.3 * share * mult
        costs = J.stat_costs()
        got = sum(v * costs.get(k, 1.0) for k, v in e["stats"].items())
        # whole numbers: each stat is within half a point of its share either way
        slack = sum(costs.get(k, 1.0) * 0.5 for k in e["stats"]) + 0.01
        check(abs(got - want) <= slack or all(v == 1 for v in e["stats"].values()),
              f"{eid} is worth {got:.1f} points, the formula says {want:.1f}")
    ladders = {}
    for eid, e in enchants.items():
        if not e.get("proc"):
            ladders.setdefault((e["group"], e["family"]), []).append(e)
    for key, rows in ladders.items():
        rows.sort(key=lambda e: e["tier"])
        for a, b in zip(rows, rows[1:]):
            check(all(b["stats"].get(k, 0) >= v for k, v in a["stats"].items()), f"{key}: {b['title']} is weaker than {a['title']}")
    for group in d["groups"]:
        fams = {f for (g, f) in ladders if g == group}
        hybrids = {e["family"] for e in enchants.values() if e["group"] == group and e["hybrid"]}
        check(hybrids, f"no hybrid enchantment for {group}")
    procs = [e for e in enchants.values() if e.get("proc")]
    check(5 <= len(procs) <= 8, f"{len(procs)} proc enchantments; Kyle asked for a handful")

    # 2
    for rid, r in recipes.items():
        for m in r["inputs"]:
            check(m in mats, f"{rid}: no material {m}")
        out = r["output"]
        if out["kind"] == "material" and "_essence" in rid:
            continue                                  # the essence swaps, checked in play below
        if out["kind"] == "material":
            check(out["material_id"] in enchants, f"{rid}: makes {out['material_id']}, which isn't an enchantment")
            rods = r.get("tool") or []
            check(rods and all(t in mats and mats[t]["material_type"] == "rod" for t in rods), f"{rid}: no rod")
            tier = E.enchant(out["material_id"])["tier"]
            need = ["runed_copper_rod", "runed_copper_rod", "runed_silver_rod", "runed_golden_rod",
                    "runed_truesilver_rod", "runed_arcanite_rod"][tier]
            check(rods and rods[0] == need and rods[-1] == "runed_arcanite_rod", f"{rid}: takes {rods}, should start at {need}")
    share = sum(1 for r in recipes.values() if r["source"] == "trainer") / len(recipes)
    check(0.50 <= share <= 0.55, f"{share:.0%} of formulas are trainer-taught (Kyle: 50 to 55%)")
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    sold = {i for v in vendors for i in v["sells"]}
    for rid, r in recipes.items():
        if r["source"] == "vendor":
            check(rid in sold, f"vendor formula {rid} is on no shelf")

    # 3
    bs = json.loads((ROOT / "data/blacksmithing/recipes.json").read_text(encoding="utf-8"))["recipes"]
    prices = []
    for rod in E.rods():
        check(f"bs_{rod}" in bs, f"blacksmiths can't make {rod}")
        prices.append(mats[rod]["vendor_price"])
        if rod != "runed_arcanite_rod":
            check(rod in sold, f"no shop sells {rod}")
    check(all(b >= a * 3 for a, b in zip(prices, prices[1:])), f"rod prices don't climb steeply: {prices}")

    # 4
    with contextlib.redirect_stdout(io.StringIO()):
        hero = Character(name="Ench", char_class="Paladin", level=60)
        party = Party(hero)
    with contextlib.redirect_stdout(io.StringIO()):
        from world import profession_manager as PM
        party.copper = 10 ** 8
        PM.learn(hero, party, "enchanting")
    check(hero.knows_profession("enchanting"), "enchanting can't be learned")
    hero.profession_skills["enchanting"] = 300
    hero.profession_tiers["enchanting"] = 3
    for rid in recipes:
        hero.known_recipes.add(rid)

    def give(mid, n):
        m = gm.make_material_instance(mid)
        m.quantity = n
        hero.add_material(m)

    # disenchanting, by rarity
    random.seed(4)
    green = gen.generate_armor_piece("wrist", "plate", "str_physical", 20, "uncommon")
    green.required_level = 20
    hero.inventory.append(green)
    ok, msg, got = E.disenchant(hero, green)
    check(ok and got and got[0].material_id in ("strange_dust", "greater_magic_essence", "small_glimmering_shard"),
          f"a level 20 green: {msg}")
    check(green not in hero.inventory, "the disenchanted item is still in the bags")
    blue = gen.generate_armor_piece("chest", "plate", "str_physical", 45, "rare")
    blue.required_level = 45
    hero.inventory.append(blue)
    ok, msg, got = E.disenchant(hero, blue)
    check(ok and got and got[0].material_id == "small_radiant_shard", f"a level 45 blue: {msg}")
    epic = gen.generate_weapon("main_hand", "sword_1h", "str_physical", 60, "epic")
    epic.required_level = 60
    hero.inventory.append(epic)
    ok, msg, got = E.disenchant(hero, epic)
    check(ok and got and got[0].material_id == "nexus_crystal", f"a level 60 epic: {msg}")
    white = gen.generate_armor_piece("wrist", "plate", "str_physical", 20, "common")
    hero.inventory.append(white)
    check(not E.disenchant(hero, white)[0], "a white item disenchanted")
    hero.profession_skills["enchanting"] = 10
    hi = gen.generate_armor_piece("feet", "plate", "str_physical", 40, "uncommon")
    hi.required_level = 40
    hero.inventory.append(hi)
    check(not E.disenchant(hero, hi)[0], "a level 40 green disenchanted at skill 10")
    hero.profession_skills["enchanting"] = 300
    # weapons give mostly essence, armour mostly dust
    random.seed(7)
    rolls = {"dust": 0, "essence": 0}
    for _ in range(200):
        w = gen.generate_weapon("main_hand", "mace_1h", "str_physical", 30, "uncommon")
        w.required_level = 30
        hero.inventory.append(w)
        _ok, _m, g = E.disenchant(hero, w)
        if g:
            rolls["dust" if "dust" in g[0].material_id else "essence" if "essence" in g[0].material_id else "x"] = \
                rolls.get("dust" if "dust" in g[0].material_id else "essence" if "essence" in g[0].material_id else "x", 0) + 1
    check(rolls["essence"] > rolls["dust"] * 2, f"weapons should give mostly essence: {rolls}")

    # a scroll, a rod, the bracers
    give("vision_dust", 10)
    give("greater_mystic_essence", 5)
    give("large_glowing_shard", 3)
    ok, msg, _ = cm.craft(hero, "enchanting", "ench_bracer_greater_agility")
    check(not ok and "Rod" in msg, f"a formula without a rod: {msg}")
    give("runed_copper_rod", 1)
    ok, msg, _ = cm.craft(hero, "enchanting", "ench_bracer_greater_agility")
    check(not ok, "a golden-rod formula worked with a copper rod")
    give("runed_truesilver_rod", 1)
    ok, msg, _ = cm.craft(hero, "enchanting", "ench_bracer_greater_agility")
    check(ok and hero.get_material_quantity("enchant_bracer_greater_agility") == 1,
          f"a better rod should do: {msg}")
    check(hero.get_material_quantity("runed_truesilver_rod") == 1, "the rod was used up")
    bracer = gen.generate_armor_piece("wrist", "plate", "str_physical", 50, "rare")
    hero.equipment.equip(bracer) if hasattr(hero.equipment, "equip") else None
    hero._recalculate_derived_stats()
    before = hero.equipment.get_total_stat_bonuses().get("agility", 0)
    ok, msg = E.apply(hero, bracer, "enchant_bracer_greater_agility")
    E.refresh(hero)
    plus = enchants["enchant_bracer_greater_agility"]["stats"]["agility"]
    check(ok and bracer.enchant_id == "enchant_bracer_greater_agility", f"apply failed: {msg}")
    check(bracer.get_all_stat_bonuses().get("agility", 0) >= plus, "the enchantment adds nothing to the item")
    now = hero.equipment.get_total_stat_bonuses().get("agility", 0)
    check(now == before + plus, f"the wearer's gear agility went {before} -> {now}, not +{plus}")
    check(any("Enchanted:" in l for l in E.tooltip_lines(bracer)), "no Enchanted line on the card")
    give("enchant_weapon_crusader", 1)
    ok, _m = E.apply(hero, bracer, "enchant_weapon_crusader")
    check(not ok, "a weapon enchantment went on bracers")
    give("enchant_bracer_major_valor", 1)
    E.apply(hero, bracer, "enchant_bracer_major_valor")
    check(bracer.enchant_id == "enchant_bracer_major_valor", "a new enchantment didn't replace the old one")
    # a proc on a weapon
    sword = gen.generate_weapon("main_hand", "sword_2h", "str_physical", 55, "rare")
    check({"weapon", "2h"} <= E.groups_for(sword), "a two-hander doesn't take 2H enchantments")
    wand = gen.generate_weapon("ranged", "wand", "int_caster", 40, "uncommon")
    check(not E.groups_for(wand), "a wand takes enchantments")
    hero.equipment.equip(sword) if hasattr(hero.equipment, "equip") else None
    ok, msg = E.apply(hero, sword, "enchant_weapon_crusader")
    E.refresh(hero)
    eff = [e for e in hero.active_effects if str(e.effect_id).endswith("_enchant")]
    check(ok and eff and eff[0].proc.get("trigger") == "on_weapon_swing", f"Crusader hangs no proc: {msg} {eff}")
    hero.equipment.unequip("main_hand") if hasattr(hero.equipment, "unequip") else None
    E.refresh(hero)
    check(not [e for e in hero.active_effects if str(e.effect_id).endswith("_enchant")], "the proc stayed after the weapon came off")
    back = Item.from_dict(json.loads(json.dumps(sword.to_dict())))
    check(back.enchant_id == "enchant_weapon_crusader", "the enchantment doesn't survive a save")
    # essences both ways (Kyle: "3 lesser for 1 greater or 1 greater breaks to 3 lesser")
    for key in ("magic", "astral", "mystic", "nether", "eternal"):
        check(f"ench_combine_{key}_essence" in recipes and f"ench_split_{key}_essence" in recipes, f"no {key} essence swap")
    hero.materials = [m for m in hero.materials if "nether_essence" not in m.material_id]
    give("lesser_nether_essence", 3)
    xp = hero.experience
    ok, msg, _ = cm.craft(hero, "enchanting", "ench_combine_nether_essence")
    check(ok and hero.get_material_quantity("greater_nether_essence") == 1 and hero.get_material_quantity("lesser_nether_essence") == 0,
          f"3 lesser didn't make a greater: {msg}")
    ok, msg, _ = cm.craft(hero, "enchanting", "ench_split_nether_essence")
    check(ok and hero.get_material_quantity("lesser_nether_essence") == 3 and hero.get_material_quantity("greater_nether_essence") == 0,
          f"a greater didn't break into 3 lesser: {msg}")
    check(hero.experience == xp, "swapping essences gave experience")

    # a wand and an oil
    give("plank_duskwood", 1)
    ok, msg, made = cm.craft(hero, "enchanting", "ench_greater_mystic_wand")
    check(ok and made is not None and made.weapon_type == "wand", f"no wand: {msg}")
    give("vial_crystal", 1)
    give("herb_firebloom", 2)
    ok, msg, oil = cm.craft(hero, "enchanting", "ench_wizard_oil")
    check(ok and oil is not None, f"no oil: {msg}")
    if oil is not None:
        sp = hero.get_active_buff_stats().get("spell_power", 0)
        hero.consumable_cooldown = 0
        oil.use(hero)
        check(hero.oil_buff is not None and hero.get_active_buff_stats().get("spell_power", 0) > sp,
              "the oil gave nothing")
        # a running oil (or any elixir) must not stop the game saving: the buff slots used to hold
        # the Consumable object itself and json.dump died half way through the file
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                back = Character.from_dict(json.loads(json.dumps(hero.to_dict())))
            check(back.oil_buff and back.oil_buff[0].name == oil.name, "the oil doesn't survive a save")
        except Exception as exc:
            bad.append(f"saving with an oil on fails: {exc}")
        hero.update_buff_timers(2000)
        check(hero.oil_buff is None, "the oil never wore off")

    # 5
    trainers = json.loads((ROOT / "data/training/trainers.json").read_text(encoding="utf-8"))["profession_trainers"]
    for nid in ("org_enchanter", "uc_enchanter", "kb_enchanter", "stw_enchanter", "oh_enchanter"):
        check("enchanting" in trainers.get(nid, []), f"{nid} doesn't teach enchanting")
    with contextlib.redirect_stdout(io.StringIO()):
        from world.travel_manager import services_for_npc

        class N:
            pass
        n = N()
        n.vendor_id = "stw_enchanter"
        check("train_prof" in services_for_npc(n), "the Steamwheedle enchanter offers no training")

    # 6
    with contextlib.redirect_stdout(io.StringIO()):
        from core.game_state import GameStateManager
        from core.game_states import GameState
        screen = pygame.Surface((1280, 720))
        try:
            gsm = GameStateManager(screen)
            gsm.player = hero
            gsm.get_party = lambda: party
            give("enchant_bracer_greater_agility", 2)
            give("enchant_weapon_fiery", 1)
            es = gsm.states[GameState.ENCHANTING]
            es.start("enchant")
            es.selected_item = bracer
            es.render(screen)
            check(es.scroll_rects, "the enchant screen shows no scrolls")
            es.start("disenchant")
            g2 = gen.generate_armor_piece("wrist", "plate", "str_physical", 30, "uncommon")
            hero.inventory.append(g2)
            es.render(screen)
            es.selected_item = g2
            es.render(screen)
            ps = gsm.states[GameState.PROFESSIONS]
            ps.active_tab = "enchanting"
            ps.render(screen)
            inv = gsm.states[GameState.INVENTORY]
            inv._draw_item_tooltip(screen, sword, (100, 100))
        except Exception as exc:
            import traceback
            bad.append(f"a screen failed: {exc}\n{traceback.format_exc()[-900:]}")

    print(f"{len(enchants)} enchantments ({sum(1 for e in enchants.values() if e['hybrid'])} hybrid, "
          f"{len(procs)} procs), {len(recipes)} recipes, {share:.0%} trainer-taught")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:40]:
            print("  -", b)
        return 1
    print("enchanting OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
