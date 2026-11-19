"""
The banter panel - portraits and a line, bottom-left of the overworld.

Kyle, 2026-10-28: "We have character portraits so it'll be fine."

DESIGN CONSTRAINT: THIS MUST BE IGNORABLE. Banter is ambience. It appears while the player is walking,
it never takes input, it never pauses anything, and it fades on its own. The moment it needs
acknowledging it stops being flavour and becomes an interruption, which is how a feature that was
supposed to make companions feel alive ends up being the thing people turn off first.

So: bottom-left, out of the way of the minimap and the action bar, small portrait, a few lines, no
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
LINE_H = 19
TEXT_SIZE = 15
MAX_ROWS = 3


class BanterPanel:
    def __init__(self, renderer):
        self.renderer = renderer

    def render(self, screen, beat):
        if beat is None:
            return
        rows = beat.lines[:beat.revealed]
        if not rows:
            return
        # a long conversation rolls: the newest lines stay, the oldest scroll away, so the panel
        # never grows to cover half the screen
        rows = rows[-MAX_ROWS:]
        tx_off = PAD + FACE + 10
        wrapped = [self._lines(text, WIDTH - tx_off - PAD) for _, _, text in rows]
        heights = [max(ROW_H, 20 + LINE_H * len(w) + 6) for w in wrapped]

        h = PAD * 2 + sum(heights)
        panel = pygame.Rect(PANEL_X, PANEL_BOTTOM - h, WIDTH, h)

        # Fade out over the last second so it leaves rather than vanishes.
        alpha = 255 if beat.remaining > 1.0 else max(0, int(255 * beat.remaining))
        surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        surf.fill((18, 18, 24, int(214 * alpha / 255)))
        pygame.draw.rect(surf, (90, 90, 110, alpha), surf.get_rect(), 1)
        screen.blit(surf, panel.topleft)

        y = panel.y + PAD
        for (recruit_id, name, text), lines, rh in zip(rows, wrapped, heights):
            face = get_recruit_face(recruit_id, FACE)
            if face is not None:
                screen.blit(face, (panel.x + PAD, y))
            else:
                pygame.draw.rect(screen, (46, 46, 58),
                                 pygame.Rect(panel.x + PAD, y, FACE, FACE))
            tx = panel.x + tx_off
            self.renderer.draw_text(screen, name, (tx, y), font_size=14, color=(214, 186, 110))
            for i, line in enumerate(lines):
                self.renderer.draw_text(screen, line, (tx, y + 20 + i * LINE_H), font_size=TEXT_SIZE,
                                        color=(222, 222, 230))
            y += rh

    def _lines(self, text, max_width, font_size=TEXT_SIZE):
        """The text broken to fit, measured with the same font it's drawn in - the mistake
        party_screen and background_screen both had to be fixed for, where measuring against one
        font and drawing with another ran text off the panel. Measuring first also gives each row
        its real height, so a three-line speech doesn't run into the row below it."""
        font = self.renderer._get_font(font_size=font_size)
        out, line = [], ""
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] > max_width and line:
                out.append(line)
                line = word
            else:
                line = candidate
        if line:
            out.append(line)
        return out
