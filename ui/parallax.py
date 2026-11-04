"""
Layered parallax backdrop for the title screen.

Kyle, 4 Nov 2026: "The title screen shows the Valley of Trials from a beautiful
cinematic angle. The player clicks New Game. The camera slowly moves toward the
valley, the logo fades away, and the camera transitions into the actual gameplay
camera." Reference: Octopath Traveler 2's title screen.

Eight hand-generated layers in assets/backgrounds/title/, drifted laterally at
different rates while idle, then dollied forward when New Game is pressed.

=== WHY THE DEPTH READS, AND WHAT WOULD KILL IT ===

The illusion is carried by the SPREAD of the rates, not by any single number.
Near layers drift and grow several times faster than far ones; that difference
IS the depth. Compressing the spread - say by capping the foreground scale to
keep it sharp - flattens the whole image into sliding stickers no matter how
good the art is.

The art itself does the other half, and Kyle's layers do it properly: the far
mesas are hazy and low contrast, the valley carries all the readable detail,
and the two nearest layers are near-black silhouettes.

=== THE KEYING IS NOT UNIFORM, AND THAT IS FINE ===

The eight layers arrived three different ways and the loader handles all of
them rather than demanding they be re-exported:

  - 1_sky is RGB and OPAQUE by design. It is the base; keying it would punch
    holes in the sunset.
  - 3_far_mesas, 6_near_outcrops, 7_fg_lip already carry a real alpha channel.
    Used as-is. Re-keying these would be actively harmful: their soft edges are
    already anti-aliased into alpha.
  - 2_clouds, 4_mid_walls, 5_valley, 8_dust are RGB on magenta.

The magenta is NOT pure #FF00FF - it measures around (251, 3, 251) and varies
per file, because it has been through a generator and a re-encode. An exact
colorkey match would have removed almost nothing and left a magenta screen. The
key is therefore a DISTANCE threshold with a soft band, which also feathers the
anti-aliased edge pixels instead of leaving a hard magenta fringe around every
cloud.
"""
import os

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT

TITLE_DIR = os.path.join("assets", "backgrounds", "title")

#: (filename, drift rate, push-in scale at full push).
#:
#: Drift is in screen-widths per MINUTE, so the whole scene breathes rather than
#: visibly slides - the sky is pinned and only the nearest rock really moves.
#: Scale is where that layer ends up when the dolly completes.
#:
#: Tuned against Kyle's real art rather than guessed: the published starting
#: table had the foreground at 4.0, which at this art's 1672x941 pulled the
#: bottom silhouette apart into mush long before the push finished. 2.9 keeps
#: it reading as rock while still outrunning everything behind it.
#: Entries are (filename, drift_x, drift_y, push_scale).
#:
#: === WIND IS NOT PARALLAX, AND THE CLOUDS PROVE IT ===
#:
#: Kyle, 4 Nov 2026: "we need to ensure that the embers and dust move as do the
#: clouds for that true octopath parallax."
#:
#: Strict parallax says a far layer must drift SLOWER than a near one, and on
#: that rule the clouds - the second-farthest thing in the picture - would
#: creep at a fiftieth of the foreground and read as painted on. Octopath's
#: sky visibly moves, and it is right to: clouds and embers have their OWN
#: motion. Wind does not care how far away it is.
#:
#: So these two deliberately break the depth ordering, and they are the only
#: two that may. Everything made of rock still obeys it strictly, which is
#: what keeps the depth honest - the eye reads the stone as a solid world and
#: the sky as weather moving through it.
#:
#: Dust also rises: they are embers off the camp fire, and embers that track
#: sideways like snow look wrong immediately. drift_y is POSITIVE for rising,
#: because the offset is SUBTRACTED from y - the intuitive negative-is-up sign
#: makes them fall, and worse, Python's modulo on a negative start makes the
#: layer jump a full height on the first frame before drifting the wrong way.
#: The fifth field is HAZE - how far this layer is blended toward the colour
#: of the sky at the horizon. See _apply_haze.
LAYERS = (
    ("1_sky.png",           0.00,  0.00, 1.00, 0.00),
    ("2_clouds.png",        0.45,  0.00, 1.06, 0.00),
    ("3_far_mesas.png",     0.05,  0.00, 1.12, 0.70),
    ("4_mid_walls.png",     0.15,  0.00, 1.38, 0.14),
    ("5_valley.png",        0.25,  0.00, 1.72, 0.00),
    ("6_near_outcrops.png", 0.55,  0.00, 2.30, 0.00),
    ("7_fg_lip.png",        1.00,  0.00, 2.90, 0.00),
    ("8_dust.png",          0.60,  0.22, 1.50, 0.00),
)

