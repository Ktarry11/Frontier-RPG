"""
The banter panel - portraits and a line, bottom-left of the overworld.

Kyle, 2026-10-28: "We have character portraits so it'll be fine."

DESIGN CONSTRAINT: THIS MUST BE IGNORABLE. Banter is ambience. It appears while the player is walking,
it never takes input, it never pauses anything, and it fades on its own. The moment it needs
acknowledging it stops being flavour and becomes an interruption, which is how a feature that was
supposed to make companions feel alive ends up being the thing people turn off first.

So: bottom-left, out of the way of the minimap and the action bar, small portrait, one or two lines, no
buttons. The reply appears a couple of seconds after the opener so it reads as an answer rather than
as two people talking at once.
"""
import pygame

from config import SCREEN_HEIGHT
from ui.recruit_portrait import get_recruit_face

PANEL_X = 16
PANEL_BOTTOM = SCREEN_HEIGHT - 16
FACE = 52
ROW_H = 62
WIDTH = 560
PAD = 10


class BanterPanel:
    def __init__(self, renderer):
        self.renderer = renderer

    def render(self, screen, beat):
        if beat is None:
            return
        rows = beat.lines[:beat.revealed]
        if not rows:
            return

        h = PAD * 2 + ROW_H * len(rows)
        panel = pygame.Rect(PANEL_X, PANEL_BOTTOM - h, WIDTH, h)

        # Fade out over the last second so it leaves rather than vanishes.
        alpha = 255 if beat.remaining > 1.0 else max(0, int(255 * beat.remaining))
        surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        surf.fill((18, 18, 24, int(214 * alpha / 255)))
        pygame.draw.rect(surf, (90, 90, 110, alpha), surf.get_rect(), 1)
        screen.blit(surf, panel.topleft)

        y = panel.y + PAD
        for recruit_id, name, text in rows:
            face = get_recruit_face(recruit_id, FACE)
            if face is not None:
                screen.blit(face, (panel.x + PAD, y))
            else:
                pygame.draw.rect(screen, (46, 46, 58),
                                 pygame.Rect(panel.x + PAD, y, FACE, FACE))
            tx = panel.x + PAD + FACE + 10
            self.renderer.draw_text(screen, name, (tx, y), font_size=14, color=(214, 186, 110))
            self._wrap(screen, text, tx, y + 20, panel.right - tx - PAD)
            y += ROW_H

    def _wrap(self, screen, text, x, y, max_width, font_size=15, line_height=19):
        """Measured and drawn with the same font - the mistake party_screen and background_screen both
        had to be fixed for, where measuring against one font and drawing with another ran text off
        the panel."""
        font = self.renderer._get_font(font_size=font_size)
        line = ""
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] > max_width and line:
                self.renderer.draw_text(screen, line, (x, y), font_size=font_size,
                                        color=(222, 222, 230))
                y += line_height
                line = word
            else:
                line = candidate
        if line:
            self.renderer.draw_text(screen, line, (x, y), font_size=font_size,
                                    color=(222, 222, 230))
