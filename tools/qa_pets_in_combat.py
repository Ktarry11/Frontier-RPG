#!/usr/bin/env python3
"""A pet is an ally. Everything ally-shaped has to survive being handed one.

    PYTHONPATH=. python3 tools/qa_pets_in_combat.py

Kyle, 2026-10-31: "so pets dont show anything, tried warlock. also did
chronomancer heal and got this" - ValueError: Pet is not in list, out of
combat_screen._rect_for_combatant.

Both halves are one fact. combat_engine.is_ally() counts pets, living_allies()
counts pets, the turn order runs them, a heal can validly target one - but
combat_engine.allies is party.members and nothing else, because pets live in
combat_engine.pets. Every piece of combat UI read allies or party.members, so a
summon was a valid target that was never drawn, and the moment the targeting
code tried to locate one it did .index() on a list it was never in.

The crash case is the important one here: it is reachable from ordinary play
(have a pet out, cast any targeted heal, move the mouse) and it takes the whole
process down, so it gets a direct reproduction rather than a proxy.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        FAILS.append(label)
        print(f"  FAIL {label}  {detail}")


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    from entities.character import Character
    from entities.pet import Pet

    # ---- 1. the attribute that made a pet unrenderable -----------------------
    owner = Character("Kyle", "warlock", level=20)
    pet = Pet("Imp", "imp", owner)
    check("a pet reports .health like a party member does",
          getattr(pet, "health", None) == pet.max_health, f"{getattr(pet, 'health', None)}")
    pet.health = 999
    check("and writing it keeps both spellings the same number",
          pet.max_health == 999 and pet.health == 999)
    pet.health = pet.max_health = 539
    pet.current_health = 539

    # ---- 2. the crash, reproduced through the real screen -------------------
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    from ui.screens.combat_screen import CombatScreen

    party = Party(owner)

    from entities.monster import Monster
    foe = Monster("Target Dummy", "beast_basic", level=20)

    class _SM:
        pass
    sm = _SM()
    sm.player = owner
    sm.get_party = lambda: party
    sm.transition_to = lambda s: None
    sm.current_enemies = [foe]
    sm.current_enemy = foe

    engine = CombatEngine(owner, foe, enemies=[foe], party=party)
    engine.pets = [pet]
    engine.combatants = engine.allies + engine.pets + engine.enemies

    check("the engine calls the pet an ally", engine.is_ally(pet))
    check("but the pet is NOT in engine.allies - the mismatch that caused it",
          pet not in engine.allies)

    cs = CombatScreen.__new__(CombatScreen)
    cs.combat_engine = engine
    cs.targeting_valid_targets = engine.living_allies()
    cs.targeting_hovered = None
    cs._targeting_rects = []

    check("the pet is a valid heal target", pet in cs.targeting_valid_targets)

    # With nothing drawn yet, hovering anywhere must be a quiet miss, not a throw.
    try:
        got = cs._get_hovered_target((200, 200))
        ok = got is None
        err = ""
    except Exception as exc:  # noqa: BLE001 - the point is that nothing escapes
        ok, err = False, f"{type(exc).__name__}: {exc}"
    check("hovering before anything is drawn does not raise", ok, err)

    try:
        ok = cs._rect_for_combatant(pet) is None
        err = ""
    except Exception as exc:  # noqa: BLE001
        ok, err = False, f"{type(exc).__name__}: {exc}"
    check("asking for an undrawn pet's rect returns None instead of raising", ok, err)

    # ---- 3. once the overlay HAS drawn, the pet is findable -----------------
    pet_rect = pygame.Rect(40, 300, 400, 80)
    cs._targeting_rects = [(owner, pygame.Rect(40, 120, 400, 80)), (pet, pet_rect)]
    check("hovering the pet's drawn rect returns the pet",
          cs._get_hovered_target(pet_rect.center) is pet)
    check("and its rect is the one that was drawn",
          cs._rect_for_combatant(pet) == pet_rect)
    # Negative control: a point in no row must still return nothing.
    check("hovering empty space returns nothing",
          cs._get_hovered_target((900, 650)) is None)
    # A combatant that is drawn but NOT a valid target must not be hoverable.
    cs.targeting_valid_targets = [owner]
    check("a drawn but invalid target is not hoverable",
          cs._get_hovered_target(pet_rect.center) is None)

    # ---- 4. the pet is actually put on screen -------------------------------
    cs.renderer = __import__("ui.renderer", fromlist=["Renderer"]).Renderer()
    cs.state_manager = sm
    cs.hotbar_positions = []   # a bare screen has drawn no buttons yet
    drawn = []
    real_bar = cs.renderer.draw_health_bar
    cs.renderer.draw_health_bar = lambda *a, **k: (drawn.append(a), real_bar(*a, **k))[1]
    try:
        cs._draw_pet_chips(screen, pet)
        ok, err = len(drawn) == 1, ""
    except Exception as exc:  # noqa: BLE001
        ok, err = False, f"{type(exc).__name__}: {exc}"
    check("the pet chip row draws one health bar per living pet", ok, err or f"{len(drawn)} bars")

    pet.current_health = 0
    drawn.clear()
    cs._draw_pet_chips(screen, None)
    check("a dead pet is not drawn", not drawn)

    # ---- 5. a Necromancer's four, and worse ---------------------------------
    # Kyle: "will this work for necromancer who has many pets". The targeting
    # panel used to walk a fixed 90px per row from y=120, which fits six rows on
    # a 720px screen. Five party members hid that; a full party plus a
    # Necromancer's four minions is nine rows and the last three were drawn off
    # the bottom - valid targets with no pixels and no way to click them.
    for cls, cap in (("necromancer", 3), ("tinker", 2), ("witch_hunter", 2)):
        c = Character("T", cls, level=60)
        check(f"{cls} can actually summon its extra pets",
              c.max_extra_pets == cap, f"got {c.max_extra_pets}, want {cap}")

    # TWO pet owners in one party. Kyle: "what if there are 2 necros in a part".
    # combat_engine.pets is built by walking every ally's all_pets, so the real
    # question is whether the party, the engine and the panel agree about a
    # stable that belongs to more than one person.
    from entities.party import Party as _Party
    from combat.combat_engine import CombatEngine as _Engine
    from entities.monster import Monster as _Monster
    a = Character("Kyle", "necromancer", level=60)
    b = Character("Freja", "necromancer", level=60)
    p2 = _Party(a)
    p2.members.append(b)
    for owner in (a, b):
        owner.active_pet = Pet(f"{owner.name} Prime", "wolf", owner)
        owner.extra_pets = [Pet(f"{owner.name} M{k}", "raptor", owner)
                            for k in range(owner.max_extra_pets)]
    dummy = _Monster("D", "beast_basic", level=60)
    e2 = _Engine(a, dummy, enemies=[dummy], party=p2)
    check("two necromancers bring eight pets between them", len(e2.pets) == 8,
          f"{len(e2.pets)}")
    check("and they are credited to both owners",
          {p.owner.name for p in e2.pets} == {"Kyle", "Freja"})
    check("every one of them is an ally and a combatant",
          all(e2.is_ally(p) and p in e2.combatants for p in e2.pets))
    check("living_allies counts party plus every pet",
          len(e2.living_allies()) == len(p2.members) + 8,
          f"{len(e2.living_allies())}")

    for n in (1, 5, 9, 13, 25):
        rects = cs._target_row_rects(n, 40, 400)
        check(f"{n} target rows all fit on screen",
              len(rects) == n and max(r.bottom for r in rects) <= 720
              and min(r.height for r in rects) >= 36,
              f"bottom={max(r.bottom for r in rects)}, h={rects[0].height}")
        # No two rows may overlap, or one would steal the other's clicks.
        overlap = any(a.colliderect(b) for i, a in enumerate(rects) for b in rects[i + 1:])
        check(f"{n} target rows do not overlap", not overlap)

    print(f"\n{len(FAILS)} failed" if FAILS else "\npets survive the combat screen")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
