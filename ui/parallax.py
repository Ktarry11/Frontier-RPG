"""
Static Valley of Trials title backdrop, with drifting embers.

Kyle, 5 Nov 2026, after seeing the moving version in the real game: "the title
screen is broken as the parallax is messed up... Let's do it stationary of the
VoT with only the embers moving... no zoom in with white flash on new game
either... once again, stationary, remove the blue mountains."

WHAT WAS HERE BEFORE AND WHY IT IS GONE
---------------------------------------
This module previously drifted all eight layers at different rates and dollied
them forward on New Game. It rendered correctly in stills and was fragmented in
motion - layers at different scales and offsets pull apart at their seams, and
the art was never cut for that: the layers are single paintings with hard
boundaries, not tiling plates with generous overlap.

The honest read is that selling a moving parallax needs art authored for it,
and grinding code against art that was not is how the last session went. A
still frame of a good painting with live embers over it looks better than a
moving one that comes apart, and it is a fraction of the work.

So: every layer is pinned. Only the embers move. No push-in, no bloom.

3_far_mesas is not loaded at all - those are Kyle's "blue mountains", painted
with a daytime blue-shift that never sat right under a red sunset. The cool
formations inside 4_mid_walls go the same way, cut by hue rather than by hand.
"""
import os

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT

TITLE_DIR = os.path.join("assets", "backgrounds", "title")

#: (filename, ember drift x, ember drift y). Everything is pinned except the
#: dust, in screen-widths (or heights) per minute.
#:
#: 3_far_mesas is deliberately absent - see the module docstring.
LAYERS = (
    ("1_sky.png",           0.00,  0.00),
    ("2_clouds.png",        0.00,  0.00),
    ("4_mid_walls.png",     0.00,  0.00),
    ("5_valley.png",        0.00,  0.00),
    ("6_near_outcrops.png", 0.00,  0.00),
    ("7_fg_lip.png",        0.00,  0.00),
    ("8_dust.png",          0.25,  0.10),
)

#: Layers whose cool/lavender pixels are cut out rather than kept. Same
#: objection as the far mesas: wrong hue for this sky, and tinting them warm
#: only ever reached muddy.
CUT_COOL = {"4_mid_walls.png"}

_KEY_INNER = 70.0
_KEY_OUTER = 140.0


def _is_magenta_backed(surface):
    """True when the background is magenta rather than real alpha.

    Measured as a FRACTION of the image. Sampling corners instead got this
    wrong on the valley layer, whose bottom corners are solid rock: it scored
    2 of 4, was declared already-keyed, and blitted opaque over the sunset.
    """
    try:
        import numpy as np
    except ImportError:
        c = surface.get_at((1, 1))
        return c.r > 180 and c.b > 180 and c.g < 90
    rgb = pygame.surfarray.pixels3d(surface)
    mask = (rgb[:, :, 0] > 180) & (rgb[:, :, 2] > 180) & (rgb[:, :, 1] < 90)
    frac = float(mask.mean())
    del rgb
    return frac > 0.05


def _key_magenta(surface):
    """Replace a magenta background with alpha, feathering the edge.

    A distance threshold, not an exact colorkey: the magenta in these files
    measures ~(251, 3, 251) and differs between them, so matching (255, 0, 255)
    exactly removes almost nothing and leaves the layer opaque.
    """
    surface = surface.convert_alpha()
    bg = surface.get_at((1, 1))
    try:
        import numpy as np
    except ImportError:
        plain = surface.convert()
        plain.set_colorkey((bg.r, bg.g, bg.b))
        return plain

    rgb = pygame.surfarray.pixels3d(surface).astype("float32")
    alpha = pygame.surfarray.pixels_alpha(surface)
    dist = np.sqrt((rgb[:, :, 0] - bg.r) ** 2
                   + (rgb[:, :, 1] - bg.g) ** 2
                   + (rgb[:, :, 2] - bg.b) ** 2)
    ramp = np.clip((dist - _KEY_INNER) / (_KEY_OUTER - _KEY_INNER), 0.0, 1.0)
    alpha[:, :] = (ramp * 255).astype("uint8")
    del rgb, alpha
    return surface


