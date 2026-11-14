#!/usr/bin/env python3
"""The Testing menu does what each button says.

    PYTHONPATH=. python3 tools/qa_testing_menu.py

Kyle, 14 Nov 2026: a testing menu with subtabs to teleport to any town and unlock every flight
master, force any recruit into the party, give gold, learn every profession and set it to
75/150/225/300, and get every profession resource, "to be able to agitate the system and check it
without spending hours".

CLAIMS:
  1. Travel: every flight path opens; teleporting to a town and to a plain zone lands the party in it.
  2. Recruits: any recruit joins at once, even one far above the player's level; a second click
     sends them home.
  3. Gold and levels: gold lands in the purse; the whole party levels to 60 through level_up.
  4. Professions: every profession learned, past the primary limit; each skill level sets the tier
     cap with it and teaches the trainer recipes; "every recipe" teaches the rest; a recipe can then
     be crafted from the materials the menu gives.
  5. Materials: "Everything" gives every material in the game; a group gives only that group.
  6. The screen draws every tab and its buttons work by clicking.
"""
import contextlib
import io
import os
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
    screen = pygame.display.set_mode((1280, 720))
    bad = []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    with contextlib.redirect_stdout(io.StringIO()):
        from core.game_state import GameStateManager
        from core.game_states import GameState
        from entities.character import Character
        from entities.party import Party
        from world import testing as T
        from world.travel_manager import get_travel_manager, TravelManager
        from world.gathering_manager import get_gathering_node_manager
        from world.crafting_manager import get_crafting_manager
        sm = GameStateManager(screen)
        hero = Character(name="Tester", char_class="Warrior", level=10)
        party = Party(hero)
        sm.player = hero
        sm.get_party = lambda: party
        zm = sm._live_zone_manager()

    # 1
    T.unlock_flights()
    check(get_travel_manager().known_nodes >= set(TravelManager.nodes()), "not every flight path opened")
    towns = T.towns(zm)
    check(len(towns) >= 20, f"only {len(towns)} towns to teleport to")
    for dest in (towns[0], towns[len(towns) // 2], towns[-1]):
        with contextlib.redirect_stdout(io.StringIO()):
            T.teleport(zm, dest)
        check(zm.current_zone and zm.current_zone.name == dest["zone"], f"teleport to {dest['label']} landed in "
              f"{zm.current_zone.name if zm.current_zone else None}")
    zones = T.zones(zm)
    from world.hidden_zones import is_hidden
    check(len(zones) == len([n for n in zm.zones if not is_hidden(n)]), "the zone list is missing zones")
    caves = [z for z in zones if z["x"] is not None and z["zone"] not in {t["zone"] for t in towns}]
    if caves:
        with contextlib.redirect_stdout(io.StringIO()):
            T.teleport(zm, caves[0])
        check(zm.current_zone.name == caves[0]["zone"], f"teleport to the zone {caves[0]['label']} failed")

    # 2
    rows = T.recruits()
    check(len(rows) >= 10, f"only {len(rows)} recruits listed")
    high = max(rows, key=lambda kv: kv[1].level)
    with contextlib.redirect_stdout(io.StringIO()):
        msg = T.force_recruit(party, high[0])
    member = next((m for m in T.everyone(party) if getattr(m, "recruit_id", None) == high[0]), None)
    check(member is not None, f"a level {high[1].level} recruit didn't join a level 10 player: {msg}")
    with contextlib.redirect_stdout(io.StringIO()):
        for rid, _r in rows[:3]:
            T.force_recruit(party, rid)
    check(len(T.everyone(party)) >= 4, "forced recruits didn't join")
    if member is not None:
        with contextlib.redirect_stdout(io.StringIO()):
            T.send_home(party, member)
        check(member not in T.everyone(party), "send home didn't")

    # 3
    before = party.copper
    T.add_gold(party, 1000)
    check(party.copper == before + 1000 * 10000, "gold didn't land")
    with contextlib.redirect_stdout(io.StringIO()):
        T.level_party(party, 60)
    check(all(m.level == 60 for m in T.everyone(party)), "the party didn't reach 60")

    # 4
    T.learn_all_professions(hero)
    profs = T.professions()
    check(set(profs) <= set(hero.known_professions), "not every profession learned")
    for s in (75, 150, 225, 300):
        T.set_profession_skill(hero, s)
        check(all(hero.profession_skills[p] == s and hero.profession_cap(p) >= s for p in profs),
              f"skill {s} didn't set every profession and its cap")
    n_trainer = len(hero.known_recipes)
    T.learn_every_recipe(hero)
    check(len(hero.known_recipes) > n_trainer, "learning every recipe added nothing")

    # 5
    gm = get_gathering_node_manager()
    T.give_materials(hero, "gems")
    check(hero.get_material_quantity("gem_garnet") == 20 and hero.get_material_quantity("strange_dust") == 0,
          "the gems group gave the wrong things")
    T.give_materials(hero, "all")
    missing = [mid for mid in gm.materials if hero.get_material_quantity(mid) < 1]
    check(not missing, f"{len(missing)} materials not given, e.g. {missing[:5]}")
    cm = get_crafting_manager()
    ok, msg, _ = cm.craft(hero, "enchanting", "ench_bracer_major_strength")
    check(ok, f"couldn't craft with the menu's materials and recipes: {msg}")

    # 6
    ts = sm.states[GameState.TESTING]
    ts.start()
    for key, _label in [("travel", 0), ("recruits", 0), ("gold", 0), ("professions", 0), ("materials", 0)]:
        ts._switch(key)
        ts.render(screen)
        check(ts.hits, f"the {key} tab draws no buttons")
    ts._switch("gold")
    ts.render(screen)
    gold_btn = next(r for r, _a in ts.hits if r.y > 140)
    before = party.copper
    ts.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=gold_btn.center, button=1))
    check(party.copper > before, f"clicking a gold button gave nothing: {ts.message}")

    print(f"{len(towns)} towns, {len(zones)} zones, {len(rows)} recruits, {len(profs)} professions, "
          f"{len(hero.known_recipes)} recipes, {len(hero.materials)} material stacks")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("testing menu OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
