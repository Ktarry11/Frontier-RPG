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
  7. Kyle, 20 Nov 2026, the switches: with "quests complete on accept" on, a kill quest and a fetch quest are ready
     to hand in the moment they're accepted, the fetch one stays ready after the bag is counted, and both hand in;
     off, a quest starts empty. With "one-hit kills" on, the party's hit kills, an enemy's hit on an enemy doesn't,
     and a phased boss stops at its next phase.
  8. The Collection: a learned thing can be removed for the account, and "Remove everything" empties it.
  9. Friendship: a recruit steps up through the stages to Friend, Make Sworn gives the keepsake, and two recruits
     can be moved to friendly, close friends, grating and rivals.
 10. The barber's chair (Kyle, 20 Nov 2026: "lets make a barber choice if the sprite is gone"): a saved look past the
     end of its list, or one whose pictures are gone, is missing and sends the character to the chair; a look that's
     there doesn't; picking one in the chair fixes it.
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
    from ui.screens.testing_screen import TABS
    for key, _label in TABS:
        ts._switch(key)
        ts.render(screen)
        check(ts.hits, f"the {key} tab draws no buttons")
    ts._switch("gold")
    ts.render(screen)
    gold_btn = next(r for r, _a in ts.hits if r.y > 140)
    before = party.copper
    ts.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=gold_btn.center, button=1))
    check(party.copper > before, f"clicking a gold button gave nothing: {ts.message}")

    switches(check)

    print(f"{len(towns)} towns, {len(zones)} zones, {len(rows)} recruits, {len(profs)} professions, "
          f"{len(hero.known_recipes)} recipes, {len(hero.materials)} material stacks")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("testing menu OK")
    return 0


def switches(check):
    """Claims 7-9, against scratch copies of the switch file and the Collection so the real ones aren't touched."""
    import tempfile
    from world import testing as T
    from world.quest import QuestStatus, ObjectiveType
    from world.quest_manager import QuestManager
    from entities import account_collection as AC
    from entities.character import Character
    from world import collection as C
    tmp = Path(tempfile.mkdtemp())
    T.FLAGS_PATH, T._flags = tmp / "flags.json", None
    old_col = AC.use_path(tmp / "collection.json")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            qm = QuestManager()
            hero = Character("Tester", "warrior", 60)

        def pick(t):
            return next(q for q in qm.quests.values() if q.status == QuestStatus.NOT_STARTED and q.objectives
                        and not (q.grant_items or {}).get("on_accept") and all(o.objective_type == t for o in q.objectives))

        class _P:
            members, bench, player = [hero], [], hero

            def award_experience(self, x):
                pass

            def add_currency(self, g):
                pass

        T.toggle("auto_quests")
        kq, fq = pick(ObjectiveType.KILL), pick(ObjectiveType.FETCH)
        for q in (kq, fq):
            qm.accept_quest(q.quest_id, player=hero)
            check(q.status == QuestStatus.READY_TO_TURN_IN, f"{q.quest_id} wasn't ready on accept with the switch on")
        qm.refresh_gather_progress(hero)
        check(fq.status == QuestStatus.READY_TO_TURN_IN, "the bag count undid a fetch quest the switch filled")
        with contextlib.redirect_stdout(io.StringIO()):
            check(qm.turn_in_quest(kq.quest_id, hero, _P()) and qm.turn_in_quest(fq.quest_id, hero, _P()),
                  "a quest the switch filled wouldn't hand in")
        T.toggle("auto_quests")
        q3 = pick(ObjectiveType.KILL)
        qm.accept_quest(q3.quest_id, player=hero)
        check(q3.status == QuestStatus.ACTIVE, "a quest finished on accept with the switch off")
        T.complete_active_quests()

        from world.creature_manager import CreatureManager
        with contextlib.redirect_stdout(io.StringIO()):
            cm = CreatureManager()
            a, b = cm.spawn_creature("Old Thunderbeak", level=48), cm.spawn_creature("Old Thunderbeak", level=48)
        T.toggle("one_hit")
        b.take_damage(1, "physical", 48, attacker=a)
        check(b.current_health > 0, "one-hit kills worked for an enemy hitting an enemy")
        a.take_damage(1, "physical", 60, attacker=hero)
        check(a.current_health == 0, f"one-hit kills left an enemy on {a.current_health}")
        a.current_health, a.max_health = 1000, 1000
        a.phases, a.phase_index = [{"at_pct": 50, "text": "test"}], 0
        a._enter_phase = lambda: setattr(a, "_phase_due", False)
        a.take_damage(1, "physical", 60, attacker=hero)
        check(a.current_health == 500, f"one-hit kills skipped a phase (health {a.current_health}, wanted 500)")
        T.toggle("one_hit")
        check(not T.any_on(), "a switch stayed on after being turned off")

        ids = [e["id"] for e in C.entries()[:3]]
        for cid in ids:
            C.grant(cid, commit=False)
        T.remove_collectable(ids[0])
        check(not C.learned(ids[0]) and C.learned(ids[1]), "removing one thing from the Collection didn't")
        T.remove_all_collectables()
        check(not T.learned_collectables(), "Remove everything left things in the Collection")

        rows = T.bonded()
        rid, other = rows[0][0], rows[1][0]
        for _ in range(4):
            T.raise_stage(rid)
        check(T.stage_name(rows[0][2]) == "Friend", f"Next stage stopped at {T.stage_name(rows[0][2])}, not Friend")
        T.make_sworn(rid)
        check(T.stage_name(rows[0][2]) == "Sworn" and C.learned(C.keepsake_of(rid)),
              "Make Sworn didn't swear them or give the keepsake")
        seen = []
        for step in (1, 1, -1, -1, -1, -1):
            T.nudge_pair(rid, other, step)
            seen.append(T.pair_state(rid, other)[0])
        for want in ("Friendly", "Close friends", "Grating", "Rivals"):
            check(want in seen, f"two recruits never reached {want} ({seen})")
        from world import race_registry as RR
        from ui.screens.barber_screen import BarberScreen
        check(not RR.look_is_missing("orc", "male", 0), "orc look 1 counted as missing")
        check(RR.look_is_missing("orc", "male", 999), "a look past the end of the list wasn't missing")
        g = RR.get_gender("orc", "male")
        g.variants.append("orc_gone_qa")
        try:
            check(RR.look_is_missing("orc", "male", len(g.variants) - 1), "a look with no pictures wasn't missing")
            check(len(g.variants) - 1 not in RR.pickable_looks("orc", "male"), "the barber offered a look with no pictures")
        finally:
            g.variants.remove("orc_gone_qa")
        hero.race, hero.gender, hero.appearance_variant = "orc", "male", 999
        check(BarberScreen.needed(hero), "a character whose look is gone isn't sent to the barber")
        hero.appearance_variant = 3
        check(not BarberScreen.needed(hero), "a character with a good look is sent to the barber")
    finally:
        AC.use_path(old_col)
        T.FLAGS_PATH, T._flags = Path(T.__file__).resolve().parent.parent / "data" / "saves" / "testing_flags.json", None


if __name__ == "__main__":
    sys.exit(main())
