"""
Party management screen (P from the overworld).

This completes the party system. Companions could previously be recruited
but nothing could be done with them afterwards - no row swapping, no
benching, no gearing, no talent spending. They were frozen in whatever
starter kit they arrived in.

Layout:
  LEFT   - the roster. Active party (max 5, player pinned at the top) above
           the bench. Click anyone to select them.
  RIGHT  - the selected member's detail panel: stats, equipment summary,
           backstory, and the action buttons that operate on them.

Actions available on the selected member:
  Front/Back   - move between rows (applies ROW_DAMAGE_MODIFIERS in combat)
  Bench/Active - swap between the active five and the bench
  Gear         - open the inventory screen bound to THAT character
  Talents      - open the talent screen bound to THAT character, spec-locked
  Dismiss      - remove a companion permanently (confirm-gated)

The player can never be benched, dismissed, or removed from the roster; the
guards for that live in Party itself, and this screen simply hides the
buttons so you don't get a dead click.
"""
import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_DARK_GRAY, COLOR_GOLD, COLOR_GREEN, COLOR_RED,
    COLOR_BLUE, COLOR_YELLOW,
)
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.recruit_portrait import get_recruit_portrait, get_recruit_face
from entities.party import FRONT_ROW, BACK_ROW, MAX_PARTY_SIZE, BENCH_XP_RATIO


ROSTER_X = 20
ROSTER_Y = 90
ROW_H = 62
ROSTER_W = 400
FACE = 48

DETAIL_X = 430
DETAIL_Y = 90

COLOR_PANEL = (38, 38, 46)
COLOR_PANEL_SEL = (72, 66, 42)
COLOR_MUTED = (150, 150, 160)
COLOR_HEADER = (200, 200, 110)


