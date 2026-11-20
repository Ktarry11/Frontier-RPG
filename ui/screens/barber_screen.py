"""The barber's chair: pick a new face when the old one is gone.

Kyle, 20 Nov 2026, on replacing the player sprites: "lets make a barber choice if the sprite is gone". A save keeps its
look as a place in its race and gender's list (world/race_registry.py), so if those pictures are deleted, or the list is
cut so the place no longer exists, the character would load wearing somebody else's face or a stand-in. The menu sends
them here first (ui/screens/menu_screen.py), and they choose from the looks their race and gender can pick now. The
race, the gender and everything else stay as they are; only the face changes.

Shown the four ways a look turns (front, left, right, back). Left and right arrows (or the buttons) go through the
looks; Enter or "Choose this look" keeps it. When the chair isn't forced (the Testing menu opens it), Escape leaves
without changing anything.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen

FACINGS = ("down", "left", "right", "up")


class BarberScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.return_state = GameState.OVERWORLD
        self.forced = False
        self.looks = []             # places in the race and gender's list that can be picked
        self.pick = 0               # index into self.looks
        self.hits = []
        self.message = ""

    # ------------------------------------------------------------ the rule
    @staticmethod
    def needed(player):
        """True if this character's look is gone and there's another one to pick."""
        if player is None:
            return False
        from world.race_registry import look_is_missing, pickable_looks
        race, gender = getattr(player, "race", None), getattr(player, "gender", None)
        return (look_is_missing(race, gender, getattr(player, "appearance_variant", 0))
                and bool(pickable_looks(race, gender)))

    def start(self, return_state=GameState.OVERWORLD, forced=False):
        from world.race_registry import pickable_looks
        p = self.state_manager.player
        self.return_state, self.forced, self.message = return_state, forced, ""
        self.looks = pickable_looks(getattr(p, "race", None), getattr(p, "gender", None))
        cur = getattr(p, "appearance_variant", 0)
        self.pick = self.looks.index(cur) if cur in self.looks else 0

    def choose(self):
        p = self.state_manager.player
        if p is not None and self.looks:
            p.appearance_variant = self.looks[self.pick]
        self.state_manager.transition_to(self.return_state)
        ow = self.state_manager.states.get(GameState.OVERWORLD)
        if ow is not None and hasattr(ow, "_notify"):
            ow._notify("A new look. Save the game to keep it.", (200, 190, 150))

    def step(self, d):
        if self.looks:
            self.pick = (self.pick + d) % len(self.looks)

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.step(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.step(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.choose()
            elif event.key == pygame.K_ESCAPE and not self.forced:
                self.state_manager.transition_to(self.return_state)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 1) == 1:
            for rect, action in list(self.hits):
                if rect.collidepoint(event.pos):
                    action()
                    return

    def update(self, dt):
        pass

    # ------------------------------------------------------------ drawing
    def render(self, screen):
        from ui.sprite_loader import get_npc_sprite
        from world.race_registry import sprite_base_path, get_race
        screen.fill((18, 15, 22))
        self.hits = []
        p = self.state_manager.player
        race_id, gender_id = getattr(p, "race", None), getattr(p, "gender", None)
        race = get_race(race_id)
        self.renderer.draw_text(screen, "THE BARBER'S CHAIR", (SCREEN_WIDTH // 2 - 150, 30), size="large", color=COLOR_GOLD)
        why = ("The look this character wore isn't in the game any more. Pick a new face; everything else stays as "
               "it is." if self.forced else "Pick a new face. Everything else stays as it is.")
        for i, line in enumerate(self.renderer.wrap_text(why, SCREEN_WIDTH - 200)[:2]):
            self.renderer.draw_text(screen, line, (100, 82 + i * 22), color=(190, 185, 200))
        if not self.looks:
            self.renderer.draw_text(screen, "There are no looks to pick for this race.", (100, 160), color=(230, 150, 130))
            return
        base = sprite_base_path(race_id, gender_id, self.looks[self.pick])
        th = int(SCREEN_HEIGHT * 0.36)
        gap = SCREEN_WIDTH // 5
        for i, f in enumerate(FACINGS):
            spr = get_npc_sprite(base, f, tile_height=th) if base else None
            cx = gap * (i + 1)
            if spr is not None:
                screen.blit(spr, spr.get_rect(midbottom=(cx, 150 + th + 20)))
            self.renderer.draw_text(screen, {"down": "Front", "up": "Back"}.get(f, f.title()), (cx - 24, 150 + th + 30),
                                    color=(150, 145, 165))
        label = f"{race.label if race else race_id} {gender_id or ''}: look {self.pick + 1} of {len(self.looks)}".strip()
        self.renderer.draw_text(screen, label, (SCREEN_WIDTH // 2 - 140, 150 + th + 70), color=(220, 215, 230))
        y = SCREEN_HEIGHT - 110
        left = pygame.Rect(SCREEN_WIDTH // 2 - 330, y, 140, 50)
        ok = pygame.Rect(SCREEN_WIDTH // 2 - 170, y, 340, 50)
        right = pygame.Rect(SCREEN_WIDTH // 2 + 190, y, 140, 50)
        for rect, text, act, col in ((left, "< Previous", lambda: self.step(-1), (50, 46, 66)),
                                     (ok, "Choose this look", self.choose, (60, 100, 70)),
                                     (right, "Next >", lambda: self.step(1), (50, 46, 66))):
            self.renderer.draw_button(screen, rect, text, color=col)
            self.hits.append((rect, act))
        if not self.forced:
            self.renderer.draw_text(screen, "Escape leaves without changing anything.", (SCREEN_WIDTH // 2 - 160, y + 62),
                                    color=(140, 135, 150))