#: How far a pixel can sit from the sampled magenta and still be cut. Below
#: INNER it is fully transparent, above OUTER fully opaque, and the band between
#: is the feather that keeps edges from showing a magenta rim.
_KEY_INNER = 70.0
_KEY_OUTER = 140.0

#: Layers are loaded wider than the screen so lateral drift never exposes an
#: edge. 1.18 is enough for the fastest layer over a long idle, since drift
#: wraps rather than running away.
_OVERSCAN = 1.18

#: Where the horizon sits in every layer, as a fraction of frame height. The
#: art prompt specified 58% and every layer was generated to it, which is what
#: lets the whole stack share one vanishing point. If layers are ever
#: regenerated to a different horizon, this is the one number to change.
HORIZON_FRACTION = 0.58

#: How much darker than the sky the haze colour is. Keeps distant land
#: separated in VALUE from the sky it hazes into - see _sky_horizon_color.
_HAZE_VALUE = 0.50


def _looks_like_magenta_backed(surface):
    """True when this layer's background is magenta rather than real alpha.

    Measured as the FRACTION of the image that is magenta, not by sampling the
    corners. The corner version of this failed on the valley layer and failed
    silently: its top corners are sky-magenta but its bottom two are solid
    rock, so a "3 of 4 corners" rule scored 2 and declared the layer already
    keyed. It was then blitted opaque over the sunset and the title screen
    rendered with a flat magenta sky - the art looked broken when the keying
    code was in fact perfect.

    The fraction test has no such edge: a keyed layer is at minimum a third
    magenta by area, while the sky (opaque, no magenta) and the three layers
    that already carry alpha score essentially zero. Nothing sits near 5%.
    """
    try:
        import numpy as np
    except ImportError:
        w, h = surface.get_size()
        pts = [(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2),
               (w // 2, 1), (w // 2, h - 2), (1, h // 2), (w - 2, h // 2)]
        hits = sum(1 for p in pts
                   for c in (surface.get_at(p),)
                   if c.r > 180 and c.b > 180 and c.g < 90)
        return hits >= 2

    rgb = pygame.surfarray.pixels3d(surface)
    mask = (rgb[:, :, 0] > 180) & (rgb[:, :, 2] > 180) & (rgb[:, :, 1] < 90)
    fraction = float(mask.mean())
    del rgb
    return fraction > 0.05


def _key_magenta(surface):
    """Replace a magenta background with alpha, feathering the edge.

    Uses a distance threshold, not an exact colorkey: the magenta in these
    files measures ~(251, 3, 251) and differs between them, so
    set_colorkey((255, 0, 255)) matches almost no pixels and leaves the layer
    opaque. That failure is silent and looks like "the parallax is broken".
    """
    surface = surface.convert_alpha()
    w, h = surface.get_size()

    # Sample the actual background colour rather than assuming pure magenta.
    bg = surface.get_at((1, 1))
    br, bg_g, bb = float(bg.r), float(bg.g), float(bg.b)

    try:
        import numpy as np
    except ImportError:
        # No numpy: fall back to a hard colorkey on the sampled colour. Coarser
        # (visible fringe on soft edges) but never a blocker.
        #
        # Set on a plain convert()ed surface and NOT followed by
        # convert_alpha(): converting to a per-pixel-alpha format after
        # setting a colorkey throws the colorkey away, which would have made
        # this fallback a silent no-op - the exact failure mode the detector
        # above already produced once.
        plain = surface.convert()
        plain.set_colorkey((bg.r, bg.g, bg.b))
        return plain

    rgb = pygame.surfarray.pixels3d(surface).astype(np.float32)
    alpha = pygame.surfarray.pixels_alpha(surface)

    dist = np.sqrt((rgb[:, :, 0] - br) ** 2
                   + (rgb[:, :, 1] - bg_g) ** 2
                   + (rgb[:, :, 2] - bb) ** 2)
    ramp = np.clip((dist - _KEY_INNER) / (_KEY_OUTER - _KEY_INNER), 0.0, 1.0)
    alpha[:, :] = (ramp * 255).astype(np.uint8)

    del rgb, alpha  # release the surface locks surfarray holds
    return surface


def _clamp_faint_alpha(surface, floor=10):
    """Zero out alpha so low it is noise rather than art.

    3_far_mesas carries alpha across rows 281-811 even though its visible band
    is only 450-596: the rows either side hold values of 1-8 out of 255. On
    their own those are invisible. After _apply_haze tints them bright sunset
    orange at 62% they become a faintly brighter RECTANGLE hanging in the sky,
    the exact width of the layer - subtle, but once seen, obviously a pasted
    box rather than weather.

    Worth doing before the haze rather than after, so the tint never gets the
    chance to amplify something that was meant to be nothing.
    """
    try:
        import numpy as np
    except ImportError:
        return surface
    surface = surface.convert_alpha()
    alpha = pygame.surfarray.pixels_alpha(surface)
    alpha[alpha < floor] = 0
    del alpha
    return surface


def _soften_hard_bottom_edge(surface, fade=90):
    """Fade out a layer that ends in a full-width guillotine cut.

    Kyle, 4 Nov 2026: "The background is weird and off for the background
    mesa."

    3_far_mesas is a band from row 450 to row 596 that goes from 1672/1672
    pixels opaque to 0 in a SINGLE row. That edge sits 51px below the horizon,
    where it is meant to be hidden behind the valley - and it is, exactly
    until the camera moves. Then it slides out as a ruler-straight line across
    the whole picture, which is the "weird and off" look: the eye reads a
    horizontal seam, not a mesa.

    Feathering the last `fade` rows turns the seam into haze, which is also
    what distance actually does to the base of a far-off landform. Done at
    LOAD rather than by editing the PNG, so Kyle's source art stays exactly as
    generated and a regenerated layer gets the same treatment for free.

    Applies only to a genuine hard cut: a layer that already fades out, or one
    whose content runs to the bottom of the frame, is left alone.
    """
    try:
        import numpy as np
    except ImportError:
        return surface

    surface = surface.convert_alpha()
    alpha = pygame.surfarray.pixels_alpha(surface)
    w, h = surface.get_size()

    opaque_per_row = (alpha > 8).sum(axis=0)          # surfarray is [x][y]
    rows = np.where(opaque_per_row > 0)[0]
    if rows.size == 0:
        del alpha
        return surface

    last = int(rows.max())
    # A hard cut: the final row is nearly full width, and there is real frame
    # left below it for the seam to be revealed into.
    if opaque_per_row[last] < w * 0.9 or last >= h - 4:
        del alpha
        return surface

    start = max(0, last - fade)
    ramp = np.linspace(1.0, 0.0, last - start + 1)
    alpha[:, start:last + 1] = (alpha[:, start:last + 1] * ramp).astype(np.uint8)
    del alpha
    return surface


def _sky_horizon_color(path):
    """The colour of the air at the horizon, sampled from the sky layer.

    Sampled rather than hard-coded so that regenerating the sky - a different
    time of day, a different palette - automatically re-tints everything that
    hazes into it. A constant here would quietly become wrong.
    """
    fallback = (225, 89, 31)
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return fallback
    try:
        sky = np.asarray(Image.open(path).convert("RGB"), dtype="float32")
    except Exception:  # noqa: BLE001 - any unreadable sky falls back
        return fallback
    h = sky.shape[0]
    band = sky[int(h * (HORIZON_FRACTION - 0.04)):int(h * (HORIZON_FRACTION + 0.04))]
    if band.size == 0:
        return fallback
    mean = band.reshape(-1, 3).mean(axis=0)
    # DARKENED, not the sky colour itself. Hazing straight toward the sky
    # erased the far mesas: blended 62% toward (225, 89, 31) they landed at
    # roughly (209, 93, 72), near enough to the sky that they stopped reading
    # as land and became translucent ghosts hanging over the horizon - which
    # is the "weirdly hazy" Kyle was still seeing after the first fix.
    #
    # A backlit ridge at sunset is warmer than the sky AND darker than it. The
    # hue has to agree or it looks pasted; the VALUE has to differ or it
    # disappears. Only the first was handled.
    return tuple(float(v) * _HAZE_VALUE for v in mean)


def _apply_haze(surface, color, strength):
    """Blend a layer toward the colour of the air in front of it.

    Kyle, 4 Nov 2026: "The background is still weirdly hazy bro. See how it's
    not blended and the background is blueish."

    He is right, and it is a flaw in the art that is cheaper to correct here
    than to regenerate. Measured, the far mesas average (184, 100, 139) against
    a horizon sky of (225, 89, 31) - FOUR TIMES the blue of the air they are
    meant to be sitting in. The generator reached for the textbook aerial
    perspective, which blue-shifts distance because the daytime sky is blue.
    Under a red sunset that is exactly backwards: distant land takes the colour
    of whatever is between you and it, and here that is hot orange.

    A purple ridge against an orange sky does not read as "far away", it reads
    as a different picture pasted in - which is precisely what Kyle saw.

    Blending toward the sampled sky colour is real aerial perspective rather
    than a colour grade, so it also does the job the haze was meant to do:
    the far mesas lose contrast and sink back, and the depth improves rather
    than merely the colour matching.
    """
    if strength <= 0.0:
        return surface
    try:
        import numpy as np
    except ImportError:
        return surface

    surface = surface.convert_alpha()
    rgb = pygame.surfarray.pixels3d(surface)
    target = np.array(color, dtype="float32").reshape(1, 1, 3)
    blended = rgb.astype("float32") * (1.0 - strength) + target * strength
    rgb[:, :, :] = np.clip(blended, 0, 255).astype("uint8")
    del rgb
    return surface


class ParallaxBackdrop:
    """The eight-layer Valley of Trials vista, drifting and dollying.

    Degrades rather than failing: any layer whose file is absent is simply
    skipped, so the art could land one piece at a time and the screen stayed
    usable throughout. With no layers at all, draw() paints a flat sunset and
    the menu still works.
    """

    def __init__(self, root=None):
        self.root = root or TITLE_DIR
        self.layers = []          # [(surface, drift, target_scale), ...]
        self.elapsed = 0.0
        self.push = 0.0           # 0 = idle vista, 1 = fully dollied in
        self.pushing = False
        self.push_seconds = 3.2
        self._scaled_cache = {}
        self._load()

    def _load(self):
        base_h = int(SCREEN_HEIGHT * _OVERSCAN)
        haze_color = _sky_horizon_color(os.path.join(self.root, LAYERS[0][0]))
        for filename, drift_x, drift_y, scale, haze in LAYERS:
            path = os.path.join(self.root, filename)
            if not os.path.exists(path):
                continue
            try:
                raw = pygame.image.load(path)
            except pygame.error:
                continue

            if _looks_like_magenta_backed(raw.convert_alpha()):
                surf = _key_magenta(raw)
            else:
                surf = raw.convert_alpha()
            surf = _clamp_faint_alpha(surf)
            surf = _soften_hard_bottom_edge(surf)
            surf = _apply_haze(surf, haze_color, haze)

            # Scale to a common height so every layer shares one horizon.
            w, h = surf.get_size()
            target_w = max(1, int(w * (base_h / float(h))))
            surf = pygame.transform.smoothscale(surf, (target_w, base_h))
            self.layers.append([surf, drift_x, drift_y, scale])

    @property
    def loaded(self):
        return bool(self.layers)

    def start_push_in(self):
        """Begin the dolly. Harmless to call twice."""
        self.pushing = True

    def reset(self):
        self.pushing = False
        self.push = 0.0

    @property
    def push_complete(self):
        return self.push >= 1.0

    def update(self, dt):
        self.elapsed += dt
        if self.pushing and self.push < 1.0:
            self.push = min(1.0, self.push + dt / self.push_seconds)

    def _eased(self):
        """Ease-in cubic.

        A linear dolly reads as a machine moving the camera. Starting slow and
        accelerating reads as a camera being PUSHED, and it also buys the logo
        time to fade before the motion gets fast enough to smear it.
        """
        p = self.push
        return p * p * p

    def draw(self, screen):
        if not self.layers:
            screen.fill((42, 22, 48))
            return

        eased = self._eased()
        # SCALE ABOUT THE HORIZON, NOT THE SCREEN CENTRE.
        #
        # Every layer was painted with its horizon 58% down the frame, so the
        # horizon is the scene's vanishing point and a real dolly leaves it
        # fixed. Scaling about the centre instead moved each layer's horizon by
        # a different amount - the valley's skyline sank faster than the far
        # mesas', which pulled them apart and exposed the hard bottom edge of
        # the mesa layer as a straight line across the picture partway into the
        # push. Invisible while idle, obvious the moment the camera moved.
        cx = SCREEN_WIDTH * 0.5
        focal_y = SCREEN_HEIGHT * HORIZON_FRACTION

        for surf, drift_x, drift_y, target_scale in self.layers:
            scale = 1.0 + (target_scale - 1.0) * eased
            w, h = surf.get_size()

            if scale > 1.001:
                # transform.scale, not smoothscale: this runs every frame for
                # eight layers during the push, and the motion hides the
                # difference entirely. smoothscale here costs ~4x for no
                # visible gain while the camera is moving.
                sw, sh = int(w * scale), int(h * scale)
                frame = pygame.transform.scale(surf, (sw, sh))
            else:
                frame, sw, sh = surf, w, h

            # Drift, in screen-widths (or heights) per minute, wrapped so the
            # loop is seamless. Frozen once the push starts - the camera is
            # moving forward now, and a continuing sideways slide reads as a
            # wobble rather than as wind.
            if self.pushing:
                off_x = off_y = 0.0
            else:
                off_x = (self.elapsed * drift_x * SCREEN_WIDTH / 60.0) % max(1, sw)
                off_y = (self.elapsed * drift_y * SCREEN_HEIGHT / 60.0) % max(1, sh)

            x = cx - sw * 0.5 - off_x
            y = focal_y - sh * HORIZON_FRACTION - off_y

            # Tile in whichever directions are actually drifting. The vertical
            # copy only exists for the embers; every other layer leaves off_y
            # at 0 and pays nothing for it.
            screen.blit(frame, (x, y))
            wrap_x = off_x > 0 and x + sw < SCREEN_WIDTH
            wrap_y = off_y > 0 and y + sh < SCREEN_HEIGHT
            if wrap_x:
                screen.blit(frame, (x + sw, y))
            if wrap_y:
                screen.blit(frame, (x, y + sh))
            if wrap_x and wrap_y:
                screen.blit(frame, (x + sw, y + sh))

    def draw_bloom(self, screen):
        """The warm white-out that hands off to gameplay.

        The title is a side-on vista and the game camera is top-down - two
        different projections of the same valley, with no continuous move
        between them. A straight crossfade reads as a bug. Blooming to warm
        white at the end of the push and opening on the top-down view reads as
        the same camera continuing, which is what Octopath does at this exact
        moment.

        Starts at 70% through the push so the white arrives while the camera is
        still accelerating, never after it has stopped.
        """
        if self.push <= 0.7:
            return
        t = (self.push - 0.7) / 0.3
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((255, 240, 214, int(min(1.0, t) * 255)))
        screen.blit(veil, (0, 0))

    def logo_alpha(self):
        """Logo opacity: full while idle, gone by a third of the way in.

        Kyle: "the camera slowly moves toward the valley, the logo fades away".
        It clears early on purpose - a title still hanging over a moving camera
        is the thing that makes an intro feel like a menu.
        """
        if not self.pushing:
            return 255
        return int(max(0.0, 1.0 - self.push / 0.33) * 255)