class PartyScreen(BaseScreen):
    """Roster management: rows, bench, gearing, talents."""

    def __init__(self, state_manager):
        super().__init__(state_manager)

        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)

        # Selection is stored as the Character object, not an index, because
        # benching reorders both lists - an index would silently point at a
        # different person after every action.
        self.selected = None

        # Dismiss is destructive and irreversible (the recruit is marked as
        # taken, so they do not reappear in the world), hence a confirm step.
        self.confirm_dismiss = False

        self.message = None
        self.message_timer = 0.0

        # Asher Coleman's dismiss-refusal line (see the "dismiss" action
        # handler below) - separate from self.message since it's a longer
        # in-character quote needing its own wrapped, warmer-toned render,
        # not the short green status-toast self.message is built for.
        self.asher_refusal_line = None
        self.asher_refusal_timer = 0.0

        # Rebuilt every render so hit-testing always matches what's drawn.
        self.member_rects = []   # [(character, rect), ...]
        self.action_rects = []   # [(action_name, rect), ...]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _party(self):
        return self.state_manager.get_party()

    def _notify(self, text):
        self.message = text
        self.message_timer = 3.0

    def _is_player(self, character):
        party = self._party()
        return party is not None and character is party.player

    def _ensure_selection(self):
        """
        Keep the selection valid. Defaults to the player, and falls back to
        the player if the selected companion was just dismissed.
        """
        party = self._party()
        if party is None:
            self.selected = None
            return
        roster = party.members + party.bench
        if self.selected not in roster:
            self.selected = party.player
            self.confirm_dismiss = False

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _toggle_row(self, character):
        party = self._party()
        current = getattr(character, "row", FRONT_ROW)
        new_row = BACK_ROW if current == FRONT_ROW else FRONT_ROW
        party.set_row(character, new_row)
        self._notify(f"{character.name} moved to the {new_row} row.")

    def _toggle_bench(self, character):
        party = self._party()
        if character in party.members:
            if party.bench_member(character):
                self._notify(f"{character.name} moved to the bench "
                             f"({int(BENCH_XP_RATIO * 100)}% XP).")
        else:
            if party.activate_member(character):
                self._notify(f"{character.name} joined the active party.")
            else:
                self._notify(f"Active party is full ({MAX_PARTY_SIZE}).")

    def _open_gear(self, character):
        """Open the inventory screen bound to this character. Each
        character owns their own persistent inventory now, but gearing a
        companion still equips FROM the player's bag (per Kyle: keep that
        flow for now) - see InventoryScreen._bag_source for the split."""
        inventory = self.state_manager.states.get(GameState.INVENTORY)
        if inventory is None:
            return
        inventory.set_subject(character, return_state=GameState.PARTY)
        self.state_manager.transition_to(GameState.INVENTORY)

    def _open_talents(self, character):
        talent_screen = self.state_manager.states.get(GameState.TALENTS)
        if talent_screen is None:
            return
        talent_screen.character = character
        talent_screen.return_state = GameState.PARTY

        # Open on the locked tree for companions so they land where they can
        # actually spend, rather than on a greyed-out tree they'll have to
        # click off of.
        locked = getattr(character, "locked_spec", None)
        trees = list(character.talent_trees.keys())
        if locked and locked in character.talent_trees:
            talent_screen.set_current_tree(locked)
        elif trees:
            talent_screen.set_current_tree(trees[0])
        self.state_manager.transition_to(GameState.TALENTS)

    def _open_skills(self, character):
        """Open the skills/hotbar screen bound to this character - same
        set_subject() handoff as _open_gear, but each companion's
        ability_book/hotbar is entirely their own with no player handoff
        involved at all (unlike gear, which still equips from the
        player's bag - see InventoryScreen._bag_source)."""
        skills = self.state_manager.states.get(GameState.SKILLS)
        if skills is None:
            return
        skills.set_subject(character, return_state=GameState.PARTY)
        self.state_manager.transition_to(GameState.SKILLS)

    def _open_background(self, character):
        """Open the 4-tab Before/Adjustment/Now/Looking Forward lore
        screen for this character - same set_subject() handoff pattern
        as gear/talents/skills above."""
        background = self.state_manager.states.get(GameState.BACKGROUND)
        if background is None:
            return
        background.set_subject(character, return_state=GameState.PARTY)
        self.state_manager.transition_to(GameState.BACKGROUND)

    def _dismiss(self, character):
        """
        Send a companion home. They are NOT deleted - their full state is
        snapshotted and they can be re-hired in their home town at the exact
        level and gear they left with.

        Asher Coleman is the one exception (Kyle, 2026-09-09: "we can't
        remove him from the party" / "if we try to remove him, he won't
        let us? 'slightly' pushy - but not too much"): this method simply
        refuses to act on him, same enforcement pattern as his locked gear/
        talents (see entities/character.py's equip_item/unequip_item and
        ui/screens/talent_tree_screen.py's is_tree_locked) - a hard block
        at the real mutation point, not just a hidden/disabled button. The
        actual in-character refusal line is shown earlier, at the point
        the player first clicks Dismiss - see _handle_dismiss_click.
        """
        from world.recruit_manager import get_recruit_manager

        party = self._party()
        if self._is_player(character):
            return
        if getattr(character, "recruit_id", None) == "asher_coleman":
            return

        recruit = get_recruit_manager().dismiss(character)
        if party.remove_member(character):
            if recruit is not None and recruit.has_home():
                self._notify(f"{character.name} departs for {recruit.home_town}.")
            else:
                self._notify(f"{character.name} has left the party.")
            self.selected = party.player
        self.confirm_dismiss = False

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        mouse_pos = event.pos

        if self.close_button.collidepoint(mouse_pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        for character, rect in self.member_rects:
            if rect.collidepoint(mouse_pos):
                if character is not self.selected:
                    self.confirm_dismiss = False
                self.selected = character
                return

        for action, rect in self.action_rects:
            if not rect.collidepoint(mouse_pos):
                continue
            target = self.selected
            if target is None:
                return
            if action == "row":
                self._toggle_row(target)
            elif action == "bench":
                self._toggle_bench(target)
            elif action == "gear":
                self._open_gear(target)
            elif action == "talents":
                self._open_talents(target)
            elif action == "skills":
                self._open_skills(target)
            elif action == "background":
                self._open_background(target)
            elif action == "dismiss":
                if getattr(target, "recruit_id", None) == "asher_coleman":
                    # Kyle: "if we try to remove him, he won't let us? -
                    # 'slightly' pushy - but not too much. We still want
                    # him likeable." One warm, firm line in his own voice -
                    # no confirm dialog at all, since there's nothing to
                    # confirm; the button simply doesn't do what it does
                    # for anyone else. Never escalates on repeat clicks
                    # (no "he's getting annoyed" ramp) - same easy warmth
                    # every time, matching how the character profile says
                    # he should never read as strained or defensive about
                    # anything. Uses its own field (self.asher_refusal_line)
                    # rather than self._notify()/self.message, which is a
                    # single short line hardcoded to COLOR_GREEN elsewhere
                    # in this screen - this is a longer in-character quote
                    # that needs its own wrapped rendering and a warmer,
                    # parchment-gold tone to read as dialogue, not a status
                    # toast.
                    self.asher_refusal_line = (
                        "\"Now hold on, brother.\" Asher doesn't move. "
                        "\"Real people got to stick together out here. "
                        "I'm not going anywhere just yet.\""
                    )
                    self.asher_refusal_timer = 4.5
                    self.confirm_dismiss = False
                elif self.confirm_dismiss:
                    self._dismiss(target)
                else:
                    self.confirm_dismiss = True
            elif action == "cancel":
                self.confirm_dismiss = False
            return

    def update(self, dt):
        self._ensure_selection()
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None
        if self.asher_refusal_timer > 0:
            self.asher_refusal_timer -= dt
            if self.asher_refusal_timer <= 0:
                self.asher_refusal_line = None

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen):
        self._ensure_selection()
        party = self._party()

        self.renderer.draw_text(screen, "PARTY", (20, 20),
                                size="large", color=COLOR_GOLD)
        self.renderer.draw_button(screen, self.close_button, "Close")

        if party is None:
            self.renderer.draw_text(screen, "No party.", (ROSTER_X, ROSTER_Y))
            return

        self._render_roster(screen, party)
        self._render_detail(screen, party)

        hint = ("Click a member to select | Rows change incoming damage | "
                f"Benched members earn {int(BENCH_XP_RATIO * 100)}% XP | "
                "ESC or P to close")
        self.renderer.draw_text(screen, hint, (20, SCREEN_HEIGHT - 34),
                                font_size=14, color=COLOR_MUTED)

        if self.message:
            self.renderer.draw_text(screen, self.message,
                                    (DETAIL_X, SCREEN_HEIGHT - 70),
                                    color=COLOR_GREEN)

        if self.asher_refusal_line:
            # Warm parchment-gold, not the green status-toast color - this
            # is dialogue, not a system message. Drawn above the hint bar
            # with generous width since it's a full quoted line, not a
            # short status string.
            self._draw_wrapped(screen, self.asher_refusal_line,
                               DETAIL_X, SCREEN_HEIGHT - 110,
                               max_width=SCREEN_WIDTH - DETAIL_X - 40,
                               color=(210, 190, 140))

    def _render_roster(self, screen, party):
        self.member_rects = []
        y = ROSTER_Y

        self.renderer.draw_text(
            screen, f"Active Party ({len(party.members)}/{MAX_PARTY_SIZE})",
            (ROSTER_X, y), color=COLOR_HEADER)
        y += 28

        for member in party.members:
            y = self._render_member_row(screen, member, y, party, benched=False)

        y += 14
        self.renderer.draw_text(screen, f"Bench ({len(party.bench)})",
                                (ROSTER_X, y), color=COLOR_HEADER)
        y += 28

        if not party.bench:
            self.renderer.draw_text(screen, "Nobody benched.", (ROSTER_X + 8, y),
                                    font_size=14, color=COLOR_MUTED)
        for member in party.bench:
            y = self._render_member_row(screen, member, y, party, benched=True)

    def _render_member_row(self, screen, member, y, party, benched):
        rect = pygame.Rect(ROSTER_X, y, ROSTER_W, ROW_H - 6)
        selected = member is self.selected
        self.renderer.draw_rect(screen, rect,
                                COLOR_PANEL_SEL if selected else COLOR_PANEL)
        self.renderer.draw_rect(screen, rect,
                                COLOR_GOLD if selected else (70, 70, 80),
                                fill=False)

        # Portrait slot: the recruit's face, or an empty frame for the hero (no portrait yet).
        frame = pygame.Rect(rect.x + 4, rect.y + (rect.height - FACE) // 2, FACE, FACE)
        self.renderer.draw_rect(screen, frame, (22, 22, 28))
        face = get_recruit_face(getattr(member, "recruit_id", None), FACE)
        if face is not None:
            if benched:
                face = face.copy()
                face.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(face, frame)
        self.renderer.draw_rect(screen, frame, COLOR_GOLD if member is party.player else (95, 95, 108), fill=False)
        tx = frame.right + 10

        row_tag = "F" if getattr(member, "row", FRONT_ROW) == FRONT_ROW else "B"
        name_color = COLOR_GOLD if member is party.player else COLOR_WHITE
        if benched:
            name_color = COLOR_MUTED

        label = f"[{row_tag}] {member.name}"
        if member is party.player:
            label += "  (you)"
        self.renderer.draw_text(screen, label, (tx, rect.y + 6),
                                color=name_color)

        sub = f"Lv {member.level} {member.char_class}"
        locked = getattr(member, "locked_spec", None)
        if locked:
            sub += f" - {self._spec_label(member, locked)}"
        self.renderer.draw_text(screen, sub, (tx, rect.y + 30),
                                font_size=14, color=COLOR_MUTED)

        # HP bar on the right of the row so you can see who came out of the
        # last fight hurt without opening each member individually.
        self.renderer.draw_health_bar(
            screen, (rect.right - 130, rect.y + 20),
            member.current_health, member.health,
            width=120, height=14, bar_color=COLOR_GREEN)

        self.member_rects.append((member, rect))
        return y + ROW_H

    @staticmethod
    def _spec_label(member, tree_id):
        """Human-readable spec name for a tree_id, e.g. 'Holy'."""
        tree = member.talent_trees.get(tree_id)
        if tree is not None:
            # spec_name is stored as "Priest Holy"; drop the class prefix.
            parts = tree.spec_name.split(" ", 1)
            return parts[1] if len(parts) > 1 else tree.spec_name
        return tree_id.replace("_", " ").title()

    #: Colors for the two effect kinds, matching how buffs/debuffs already
    #: read elsewhere in the UI (green = good for you, red = not).
    _BUFF_COLOR = (150, 205, 150)
    _DEBUFF_COLOR = (215, 120, 120)

    def _render_active_effects(self, screen, member, x, y, panel):
        """Current buffs and debuffs on this member, with time remaining.

        Kyle: "the party screen here would be a good place to have current
        buffs!" - and it is the natural home for them, because this is the
        screen you open to check on somebody between fights, which is exactly
        when you want to know whether their Fortitude is still up.

        Filtered to BUFF/DEBUFF the same way the Cast screen's roster already
        filters, so the two screens agree on what counts as a "buff". DOT and
        HOT effects are deliberately excluded: they are combat bookkeeping
        rather than a status you track out here.

        Durations come in two flavours and both have to read correctly. A
        turn-based effect stores whole turns in `duration`; a "raid" scope
        buff (Fortitude, Mark of the Wild) stores wall-clock seconds in
        `real_time_seconds` and ignores `duration` entirely - showing its raw
        `duration` would print a meaningless number, which is the trap
        get_effects_summary falls into by flattening both into one field.
        """
        from combat.status_effects import EffectType

        effects = [e for e in member._effects()
                   if e.effect_type in (EffectType.BUFF, EffectType.DEBUFF)]

        self.renderer.draw_text(screen, "ACTIVE EFFECTS", (x, y),
                                font_size=14, color=COLOR_GOLD)
        y += 24

        if not effects:
            self.renderer.draw_text(screen, "None", (x, y),
                                    font_size=14, color=COLOR_MUTED)
            return y + 26

        # Cap the list so a heavily-buffed character cannot push the action
        # buttons off the bottom of the panel - the same reason the backstory
        # below is truncated rather than wrapped forever.
        MAX_ROWS = 5
        for effect in effects[:MAX_ROWS]:
            is_buff = effect.effect_type == EffectType.BUFF
            color = self._BUFF_COLOR if is_buff else self._DEBUFF_COLOR

            label = effect.name
            stacks = getattr(effect, "stacks", 1)
            if stacks > 1:
                label += f" x{stacks}"

            secs = getattr(effect, "real_time_seconds", None)
            if secs is not None:
                remaining = (f"{int(secs // 60)}m" if secs >= 60
                             else f"{max(0, int(secs))}s")
            else:
                turns = max(0, int(getattr(effect, "duration", 0)))
                remaining = f"{turns}t"

            self.renderer.draw_text(screen, label, (x, y), font_size=14, color=color)
            rem_w = self.renderer._get_font(font_size=13).size(remaining)[0]
            self.renderer.draw_text(screen, remaining,
                                    (x + panel.width - 32 - rem_w, y + 1),
                                    font_size=13, color=COLOR_MUTED)
            y += 22

        if len(effects) > MAX_ROWS:
            self.renderer.draw_text(screen, f"+{len(effects) - MAX_ROWS} more",
                                    (x, y), font_size=13, color=COLOR_MUTED)
            y += 22

        return y + 8

    def _render_detail(self, screen, party):
        self.action_rects = []
        member = self.selected
        if member is None:
            return

        panel = pygame.Rect(DETAIL_X, DETAIL_Y,
                            SCREEN_WIDTH - DETAIL_X - 20, SCREEN_HEIGHT - DETAIL_Y - 60)
        self.renderer.draw_rect(screen, panel, COLOR_PANEL)
        self.renderer.draw_rect(screen, panel, (80, 80, 90), fill=False)

        x = panel.x + 16
        y = panel.y + 14

        # Recruit portrait (top-right of the panel); the player has none.
        portrait = get_recruit_portrait(getattr(member, "recruit_id", None), 130)
        pw = portrait.get_width() if portrait is not None else 118
        pframe = pygame.Rect(panel.right - pw - 14, panel.y + 10, pw, 130)
        self.renderer.draw_rect(screen, pframe, (22, 22, 28))
        if portrait is not None:
            screen.blit(portrait, pframe)
        self.renderer.draw_rect(screen, pframe, COLOR_GOLD if member is party.player else (95, 95, 108), fill=False)

        self.renderer.draw_text(screen, member.name, (x, y),
                                size="large", color=COLOR_GOLD)
        y += 38

        locked = getattr(member, "locked_spec", None)
        spec_text = f" - {self._spec_label(member, locked)} (locked)" if locked else ""
        self.renderer.draw_text(
            screen, f"Level {member.level} {member.char_class}{spec_text}", (x, y))
        y += 26

        row = getattr(member, "row", FRONT_ROW)
        status = "Active" if member in party.members else "Benched"
        self.renderer.draw_text(
            screen, f"{status}  |  {row.capitalize()} row", (x, y),
            color=COLOR_MUTED)
        y += 32

        # Resources
        self.renderer.draw_text(screen, f"HP  {member.display_health}/{round(member.health)}",
                                (x, y))
        self.renderer.draw_health_bar(screen, (x + 200, y), member.current_health,
                                      member.health, width=180, height=16,
                                      bar_color=COLOR_GREEN)
        y += 28
        y = self._render_resource(screen, member, x, y)
        y += 12

        # Core stats, two per line to keep the panel compact.
        stats = [
            ("STR", member.strength), ("AGI", member.agility),
            ("STA", member.stamina), ("INT", member.intellect),
            ("SPI", member.spirit), ("ARMOR", getattr(member, "armor", 0)),
        ]
        for i in range(0, len(stats), 2):
            line = "   ".join(f"{n}: {v}" for n, v in stats[i:i + 2])
            self.renderer.draw_text(screen, line, (x, y), font_size=14)
            y += 22
        y += 10

        points = getattr(member, "talent_points_available", 0)
        point_color = COLOR_GOLD if points else COLOR_MUTED
        self.renderer.draw_text(screen, f"Unspent talent points: {points}",
                                (x, y), font_size=14, color=point_color)
        y += 26

        equipped = sum(1 for slot in member.equipment.to_dict().values() if slot)
        self.renderer.draw_text(screen, f"Equipped items: {equipped}",
                                (x, y), font_size=14, color=COLOR_MUTED)
        y += 30

        y = self._render_active_effects(screen, member, x, y, panel)

        backstory = getattr(member, "backstory", "")
        if backstory:
            # Wrap backstory but cap the height so it doesn't overflow the panel.
            # Draw at most 4 lines (80px worth) before the action buttons.
            backstory_start = y
            y = self._draw_wrapped(screen, backstory, x, y,
                                   panel.width - 32, color=(170, 170, 185))
            # If backstory exceeded ~80px, truncate it and add ellipsis hint
            if y > backstory_start + 85:
                y = backstory_start + 85
                self.renderer.draw_text(screen, "...",
                                        (x, y - 20), font_size=14,
                                        color=(170, 170, 185))
            y += 10

        self._render_actions(screen, member, party, panel, y)

    def _render_resource(self, screen, member, x, y):
        """Draw the member's class resource bar under their HP."""
        from combat.abilities import get_class_resource, ResourceType

        resource = get_class_resource(member.char_class)
        options = [
            (ResourceType.MANA, "Mana", member.current_mana, member.mana, COLOR_BLUE),
            (ResourceType.RAGE, "Rage", member.current_rage, member.max_rage, COLOR_RED),
            (ResourceType.ENERGY, "Energy", member.current_energy,
             member.max_energy, COLOR_YELLOW),
        ]
        for res_type, label, current, maximum, color in options:
            if resource == res_type and maximum:
                self.renderer.draw_text(
                    screen, f"{label}  {round(current)}/{round(maximum)}", (x, y))
                self.renderer.draw_health_bar(
                    screen, (x + 200, y), current, maximum,
                    width=180, height=16, bar_color=color)
                return y + 28
        return y

    def _draw_wrapped(self, screen, text, x, y, max_width, color=COLOR_WHITE):
        """Naive word wrap - the backstories are a few sentences at most.

        Measures with the SAME 14px font draw_text actually renders with
        below (font_size=14) - previously measured against font_normal
        (20px) while drawing with what silently resolved to font_large
        (40px, since size="small" was never a real recognized value -
        see draw_text/_get_font), so lines were far too long for what
        actually got drawn and ran straight off the panel's edge.
        """
        font = self.renderer._get_font(font_size=14)
        words = text.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] > max_width and line:
                self.renderer.draw_text(screen, line, (x, y), font_size=14, color=color)
                y += 18
                line = word
            else:
                line = candidate
        if line:
            self.renderer.draw_text(screen, line, (x, y), font_size=14, color=color)
            y += 18
        return y

    def _render_actions(self, screen, member, party, panel, y):
        """Action buttons, laid out from the bottom of the detail panel up."""
        is_player = member is party.player
        btn_w, btn_h, gap = 150, 42, 10

        buttons = []
        row = getattr(member, "row", FRONT_ROW)
        buttons.append(("row", "To Back" if row == FRONT_ROW else "To Front"))
        buttons.append(("gear", "Gear"))
        buttons.append(("talents", "Talents"))
        buttons.append(("skills", "Skills"))
        buttons.append(("background", "Background"))
        if not is_player:
            buttons.append(
                ("bench", "Bench" if member in party.members else "Activate"))
            if self.confirm_dismiss:
                buttons.append(("dismiss", "Confirm!"))
                buttons.append(("cancel", "Cancel"))
            else:
                buttons.append(("dismiss", "Dismiss"))

        start_y = max(y + 10, panel.bottom - 110)
        col_x = panel.x + 16
        cur_x, cur_y = col_x, start_y
        for action, label in buttons:
            if cur_x + btn_w > panel.right - 16:
                cur_x = col_x
                cur_y += btn_h + gap
            rect = pygame.Rect(cur_x, cur_y, btn_w, btn_h)
            color = COLOR_RED if action == "dismiss" and self.confirm_dismiss \
                else COLOR_DARK_GRAY
            self.renderer.draw_button(screen, rect, label, color=color)
            self.action_rects.append((action, rect))
            cur_x += btn_w + gap

        if self.confirm_dismiss:
            from world.recruit_manager import get_recruit_manager
            recruit = get_recruit_manager().recruits.get(
                getattr(member, "recruit_id", None))
            if recruit is not None and recruit.has_home():
                warning = (f"Dismiss {member.name}? They'll wait in "
                           f"{recruit.home_town} - gear and level kept.")
            else:
                warning = f"Dismiss {member.name}?"
            self.renderer.draw_text(screen, warning,
                                    (col_x, start_y - 26), font_size=14,
                                    color=COLOR_RED)