def _clamp_faint_alpha(surface, floor=10):
    """Zero alpha too low to be art - it only ever shows up as a faint box."""
    try:
        import numpy as np
    except ImportError:
        return surface
    surface = surface.convert_alpha()
    alpha = pygame.surfarray.pixels_alpha(surface)
    alpha[alpha < floor] = 0
    del alpha
    return surface


def _cut_cool_pixels(surface, threshold=0.55):
    """Delete lavender pixels instead of trying to warm them.

    4_mid_walls holds both the warm canyon walls that frame the shot and a set
    of cool formations in the gap between them - measured, 12.3% of its rock
    at (177, 72, 120) against warm rock at (184, 63, 56). Tinting could not
    fix that: pushed hard enough to kill the purple it went muddy, because the
    colour is in the paint.

    They sit against open sky, so removing them costs nothing structurally.
    Keyed on blue relative to red, so warm rock scores zero and survives.
    """
    try:
        import numpy as np
    except ImportError:
        return surface
    surface = surface.convert_alpha()
    rgb = pygame.surfarray.pixels3d(surface).astype("float32")
    cool = np.clip((rgb[:, :, 2] - 0.45 * rgb[:, :, 0]) / 80.0, 0.0, 1.0)
    del rgb
    alpha = pygame.surfarray.pixels_alpha(surface)
    keep = np.clip((threshold - cool) / threshold, 0.0, 1.0)
    alpha[:, :] = (alpha * keep).astype("uint8")
    del alpha
    return surface


class ParallaxBackdrop:
    """The Valley of Trials vista: pinned, with drifting embers.

    Name kept so MenuScreen and anything else referring to it keeps working;
    there is no parallax left in it.

    Degrades rather than failing - a missing layer is skipped, and with no
    layers at all draw() paints a flat dusk and the menu still works.
    """

    def __init__(self, root=None):
        self.root = root or TITLE_DIR
        self.layers = []          # [(surface, drift_x, drift_y), ...]
        self.elapsed = 0.0
        self._load()

    def _load(self):
        for filename, dx, dy in LAYERS:
            path = os.path.join(self.root, filename)
            if not os.path.exists(path):
                continue
            try:
                raw = pygame.image.load(path)
            except pygame.error:
                continue

            surf = _key_magenta(raw) if _is_magenta_backed(raw.convert_alpha()) \
                else raw.convert_alpha()
            surf = _clamp_faint_alpha(surf)
            if filename in CUT_COOL:
                surf = _cut_cool_pixels(surf)

            # Everything is pinned now, so each layer is scaled to cover the
            # screen exactly. The old build loaded them oversized to leave room
            # for drift; without drift that margin is just wasted memory and
            # pixels cropped off every edge.
            surf = pygame.transform.smoothscale(surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.layers.append((surf, dx, dy))

    @property
    def loaded(self):
        return bool(self.layers)

    def update(self, dt):
        self.elapsed += dt

    def draw(self, screen):
        if not self.layers:
            screen.fill((42, 22, 48))
            return

        for surf, dx, dy in self.layers:
            if dx == 0.0 and dy == 0.0:
                screen.blit(surf, (0, 0))
                continue

            # Embers: wrapped in both axes so the loop is seamless. Positive
            # drift_y rises, because the offset is subtracted from y.
            ox = (self.elapsed * dx * SCREEN_WIDTH / 60.0) % SCREEN_WIDTH
            oy = (self.elapsed * dy * SCREEN_HEIGHT / 60.0) % SCREEN_HEIGHT
            x, y = -ox, -oy
            screen.blit(surf, (x, y))
            screen.blit(surf, (x + SCREEN_WIDTH, y))
            screen.blit(surf, (x, y + SCREEN_HEIGHT))
            screen.blit(surf, (x + SCREEN_WIDTH, y + SCREEN_HEIGHT))
