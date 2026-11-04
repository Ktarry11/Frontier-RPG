#!/usr/bin/env python3
"""Render a UI screen headlessly to a PNG, for before/after layout review.

Real pygame rendering against a real Character and Party - the point is to see
what the player sees, not an approximation of it. Stubs only the
GameStateManager, since the screens reach into it for the party and player and
nothing else during a render.

    python3 tools/shot_screen.py cast  /tmp/cast.png  [--class Primalist] [--level 1]
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402


def build(char_class="Primalist", level=1):
    from entities.character import Character
    from entities.party import Party
    player = Character("Hero", char_class, level)
    party = Party(player)
    return player, party


class StubSM:
    def __init__(self, player, party):
        self.player = player
        self._party = party
        self.states = {}
        self.current_state = None
        self.current_enemy = None
        self.current_enemies = []
        self.current_zone = None

    def get_party(self):
        return self._party

    def change_state(self, *a, **k):
        pass


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "cast"
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/screen.png"
    cls = "Primalist"
    lvl = 1
    if "--class" in sys.argv:
        cls = sys.argv[sys.argv.index("--class") + 1]
    if "--level" in sys.argv:
        lvl = int(sys.argv[sys.argv.index("--level") + 1])

    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    player, party = build(cls, lvl)
    sm = StubSM(player, party)

    if which == "cast":
        from ui.screens.cast_screen import CastScreen
        scr = CastScreen(sm)
        scr.selected_caster = player
    elif which.startswith("party"):
        from entities.character import Character as _C
        from ui.screens.party_screen import PartyScreen
        mate = _C("Mate", "Priest", max(1, lvl))
        party.add_member(mate)
        scr = PartyScreen(sm)
        scr.selected = mate
        if hasattr(scr, "selected_member"):
            scr.selected_member = mate
        if "_" in which:
            scr.tab = which.split("_", 1)[1]
    elif which in ("inventory", "inventory_discard", "inventory_confirm",
                   "inventory_companion"):
        from entities.loot_generator import LootGenerator
        from entities.loot_item import LootItem
        from ui.screens.inventory_screen import InventoryScreen
        gen = LootGenerator()
        for slot in ("chest", "legs", "head", "hands", "feet"):
            it = gen.generate_item_for_class(cls, max(1, lvl), slot=slot)
            if it is not None:
                player.inventory.append(it)
        player.inventory.append(LootItem("qi", "Sister Mollis's Ledger",
                                         category="quest", quest_id="q1"))
        scr = InventoryScreen(sm)
        if which == "inventory_companion":
            from entities.character import Character as _C2
            _mate = _C2("Mate", "Priest", max(1, lvl))
            party.add_member(_mate)
            scr.set_subject(_mate)
        else:
            scr.set_subject(player)
        if which == "inventory_discard":
            scr.discard_mode = True
        if which == "inventory_confirm":
            scr.pending_destroy_item = player.inventory[-1]
    elif which == "journal":
        # Real quests from the real manager - the point is to see the con
        # colours against a real spread of quest levels, which a stub cannot
        # give. Accepts a handful regardless of level gating so the list has
        # rows in several bands at once.
        from world.quest_manager import get_quest_manager
        from ui.screens.quest_journal_screen import QuestJournalScreen
        qm = get_quest_manager()
        picked = sorted(qm.quests.values(), key=lambda q: (q.quest_level, q.quest_id))
        spread = []
        for want in (lvl - 14, lvl - 6, lvl - 2, lvl, lvl + 3, lvl + 6):
            best = min(picked, key=lambda q: abs(q.quest_level - want), default=None)
            if best is not None and best not in spread:
                spread.append(best)
        from world.quest import QuestStatus
        for q in spread:
            q.status = QuestStatus.ACTIVE
        scr = QuestJournalScreen(sm)
    elif which == "combat":
        # Needs a real fight behind it, or the screen renders its "combat
        # over" scrim instead of the thing we want to look at.
        from entities.monster import Monster
        from ui.screens.combat_screen import CombatScreen
        sm.current_enemy = Monster("Mangy Wolf", "beast_basic", level=max(1, lvl))
        sm.current_enemies = [sm.current_enemy]
        sm.current_zone = None
        scr = CombatScreen(sm)
        scr._init_combat()
    else:
        raise SystemExit(f"unknown screen {which!r}")

    scr.render(surf)
    pygame.image.save(surf, out)
    print(f"wrote {out}  ({cls} lvl {lvl}, {SCREEN_WIDTH}x{SCREEN_HEIGHT})")
    pygame.quit()


if __name__ == "__main__":
    main()
