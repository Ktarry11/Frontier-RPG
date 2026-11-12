"""
Eat and Drink buttons on the overworld HUD feed the whole party in one press.

Kyle, 12 Nov: food and water on the hotbar "isnt useable in combat (correct) but clicking it
removes it... can we bind food/drink to another use tab somehow?"

With the real overworld screen, a player and three companions, and real food in the bags:
  1. the two buttons are drawn, inside the screen, not on top of Mount or Hearth
  2. Eat: everyone who is hurt starts eating; nobody at full health does; one item each
  3. each takes the BEST food they are high enough level for - a level 12 does not eat the
     level 38 ribs, and does not go hungry because the ribs are first in the list
  4. Drink: only characters with a mana bar who are short of mana
  5. the health and mana actually arrive as time passes
  6. pressing again while eating does nothing more (no double-dipping the stack)
  7. no food -> says so, nothing changes; everyone full -> says so, nothing is used
  8. the F and Q keys do the same as the buttons
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pygame  # noqa: E402

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager, GameState
    from entities.character import Character
    from entities.consumable_manager import get_consumable_manager
    from ui.screens.overworld_screen import OverworldScreen

    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=40)
    ow = sm.states.get(GameState.OVERWORLD) or OverworldScreen(sm)
    if hasattr(ow, "on_enter"):
        ow.on_enter()
    party = sm.get_party()
    mage = Character(name="Mira", char_class="Mage", level=40)
    priest = Character(name="Pell", char_class="Priest", level=12)
    rogue = Character(name="Rook", char_class="Rogue", level=40)
    for m in (mage, priest, rogue):
        party.add_member(m) if hasattr(party, "add_member") else party.members.append(m)
    everyone = ow._rest_party()
    check(len(everyone) == 4, f"rig: party of {len(everyone)}, wanted 4")

    cm = get_consumable_manager()
    sm.player.consumables = [
        cm.get_consumable("meal_kodo_ribs", 5),       # level 38, best
        cm.get_consumable("meal_trailbread", 5),      # level 10
        cm.get_consumable("drink_birch_wine", 5),     # level 38
        cm.get_consumable("drink_barley_beer", 5),    # level 10
    ]
    stock = {c.consumable_id: c for c in sm.player.consumables}

    def qty(cid):
        return stock[cid].quantity

    notes = []
    real_notify = ow._notify
    ow._notify = lambda text, *a, **k: (notes.append(text), real_notify(text, *a, **k))[1]

    # 1 ------------------------------------------------------------------------------------
    ow.render(screen)
    rects = {n: getattr(ow, n, None) for n in ("mount_button_rect", "hearth_button_rect", "eat_button_rect", "drink_button_rect")}
    for n, r in rects.items():
        if check(r is not None, f"{n} is not drawn"):
            check(screen.get_rect().contains(r), f"{n} {tuple(r)} is off screen")
    names = list(rects)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if rects[a] and rects[b]:
                check(not rects[a].colliderect(rects[b]), f"{a} overlaps {b}")

    # 7a. everyone full
    for m in everyone:
        m.current_health = m.health
        m.current_mana = m.mana
    before = {k: c.quantity for k, c in stock.items()}
    check(ow._rest("meal") == 0 and {k: c.quantity for k, c in stock.items()} == before,
          "Eat with everyone at full health used food")
    check(notes and "full health" in notes[-1], f"Eat at full health should say so; said {notes[-1:] }")

    # 2 + 3 --------------------------------------------------------------------------------
    sm.player.current_health = sm.player.health // 2
    priest.current_health = priest.health // 2
    rogue.current_health = rogue.health                       # full: must not eat
    mage.current_health = mage.health // 2
    hp_before = {m.name: m.current_health for m in everyone}
    fed = ow._rest("meal")
    check(fed == 3, f"three are hurt; {fed} ate")
    eating = {m.name: [n for k, n, _l in m.consumable_regen_active() if k == "meal"] for m in everyone}
    check(eating["Hero"] == ["Kodo Rib Roast"], f"Hero (40) should eat the ribs: {eating['Hero']}")
    check(eating["Pell"] and eating["Pell"] == ["Dried Trailbread"], f"Pell (12) should eat the level 10 food: {eating['Pell']}")
    check(not eating["Rook"], f"Rook is at full health and is eating {eating['Rook']}")
    check(qty("meal_kodo_ribs") == 3 and qty("meal_trailbread") == 4,
          f"expected 2 ribs and 1 bread used; ribs {qty('meal_kodo_ribs')}/5, bread {qty('meal_trailbread')}/5")

    # 6. again while eating
    snap = {k: c.quantity for k, c in stock.items()}
    ow._rest("meal")
    check({k: c.quantity for k, c in stock.items()} == snap, "pressing Eat again while eating used more food")

    # 4 ------------------------------------------------------------------------------------
    mage.current_mana = mage.mana // 3
    priest.current_mana = priest.mana // 3
    drank = ow._rest("drink")
    check(drank == 2, f"two casters are short of mana; {drank} drank")
    for m in (sm.player, rogue):
        check(not [1 for k, _n, _l in m.consumable_regen_active() if k == "drink"], f"{m.name} has no mana bar and is drinking")
    check(qty("drink_birch_wine") == 4 and qty("drink_barley_beer") == 4,
          f"expected one wine and one beer used; wine {qty('drink_birch_wine')}/5, beer {qty('drink_barley_beer')}/5")

    # 5 ------------------------------------------------------------------------------------
    mana_before = mage.current_mana
    for _ in range(40):
        ow.update(0.5)
    check(sm.player.current_health > hp_before["Hero"], "Hero ate and gained no health")
    check(priest.current_health > hp_before["Pell"], "Pell ate and gained no health")
    check(mage.current_mana > mana_before, "Mira drank and gained no mana")

    # 8 ------------------------------------------------------------------------------------
    for m in everyone:
        m.break_consumable_regen()
    rogue.current_health = rogue.health // 2
    snap = qty("meal_kodo_ribs")
    ow.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f, mod=0, unicode="f"))
    check(qty("meal_kodo_ribs") < snap, "the F key does not eat")
    mage.current_mana = 1
    snap = qty("drink_birch_wine")
    ow.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, mod=0, unicode="q"))
    check(qty("drink_birch_wine") < snap, "the Q key does not drink")
    for m in everyone:
        m.break_consumable_regen()
    sm.player.current_health = 1
    snap = sum(c.quantity for c in sm.player.consumables)
    ow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=ow.eat_button_rect.center, button=1))
    check(sum(c.quantity for c in sm.player.consumables) < snap, "clicking the Eat button does not eat")

    # 7b. no food
    sm.player.consumables = []
    for m in everyone:
        m.break_consumable_regen()
    check(ow._rest("meal") == 0 and "no food" in notes[-1], f"Eat with empty bags should say so; said {notes[-1:]}")

    if "--shot" in sys.argv:
        sm.player.consumables = [cm.get_consumable("meal_kodo_ribs", 12), cm.get_consumable("drink_birch_wine", 7)]
        ow.render(screen)
        pygame.image.save(screen, sys.argv[sys.argv.index("--shot") + 1])

    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("eat / drink buttons OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
