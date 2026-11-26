"""Friendship test panel: drive Kesten, Adrián and Tarek's friendship by hand and watch it move.

Kyle, 13 Nov 2026, on the recruit pilot: there was "no way to improve their relationship", and he
wanted a test panel for friendship. Open it from the party screen (the "Friendship Test" button,
or F9 there).

Everything here goes through world/bond_manager.py exactly the way the game does: the event
buttons call the same functions a quest turn-in, a dungeon, a wipe or a town arrival calls, on
your real party. So what you see here is what will happen in play, faster. "Reset friendship"
puts everyone back to strangers.

Wave 3 (Nov 2026) added what the recruits think of each other. With ninety-eight recruits the old
one-column-per-recruit layout was unreadable, so the columns now show only the recruits you have
with you (party and bench), a picker at the top brings anybody else along, and the Pairs panel
shows every pair in the party: how they get on, how many outings they've shared, their chemistry,
and how far through their signature arc they are. "10 outings" and "Next beat" speed things up,
and the log on the right is what they've said to each other.
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


#: the most recruit columns drawn at once (a full party plus the bench)
MAX_COLS = 5


class BondTestScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.close_button = pygame.Rect(SCREEN_WIDTH - 140, 20, 110, 40)
        self.reset_button = pygame.Rect(SCREEN_WIDTH - 330, 20, 170, 40)
        self.rects = []
        self.note = ""
        self.pick = 0             # which absent recruit the picker shows

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

    def _with_you(self):
        """Recruit ids in the party or on the bench, in party order."""
        party = self._party()
        out = []
        for m in getattr(party, "members", []) + getattr(party, "bench", []):
            rid = getattr(m, "recruit_id", None)
            if rid in self._bm().bonds and rid not in out:
                out.append(rid)
        return out

    def _absent(self):
        bm, here = self._bm(), set(self._with_you())
        return sorted((rid for rid in bm.bonds if rid not in here), key=bm.name_of)

    def _party_ids(self):
        party = self._party()
        return {getattr(m, "recruit_id", None) for m in getattr(party, "members", [])} & set(self._bm().bonds)

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
        elif key == "ten":
            for _ in range(10):
                bm.on_deed("dungeon", party, zone="Open road")
                bm.rel.queue.clear()
            self.note = "Ten outings"
            return
        elif key in ("group", "argue", "talk"):
            # the interactive party (world/group_dynamics.py, world/conversations.py)
            ids = self._party_ids()
            from world.conversations import get_conversations
            cv = get_conversations()
            if key == "group":
                if len(ids) < 3:
                    self.note = "Bring three recruits along for a group scene."
                    return
                bm.rel.groups.scene(ids, "outing")
                self.note = "Group scene"
            elif key == "argue":
                cv.pending_ask = None
                self.note = "Argument" if cv.start_argument(ids) else "No written argument for anyone here"
            else:
                import random as _r
                for rid in _r.sample(ids, len(ids)):
                    for kind, sub in (("aftermath", "wipe"), ("confrontation", "risks"), ("history", None),
                                      ("development", None), ("aftermath", "near_death")):
                        if cv.want(rid, kind, sub, force=True):
                            self.note = f"{bm.name_of(rid).split()[0]} wants a word ({kind})"
                            return
                self.note = "Nobody here has lines to talk to you yet"
            return
        elif key == "beat":
            ids = self._party_ids()
            if len(ids) < 2:
                self.note = "Bring two recruits along first."
                return
            bm.rel._sig_or_ambient(ids, 1.0)
            self.note = "Next beat"
            return
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
            if party.add_member(char) is None:
                self.note = "No room: the party and the bench are both full."
                return
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
                # nothing here shows the banter panel, so whatever they said is already in the log;
                # a beat left waiting would hold back the next one, so let it go
                self._bm().rel.queue.clear()
                if kind == "event":
                    self._event(key)
                elif kind == "pick":
                    n = max(1, len(self._absent()))
                    self.pick = (self.pick + (1 if key == "next" else -1)) % n
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
        for key, label in (("ten", "10 outings"), ("beat", "Next beat"), ("group", "Group scene"),
                           ("argue", "Argument"), ("talk", "Wants a word")):
            w = self.renderer.font_normal.size(label)[0] + 26
            if x + w > SCREEN_WIDTH - 30:
                x, y = 30, y + 44
            r = pygame.Rect(x, y, w, 36)
            self.renderer.draw_button(screen, r, label, color=(60, 70, 50))
            self.rects.append(("event", key, None, r))
            x += w + 8
        y += 44

        # the picker: anybody not with you, one at a time
        absent = self._absent()
        if absent:
            self.pick %= len(absent)
            rid = absent[self.pick]
            left, right = pygame.Rect(30, y, 36, 32), pygame.Rect(316, y, 36, 32)
            self.renderer.draw_button(screen, left, "<", color=COLOR_DARK_GRAY)
            self.renderer.draw_button(screen, right, ">", color=COLOR_DARK_GRAY)
            self.renderer.draw_text(screen, bm.name_of(rid), (76, y + 7), font_size=15, color=COLOR_WHITE)
            join = pygame.Rect(362, y, 130, 32)
            self.renderer.draw_button(screen, join, "Bring along")
            self.rects += [("pick", "prev", None, left), ("pick", "next", None, right),
                           ("per", "join", rid, join)]
            self.renderer.draw_text(screen, f"{len(absent)} others at home or away",
                                    (504, y + 8), font_size=14, color=(150, 150, 160))
        y += 44

        cols = self._with_you()[:MAX_COLS]
        col_w = (SCREEN_WIDTH - 60) // MAX_COLS
        panel_h = 250
        for i, rid in enumerate(cols):
            b = bm.bonds[rid]
            cx = 30 + i * col_w
            cy = y
            panel = pygame.Rect(cx, cy, col_w - 10, panel_h)
            self.renderer.draw_rect(screen, panel, (24, 24, 32))
            self.renderer.draw_rect(screen, panel, (80, 80, 95), fill=False)
            self.renderer.draw_text(screen, bm.name_of(rid), (cx + 8, cy + 6), font_size=15, color=COLOR_GOLD)
            nxt = THRESHOLDS[b.stage + 1] if b.stage + 1 < len(STAGES) else None
            where = ("with you" if self._member(rid) is not None else
                     f"away, {max(0, b.break_left):.1f} jobs to go" if b.away else "at home")
            rows = [
                f"{STAGE_NAMES[b.stage_key]}  ({b.trust:.0f}" + (f"/{nxt})" if nxt else ")"),
                f"Mood {b.mood:.0f}.  Trip {b.outings}/{b.stint_len}",
                f"Where: {where}",
                f"Wipes {b.wipes}.  Angry: {'yes' if b.angry else 'no'}",
                f"Gear missing: {', '.join(b.short) or 'none'}",
                f"Needs a talk: {'yes' if b.needs_talk else 'no'}",
            ]
            ry = cy + 30
            for row in rows:
                self._fit(screen, row, cx + 8, ry, col_w - 26, 13, COLOR_WHITE)
                ry += 18
            bx, by = cx + 8, ry + 6
            for key, label in PER:
                if key == "join":
                    continue
                w = self.renderer._get_font(font_size=13).size(label)[0] + 16
                if bx + w > panel.right - 6:
                    bx, by = cx + 8, by + 32
                r = pygame.Rect(bx, by, w, 28)
                self.renderer.draw_button(screen, r, label, color=COLOR_DARK_GRAY)
                self.rects.append(("per", key, rid, r))
                bx += w + 5
        if not cols:
            self.renderer.draw_text(screen, "Nobody's with you. Use the picker above to bring a recruit along.",
                                    (30, y + 10), font_size=15, color=(170, 170, 180))

        # what the recruits think of each other, and what they've said
        ly = y + panel_h + 12
        half = (SCREEN_WIDTH - 70) // 2
        self.renderer.draw_text(screen, "Pairs", (30, ly), color=(150, 200, 160))
        self.renderer.draw_text(screen, f"What they said{(': ' + self.note) if self.note else ''}",
                                (40 + half, ly), color=(150, 200, 160))
        ly += 24
        rm = bm.rel
        py = ly
        ids = [r for r in cols if r in self._party_ids()]
        pairs = rm.pairs_in(ids)
        for a, b2 in pairs:
            r = rm.rel(a, b2)
            sig = rm.sigs.get(rm.key(a, b2))
            arc = f", arc {r.sig_step}/{len(sig['steps'])}" if sig else ""
            line = (f"{bm.first_name(a) if hasattr(bm, 'first_name') else bm.name_of(a).split()[0]} & "
                    f"{bm.name_of(b2).split()[0]}: {r.state} ({r.affinity:.0f}), "
                    f"{r.outings} out, chem {rm.chem(a, b2, r.outings):+.1f}{arc}")
            self._fit(screen, line, 30, py, half, 13, (220, 220, 225))
            py += 18
            if py > SCREEN_HEIGHT - 16:
                break
        if not pairs:
            self.renderer.draw_text(screen, "Bring two or more recruits along to see how they get on.",
                                    (30, py), font_size=13, color=(150, 150, 160))
        # GROUPS (world/group_dynamics.py): the party's mood, crews and families, each person's role, how they
        # come across in this company, how they've grown, and what they make of you (world/conversations.py)
        if ids and py < SCREEN_HEIGHT - 60:
            py += 8
            self.renderer.draw_text(screen, "Groups", (30, py), color=(150, 200, 160))
            py += 22
            from world.conversations import get_conversations
            cv = get_conversations()
            rows = rm.groups.panel(ids) + [(bm.name_of(r).split()[0] + " on you", cv.describe_impression(r))
                                           for r in ids if rm.groups.has(r)]
            for label, text in rows:
                self._fit(screen, f"{label}: {text}", 30, py, half, 13, (220, 220, 225))
                py += 18
                if py > SCREEN_HEIGHT - 16:
                    break

        log = [(rid, t) for rid, t in rm.log] or list(bm.log)
        rows_left = max(1, (SCREEN_HEIGHT - 16 - ly) // 18)
        for rid, text in log[-rows_left:]:
            who = bm.name_of(rid).split()[0] if rid else "News"
            self._fit(screen, f"{who}: {text}", 40 + half, ly, half - 10, 13, (220, 220, 225))
            ly += 18

    def _fit(self, screen, text, x, y, width, size, color):
        """One line, cut to fit the width it's given, measured in the font it's drawn in."""
        font = self.renderer._get_font(font_size=size)
        if font.size(text)[0] > width:
            while text and font.size(text + "...")[0] > width:
                text = text[:-1]
            text = text.rstrip(" ,") + "..."
        self.renderer.draw_text(screen, text, (x, y), font_size=size, color=color)
