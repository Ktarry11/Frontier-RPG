#!/usr/bin/env python3
"""Jewelcrafting works end to end.

    PYTHONPATH=. python3 tools/qa_jewelcrafting.py

Kyle, 14 Nov 2026: build jewelcrafting from the gems that drop from ore, with colours, sockets on
gear from level 30, and rings, necklaces and trinkets; vendors sell cutting kits and settings,
blacksmiths make settings too. His calls: TBC colours, sockets paid from stats, Prospecting, and a
jeweller who takes gems out for a fee. Meta gems written but switched off.

CLAIMS:
  1. Every socket colour can be filled at every mining band up to 300, and every cut gem is worth
     what the one formula says (gem_budget through each stat's cost), never a stat that rounds up
     from almost nothing.
  2. Recipes are whole: every input and output exists, about half are trainer-taught (Kyle: 50 to
     55%), every design sold by a vendor is on a shelf, and every one needs the Jeweler's Kit.
  3. Sockets: never below level 30, never on trinkets, counts by rarity, paid from the item's own
     stats, and a bonus only when every gem fits.
  4. In play: learn it at a forge trainer, need the kit, cut a gem, prospect ore, make a ring and a
     figurine that does something, socket a gem and see the stats move, replace one (the old one
     is gone), have a jeweller take one out for a fee, and keep it all through a save.
  5. Settings: smiths sell the plain ones and the kit, blacksmiths can make every setting.
  6. Meta gems: the rules work, and nothing in the game makes a meta socket yet.
  7. The screens draw: the Jewelcrafting tab, the socket screen both ways, an item card.
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
    d = J.data()
    raw, cuts = d["raw_gems"], d["cut_gems"]
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]

    # 1
    for lo, hi in ((1, 74), (75, 149), (150, 224), (225, 300)):
        have = {c for g in raw.values() if lo <= g["skill"] <= hi for c in J.FITS[g["color"]]}
        for colour in J.COLOURS:
            check(colour in have, f"no gem fits a {colour} socket at mining {lo}-{hi}")
    costs = J.stat_costs()
    for cid, g in cuts.items():
        if g["cut"] == "Prismatic":
            continue
        budget = J.gem_budget(g["level"], g["quality"])
        for st, v in g["stats"].items():
            share = 1.0 / len(g["stats"])
            want = budget * share / costs.get(st, 1.0)
            check(want >= 0.5, f"{cid}: {st} rounds up from {want:.2f}")
            check(abs(v - want) <= 1.0, f"{cid}: {st} {v}, the formula says {want:.1f}")

    # 2
    recipes = cm.all_recipes("jewelcrafting")
    check(len(recipes) > 100, f"only {len(recipes)} jewelcrafting recipes")
    for rid, r in recipes.items():
        for mid in r["inputs"]:
            check(mid in mats, f"{rid}: input {mid} doesn't exist")
        out = r["output"]
        if out["kind"] == "material":
            check(out["material_id"] in mats, f"{rid}: output {out['material_id']} doesn't exist")
        check(r.get("tool") == "jewelers_kit", f"{rid}: doesn't need the kit")
    share = sum(1 for r in recipes.values() if r["source"] == "trainer") / max(1, len(recipes))
    check(0.45 <= share <= 0.60, f"{share:.0%} of recipes are trainer-taught")
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    shelves = {i for v in vendors for i in v["sells"]}
    for rid, r in recipes.items():
        if r["source"] == "vendor":
            check(rid in shelves, f"{rid} is a vendor design and no shop sells it")

    # 3
    random.seed(5)
    counts = {"uncommon": [], "rare": [], "epic": []}
    for rarity in counts:
        for _ in range(60):
            it = gen.generate_armor_piece("chest", "plate", "str_physical", 45, rarity)
            counts[rarity].append(len(J.sockets(it)))
    check(max(counts["uncommon"]) <= 1 and 0 < sum(counts["uncommon"]) < 40, f"uncommon sockets {counts['uncommon'][:10]}")
    check(min(counts["rare"]) >= 1 and max(counts["rare"]) <= 2, "rare gear should have 1 or 2 sockets")
    check(min(counts["epic"]) >= 2 and max(counts["epic"]) <= 3, "epic gear should have 2 or 3 sockets")
    for _ in range(30):
        low = gen.generate_armor_piece("chest", "plate", "str_physical", 25, "epic")
        check(not J.sockets(low), "a level 23 item has a socket")
        tr = gen.generate_armor_piece("trinket", None, "str_physical", 50, "epic")
        check(not J.sockets(tr), "a trinket has a socket")
    # paid from stats: a socketed epic has fewer raw stats than an unsocketed one of the same roll
    random.seed(9)
    total_with, total_without = 0, 0
    for _ in range(80):
        it = gen.generate_armor_piece("legs", "plate", "str_physical", 50, "epic")
        s = sum(v for v in it.get_all_stat_bonuses().values())
        if J.sockets(it):
            total_with += s
    random.seed(9)
    saved = J.SOCKET_ROLLS
    J.SOCKET_ROLLS = {}
    for _ in range(80):
        it = gen.generate_armor_piece("legs", "plate", "str_physical", 50, "epic")
        total_without += sum(v for v in it.get_all_stat_bonuses().values())
    J.SOCKET_ROLLS = saved
    check(total_with < total_without, "sockets didn't cost the item any stats")

    # 4
    with contextlib.redirect_stdout(io.StringIO()):
        hero = Character(name="Gem", char_class="Warrior", level=50)
        party = Party(hero)
    hero.profession_skills = dict(getattr(hero, "profession_skills", {}))
    if hasattr(hero, "learn_profession"):
        with contextlib.redirect_stdout(io.StringIO()):
            hero.learn_profession("jewelcrafting")
    check(hero.knows_profession("jewelcrafting"), "jewelcrafting can't be learned")
    hero.profession_skills["jewelcrafting"] = 300
    if hasattr(hero, "profession_tiers"):
        hero.profession_tiers["jewelcrafting"] = 3
    for rid in recipes:
        hero.known_recipes.add(rid) if isinstance(hero.known_recipes, set) else hero.known_recipes.append(rid)

    def give(mid, n):
        m = gm.make_material_instance(mid)
        m.quantity = n
        hero.add_material(m)

    give("gem_star_ruby", 3)
    ok, msg, _ = cm.craft(hero, "jewelcrafting", "jc_cut_bold_star_ruby")
    check(not ok and "Kit" in msg, f"cut without a kit: {msg}")
    give("jewelers_kit", 1)
    ok, msg, _ = cm.craft(hero, "jewelcrafting", "jc_cut_bold_star_ruby")
    check(ok and hero.get_material_quantity("cut_bold_star_ruby") == 1, f"cutting failed: {msg}")
    check(hero.get_material_quantity("jewelers_kit") == 1, "the kit was used up")
    give("ore_mithril", 5)
    ok, msg, _ = cm.craft(hero, "jewelcrafting", "jc_prospect_mithril")
    got = hero.get_material_quantity("gem_aquamarine") + hero.get_material_quantity("gem_star_ruby") - 2
    check(ok and got >= 1, f"prospecting found nothing: {msg}")
    give("setting_ring_mithril", 1)
    give("bar_mithril", 1)
    give("gem_star_ruby", 1)
    ok, msg, ring = cm.craft(hero, "jewelcrafting", "jc_ring_mithril_str_physical")
    check(ok and ring is not None and ring.slot == "ring", f"ring failed: {msg}")
    give("gem_star_ruby", 2)
    give("gem_topaz", 2)
    give("bar_truesilver", 3)
    ok, msg, lion = cm.craft(hero, "jewelcrafting", "jc_star_ruby_lion")
    check(ok and lion is not None and lion.proc, f"the Star Ruby Lion failed or does nothing: {msg}")

    helm = gen.generate_armor_piece("head", "plate", "str_physical", 50, "epic")
    helm.sockets = [{"color": "red", "gem": None}, {"color": "blue", "gem": None}]
    helm.socket_bonus = {"strength": 4}
    hero.inventory.append(helm)
    before = dict(helm.get_all_stat_bonuses())
    give("cut_bold_star_ruby", 2)
    ok, msg = J.place(hero, helm, 0, "cut_bold_star_ruby")
    after = helm.get_all_stat_bonuses()
    check(ok and after.get("strength", 0) == before.get("strength", 0) + cuts["cut_bold_star_ruby"]["stats"]["strength"],
          f"a socketed gem didn't add its stats: {msg}")
    check(not J.bonus_active(helm), "the bonus is on with a socket empty")
    give("cut_solid_aquamarine", 1)
    J.place(hero, helm, 1, "cut_solid_aquamarine")
    check(J.bonus_active(helm), "the bonus is off with every socket matched")
    J.place(hero, helm, 1, "cut_bold_star_ruby")
    check(not J.bonus_active(helm), "a red gem in a blue socket still turns the bonus on")
    check(hero.get_material_quantity("cut_solid_aquamarine") == 0, "the replaced gem came back")
    party.copper = 0
    ok, msg = J.remove(hero, helm, 0, party=party)
    check(not ok, "a jeweller took a gem out for nothing")
    party.copper = 100000
    ok, msg = J.remove(hero, helm, 0, party=party)
    check(ok and helm.sockets[0]["gem"] is None and hero.get_material_quantity("cut_bold_star_ruby") >= 1
          and party.copper < 100000, f"the jeweller didn't hand the gem back for a fee: {msg}")
    back = Item.from_dict(json.loads(json.dumps(helm.to_dict())))
    check(back.sockets == helm.sockets and back.socket_bonus == helm.socket_bonus, "sockets don't survive a save")

    # 5
    smiths = [v for v in vendors if "jewelers_kit" in v["sells"]]
    check(len(smiths) >= 10, f"only {len(smiths)} shops sell the Jeweler's Kit")
    check(any("setting_ring_copper" in v["sells"] for v in vendors), "nobody sells a copper ring setting")
    bs = json.loads((ROOT / "data/blacksmithing/recipes.json").read_text(encoding="utf-8"))["recipes"]
    for metal in ("copper", "silver", "gold", "mithril", "truesilver", "thorium"):
        for kind in ("ring", "necklace"):
            check(f"bs_setting_{kind}_{metal}" in bs, f"a blacksmith can't make a {metal} {kind} setting")
    trainers = json.loads((ROOT / "data/training/trainers.json").read_text(encoding="utf-8"))["profession_trainers"]
    teach = [k for k, v in trainers.items() if "jewelcrafting" in v]
    check(len(teach) >= 10, f"only {len(teach)} trainers teach jewelcrafting")
    from world.travel_manager import services_for_npc
    npc = type("N", (), {"npc_id": teach[0], "vendor_id": None})()
    check("jeweller" in services_for_npc(npc), "a jewelcrafting trainer can't take gems out")

    # 6
    check(not J.META_ENABLED, "meta gems are switched on; Kyle asked for the code only")
    check(J.requirement_met({"at_least": {"blue": 2}}, {"red": 0, "yellow": 0, "blue": 2}), "meta: at_least")
    check(not J.requirement_met({"more": ["red", "blue"]}, {"red": 1, "yellow": 0, "blue": 1}), "meta: more")
    check(J.requirement_met({"each": 1}, {"red": 1, "yellow": 1, "blue": 1}), "meta: each")
    check(len(d.get("meta_gems", {})) >= 4, "no meta gem definitions")
    random.seed(1)
    for _ in range(40):
        h = gen.generate_armor_piece("head", "plate", "str_physical", 58, "epic")
        check(all(s["color"] != "meta" for s in J.sockets(h)), "a meta socket was rolled while switched off")

    # 7
    with contextlib.redirect_stdout(io.StringIO()):
        from core.game_state import GameStateManager
        from core.game_states import GameState
        screen = pygame.Surface((1600, 900))
        try:
            gsm = GameStateManager(screen)
            gsm.player = hero
            gsm.get_party = lambda: party
            ss = gsm.states[GameState.SOCKETING]
            for mode in ("socket", "remove"):
                ss.start(mode)
                ss.selected_item = helm
                ss.render(screen)
            check(ss.socket_rects, "the socket screen shows no sockets")
            ps = gsm.states[GameState.PROFESSIONS]
            ps.active_tab = "jewelcrafting"
            ps.render(screen)
            inv = gsm.states[GameState.INVENTORY]
            inv._draw_item_tooltip(screen, helm, (100, 100))
        except Exception as exc:
            import traceback
            bad.append(f"a screen failed: {exc}\n{traceback.format_exc()[-900:]}")

    print(f"{len(raw)} stones, {len(cuts)} cut gems, {len(recipes)} recipes, {share:.0%} trainer-taught")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:40]:
            print("  -", b)
        return 1
    print("jewelcrafting OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
