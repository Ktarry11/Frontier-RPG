"""The cutscene player (world/cutscenes.py, docs/crown_cutscene.md).

Plays a cutscene's shots one after another: each a painting with a slow pan or push (the part of the painting on screen
eases from a start framing to an end framing), crossfading into the next. A shot can shake, flood with gold-white light
toward its end, or open out of that light. No figure is ever drawn and no words are spoken. Escape, Enter or Space skips
to the end. When it's over the overworld takes back, and the player is wherever the cutscene leaves them.

A REPLAY (the Mural Shard keepsake, or the fallen piece of the mural on the Crown: docs/crown_cutscene.md) is started
with cutscene_replay=True. It plays the same shots and hands you back exactly where you stood: no move, nothing marked.
"""
import math
import random

import pygame

from core.game_states import GameState
from ui.screens.base_screen import BaseScreen

FADE = 0.7          # seconds of crossfade between shots
END_FADE = 0.9      # seconds of fade to black at the end
FLOOD = (255, 244, 214)


def _ease(t):
    return t * t * (3 - 2 * t)


class CutsceneScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.cid = None
        self.shots = []
        self.images = {}
        self.t = 0.0
        self.total = 0.0
        self.done = False
        self.replay = False

    # ------------------------------------------------------------------ setup
    def start(self, cid):
        from world.cutscenes import CUTSCENES
        self.cid = cid
        self.replay = bool(getattr(self.state_manager, "cutscene_replay", False))
        self.shots = list(CUTSCENES[cid]["shots"])
        self.images = {}
        for (path, *_rest) in self.shots:
            if path not in self.images:
                try:
                    self.images[path] = pygame.image.load(path).convert()
                except (pygame.error, FileNotFoundError):
                    self.images[path] = None
        self.t = 0.0
        self.total = sum(s[1] for s in self.shots) + END_FADE
        self.done = False

    # ------------------------------------------------------------------ the loop
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.finish()

    def update(self, dt):
        cid = getattr(self.state_manager, "current_cutscene", None)
        if cid and cid != self.cid:
            self.start(cid)
        if not self.shots:
            self.finish()
            return
        self.t += dt
        if self.t >= self.total:
            self.finish()

    def finish(self):
        if self.done:
            return
        self.done = True
        sm = self.state_manager
        zm = getattr(sm, "zone_manager", None)
        cid, self.cid = self.cid, None
        sm.current_cutscene = None
        replay, self.replay = self.replay, False
        sm.cutscene_replay = False
        if zm is not None and cid and not replay:
            from world.cutscenes import get_cutscenes
            dest = get_cutscenes().destination(cid, getattr(zm, "zones", {}))
            if dest:
                zm.transition_to_zone(*dest)
        sm.transition_to(GameState.OVERWORLD)

    # ------------------------------------------------------------------ drawing
    def _frame(self, screen, idx, local):
        path, secs, a, b, extra = self.shots[idx]
        img = self.images.get(path)
        sw, sh = screen.get_size()
        if img is None:
            screen.fill((0, 0, 0))
            return
        k = _ease(min(1.0, max(0.0, local / secs)))
        x, y, w, h = (a[i] + (b[i] - a[i]) * k for i in range(4))
        iw, ih = img.get_size()
        # keep the screen's shape: widen or narrow the window to match it, centred on the framing
        want = sw / sh
        cw, ch = w * iw, h * ih
        if cw / ch > want:
            cw = ch * want
        else:
            ch = cw / want
        cx = x * iw + w * iw / 2
        cy = y * ih + h * ih / 2
        if extra.get("shake"):
            amp = 6.0 * min(1.0, local / 0.6) * (1.0 - _ease(min(1.0, max(0.0, (local - secs + 1.0)))))
            cx += amp * math.sin(local * 47.0) + random.uniform(-1, 1) * amp * 0.3
            cy += amp * math.cos(local * 39.0)
        rx = max(0, min(iw - cw, cx - cw / 2))
        ry = max(0, min(ih - ch, cy - ch / 2))
        crop = img.subsurface(pygame.Rect(int(rx), int(ry), int(cw), int(ch)))
        screen.blit(pygame.transform.smoothscale(crop, (sw, sh)), (0, 0))
        flood = 0.0
        if "flood_in" in extra:
            flood = max(flood, _ease(min(1.0, max(0.0, (local - (secs - extra["flood_in"])) / extra["flood_in"]))))
        if "flood_out" in extra:
            flood = max(flood, 1.0 - _ease(min(1.0, local / extra["flood_out"])))
        if flood > 0:
            veil = pygame.Surface((sw, sh))
            veil.fill(FLOOD)
            veil.set_alpha(int(255 * flood))
            screen.blit(veil, (0, 0))

    def render(self, screen):
        screen.fill((0, 0, 0))
        if not self.shots:
            return
        t, idx = self.t, 0
        while idx < len(self.shots) - 1 and t >= self.shots[idx][1]:
            t -= self.shots[idx][1]
            idx += 1
        self._frame(screen, idx, t)
        # crossfade into the next shot over its first FADE seconds
        if idx > 0 and t < FADE:
            prev = screen.copy()
            self._frame(prev, idx - 1, self.shots[idx - 1][1])
            prev.set_alpha(int(255 * (1.0 - _ease(t / FADE))))
            self._frame(screen, idx, t)
            screen.blit(prev, (0, 0))
        text = self.shots[idx][4].get("text")
        if text:
            font = pygame.font.Font(None, 34)
            surf = font.render(text, True, (250, 240, 215))
            screen.blit(surf, ((screen.get_width() - surf.get_width()) // 2, screen.get_height() - 70))
        # fade to black at the very end
        end = sum(s[1] for s in self.shots)
        if self.t > end:
            veil = pygame.Surface(screen.get_size())
            veil.fill((0, 0, 0))
            veil.set_alpha(int(255 * min(1.0, (self.t - end) / END_FADE)))
            screen.blit(veil, (0, 0))
