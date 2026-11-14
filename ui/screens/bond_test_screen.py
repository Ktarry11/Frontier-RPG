"""Friendship test panel: drive Kesten, Adrián and Tarek's friendship by hand and watch it move.

Kyle, 13 Nov 2026, on the recruit pilot: there was "no way to improve their relationship", and he
wanted a test panel for friendship. Open it from the party screen (the "Friendship Test" button,
or F9 there).

Everything here goes through world/bond_manager.py exactly the way the game does: the event
buttons call the same functions a quest turn-in, a dungeon, a wipe or a town arrival calls, on
your real party. So what you see here is what will happen in play, faster. "Reset friendship"
puts all three back to strangers.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_DARK_GRAY
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen

EVENTS = [
    ("quest", "Hand in a quest"),
    ("dungeon", "Finish a dungeon"),
    ("boss", "Kill a boss"),
    ("grind", "Kill 30 open-world mobs"),
    ("wipe", "Wipe at a dungeon door"),
    ("high", "Enter a zone 5 levels up"),
    ("town", "Arrive in a town"),
]
PER = [
    ("join", "Bring along"),
    ("home", "Send home"),
    ("take", "Take a gear piece"),
    ("give", "Give an upgrade"),
    ("trust", "Trust to next stage"),
    ("talk", "Talk"),
]


class _Dummy:
    """A stand-in enemy or zone for the event buttons."""
    def __init__(self, **kw):
        self.__dict__.update(kw)


class BondTestScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.close_button = pygame.Rect(SCREEN_WIDTH - 140, 20, 110, 40)
        self.reset_button = pygame.Rect(SCREEN_WIDTH - 330, 20, 170, 40)
        self.rects = []
        self.note = ""

    # ------------------------------------------------------------ helpers
    def _bm(self):
        from world.bond_manager import get_bond_manager
        return get_bond_manager()

    def _party(self):
        return self.state_manager.get_party()

    def _member(self, rid):
        party = self._party()
        return next((m for m in getattr(party, "members", []) + getattr(party, "bench", [])
                     if getattr(m, "recruit_id", None) == rid), None)

    def _event(self, key):
        bm, party = self._bm(), self._party()
        bm.party = party
        level = getattr(getattr(party, "player", None), "level", 10)
        if key == "quest":
            bm.on_deed("quest", party)
        elif key == "dungeon":
            bm.on_deed("dungeon", party, zone="Open road")
        elif key == "boss":
            bm.on_kills([_Dummy(name="Test Boss", is_boss=True, monster_type="humanoid")], party)
        elif key == "grind":
            bm.on_kills([_Dummy(name="Test Boar", is_boss=False, monster_type="beast")] * 30,
                        party, zone="Open road")
        elif key == "wipe":
            bm.on_wipe(party, at_dungeon_door=True)
        elif key == "high":
            zone = _Dummy(name="__test_high__", is_town=False)
            orig = bm._zone_level
            bm._zone_level = lambda z: level + 5 if getattr(z, "name", "") == "__test_high__" else orig(z)
            try:
                bm.on_zone(zone, party)
            finally:
                bm._zone_level = orig
        elif key == "town":
            bm.on_zone(_Dummy(name="Test Town", is_town=True), party)
        self.note = dict(EVENTS)[key]

    def _per(self, key, rid):
        from world.recruit_manager import get_recruit_manager
        bm, rm, party = self._bm(), get_recruit_manager(), self._party()
        b = bm.get(rid)
        member = self._member(rid)
        recruit = rm.recruits.get(rid)
        if key == "join":
            if member is not None or recruit is None:
                return
            if b.away:
                b.away = False
                b.break_left = 0
            hire = bm.hire_moment(rid)
            if hire is not None:
                bm.answer(rid, hire["id"], next(i for i, o in enumerate(hire["options"]) if o.get("joins")))
            bm.heard_walkout_talk(rid)
            char = rm.build_or_restore(recruit, getattr(party.player, "level", None))
            if char is None:
                self.note = rm.block_reason(recruit, getattr(party.player, "level", None)) or ""
                return
            party.add_member(char)
            rm.mark_recruited(rid)
            bm.on_joined(rid)
        elif key == "home":
            if member is not None:
                bm.depart(b, "stint")
                if self._member(rid) is not None:       # the first-goodbye question held him
                    self.note = "He wants a word first. Use Talk."
        elif key == "take":
            if member is None:
                return
            slot = next((s for s, it in member.equipment.slots.items() if it is not None
                         and s not in ("bag1", "bag2", "bag3", "bag4")), None)
            if slot is None:
                return
            member.last_refusal = None
            if not member.unequip_item(slot, into=party.player):
                self.note = getattr(member, "last_refusal", None) or "Bags full."
        elif key == "give":
            if member is not None:
                slot = b.short[0] if b.short else "chest"
                bm.on_gear_given(rid, slot, better=True)
        elif key == "trust":
            from world.bond_manager import THRESHOLDS, STAGES
            if b.stage + 1 < len(STAGES):
                if b.stage + 1 == len(STAGES) - 1 and "goal_done" not in b.flags:
                    b.flags.append("goal_done")         # stands in for the personal quest
                b.trust = THRESHOLDS[b.stage + 1]
                bm._trust(b, 0)
        elif key == "talk":
            if recruit is not None:
                self.state_manager.transition_to(GameState.RECRUIT_DIALOG, current_recruit_npc=recruit)

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_F9):
            self.state_manager.transition_to(GameState.PARTY)
            return
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.close_button.collidepoint(event.pos):
            self.state_manager.transition_to(GameState.PARTY)
            return
        if self.reset_button.collidepoint(event.pos):
            from world.bond_manager import Bond
            bm = self._bm()
            for rid, b in list(bm.bonds.items()):
                fresh = Bond(rid, b.data)
                fresh.in_party = self._member(rid) is not None
                if fresh.in_party:
                    fresh.stint_len = bm._stint_length(fresh)
                    fresh.stints = 1
                bm.bonds[rid] = fresh
            bm.pair_time, bm.pairs_heard, bm.log = {}, [], []
            self.note = "Friendship reset."
            return
        for kind, key, rid, rect in self.rects:
            if rect.collidepoint(event.pos):
                if kind == "event":
                    self._event(key)
                else:
                    self._per(key, rid)
                return

    # ------------------------------------------------------------ drawing
    def render(self, screen):
        from world.bond_manager import STAGE_NAMES, THRESHOLDS, STAGES
        screen.fill((12, 12, 18))
        self.rects = []
        bm = self._bm()
        self.renderer.draw_text(screen, "Friendship Test", (30, 24), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(screen, f"Outings so far: {bm.deeds}.  Events act on your real party.",
                                (30, 64), font_size=15, color=(170, 170, 180))
        self.renderer.draw_button(screen, self.reset_button, "Reset friendship")
        self.renderer.draw_button(screen, self.close_button, "Close")

        x, y = 30, 96
        for key, label in EVENTS:
            w = self.renderer.font_normal.size(label)[0] + 26
            if x + w > SCREEN_WIDTH - 30:
                x, y = 30, y + 44
            r = pygame.Rect(x, y, w, 36)
            self.renderer.draw_button(screen, r, label)
            self.rects.append(("event", key, None, r))
            x += w + 8
        y += 56

        col_w = (SCREEN_WIDTH - 60) // max(1, len(bm.bonds))
        for i, (rid, b) in enumerate(bm.bonds.items()):
            cx = 30 + i * col_w
            cy = y
            panel = pygame.Rect(cx, cy, col_w - 12, 330)
            self.renderer.draw_rect(screen, panel, (24, 24, 32))
            self.renderer.draw_rect(screen, panel, (80, 80, 95), fill=False)
            self.renderer.draw_text(screen, bm.name_of(rid), (cx + 10, cy + 8), color=COLOR_GOLD)
            nxt = THRESHOLDS[b.stage + 1] if b.stage + 1 < len(STAGES) else None
            where = ("with you" if self._member(rid) is not None else
                     f"away, back after {max(0, b.break_left)} outings" if b.away else "at home")
            rows = [
                f"{STAGE_NAMES[b.stage_key]}  (trust {b.trust:.0f}" + (f" of {nxt})" if nxt else ")"),
                f"Mood {b.mood:.0f}.  {bm.mood_line(rid) if b.in_party else ''}",
                f"Trip: {b.outings} of {b.stint_len} outings, {b.wipes} wipes",
                f"Where: {where}",
                f"Warned: {b.warned or 'no'}.  Leaving: {b.leave_cause or 'no'}",
                f"Gear missing: {', '.join(b.short) or 'none'}",
                f"Angry: {'yes' if b.angry else 'no'}.  Needs a talk: {'yes' if b.needs_talk else 'no'}",
                f"Moments done: {', '.join(b.moments_done) or 'none'}",
            ]
            ry = cy + 36
            for row in rows:
                self.renderer.draw_text(screen, row, (cx + 10, ry), font_size=14, color=COLOR_WHITE)
                ry += 20
            bx, by = cx + 10, ry + 8
            for key, label in PER:
                w = self.renderer.font_normal.size(label)[0] + 18
                if bx + w > panel.right - 8:
                    bx, by = cx + 10, by + 38
                r = pygame.Rect(bx, by, w, 32)
                self.renderer.draw_button(screen, r, label, color=COLOR_DARK_GRAY)
                self.rects.append(("per", key, rid, r))
                bx += w + 6

        ly = y + 344
        self.renderer.draw_text(screen, f"What they said{(': ' + self.note) if self.note else ''}",
                                (30, ly), color=(150, 200, 160))
        ly += 26
        for rid, text in bm.log[-9:]:
            who = bm.name_of(rid) if rid else "News"
            line = f"{who}: {text}"
            max_chars = max(40, (SCREEN_WIDTH - 60) // 8)
            if len(line) > max_chars:
                line = line[:max_chars - 3] + "..."
            self.renderer.draw_text(screen, line, (30, ly), font_size=14, color=(220, 220, 225))
            ly += 20
            if ly > SCREEN_HEIGHT - 20:
                break
